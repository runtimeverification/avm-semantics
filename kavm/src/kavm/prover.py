# type: ignore

import importlib
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Tuple

import hypothesis.strategies as st
import pyteal
import pytest
from algosdk.abi.method import Method
from algosdk.future.transaction import ApplicationCallTxn, AssetTransferTxn, PaymentTxn, SuggestedParams, Transaction
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis.control import assume
from pyk.kast.inner import KApply, KInner, KLabel, KRewrite, KSort, KToken, KVariable, Subst, build_assoc
from pyk.kast.manip import (
    flatten_label,
    inline_cell_maps,
    minimize_term,
    omit_large_tokens,
    push_down_rewrites,
    set_cell,
    split_config_and_constraints,
    split_config_from,
)
from pyk.kast.outer import KClaim, read_kast_definition
from pyk.ktool.kprint import build_symbol_table, paren, pretty_print_kast
from pyk.ktool.kprove import KProve
from pyk.prelude.bytes import bytesToken
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken
from pyk.utils import dequote_str
from pyteal.ir import Op

from kavm.adaptors.algod_transaction import KAVMTransaction, transaction_k_term
from kavm.kast.factory import KAVMTermFactory
from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_address_to_k_bytes, generate_tvalue_list, int_2_bytes, method_selector_to_k_bytes
from kavm.scenario import KAVMScenario

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def last_log_item_eq(int_term: KInner) -> KInner:
    return KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(int_term, BE, Unsigned), 8, 0)
        "_==K_",
        [
            KVariable('?FINAL_LOGDATA_CELL'),
            KApply(
                '_+Bytes_',
                [
                    bytesToken(dequote_str(str(b'\x15\x1f|u')[2:-1])),
                    KApply(
                        'padLeftBytes',
                        [
                            KApply(
                                'Int2Bytes',
                                [
                                    int_term,
                                    KToken('BE', KSort('Endianness')),
                                    KToken('Unsigned', KSort('Signedness')),
                                ],
                            ),
                            intToken(8),
                            intToken(0),
                        ],
                    ),
                ],
            ),
        ],
    )


pyteal_op_to_k_op = {
    Op.eq: '_==Int_',
    Op.neq: '_=/=Int_',
    Op.ge: '_>=Int_',
    Op.gt: '_>Int_',
    Op.le: '_<=Int_',
    Op.lt: '_<Int_',
    Op.div: '_/Int_',
    Op.mul: '_*Int_',
    Op.add: '_+Int_',
    Op.minus: '_-Int_',
}

pyteal_op_to_python_op = {
    Op.eq: '==',
    Op.neq: '!=',
    Op.ge: '>=',
    Op.gt: '>',
    Op.le: '<=',
    Op.lt: '<',
    Op.div: '/',
    Op.mul: '*',
    Op.add: '+',
    Op.minus: '-',
}


def pyteal_expr_to_kast(expr: pyteal.Expr) -> KInner:
    if isinstance(expr, SymbolicInt):
        return KVariable(expr.var_name.upper())
    if isinstance(expr, pyteal.Int):
        return intToken(expr.value)
    if isinstance(expr, pyteal.BinaryExpr) and expr.op in pyteal_op_to_k_op.keys():
        return KApply(
            pyteal_op_to_k_op[expr.op],
            [
                pyteal_expr_to_kast(expr.argLeft),
                pyteal_expr_to_kast(expr.argRight),
            ],
        )
    if isinstance(expr, pyteal.NaryExpr) and len(expr.args) == 2 and expr.op in pyteal_op_to_k_op.keys():
        return KApply(
            pyteal_op_to_k_op[expr.op],
            [
                pyteal_expr_to_kast(expr.args[0]),
                pyteal_expr_to_kast(expr.args[1]),
            ],
        )
    else:
        raise ValueError(f'Unsupported PyTeal expression: {expr} of type {type(expr)}')


def pyteal_expr_to_python_src(expr: pyteal.Expr) -> str:
    if isinstance(expr, SymbolicInt):
        return expr.var_name.upper()
    if isinstance(expr, pyteal.Int):
        # strategy_env[expr.var_name.upper()] = st.just(expr.value)
        return str(expr.value)
    if isinstance(expr, pyteal.BinaryExpr) and expr.op in pyteal_op_to_k_op.keys():
        return f'{pyteal_expr_to_python_src(expr.argLeft)} {pyteal_op_to_python_op[expr.op]} {pyteal_expr_to_python_src(expr.argRight)}'
    if isinstance(expr, pyteal.NaryExpr) and len(expr.args) == 2 and expr.op in pyteal_op_to_k_op.keys():
        return f'{pyteal_expr_to_python_src(expr.args[0])} {pyteal_op_to_python_op[expr.op]} {pyteal_expr_to_python_src(expr.args[1])}'
    else:
        raise ValueError(f'Unsupported PyTeal expression: {expr} of type {type(expr)}')


class SymbolicInt(pyteal.Int):
    """An expression that represents a symbolic uint64."""

    def __init__(self, var_name: str) -> None:
        """Create a new uint64.
        Args:
            value: The integer value this uint64 will represent. Must be a positive value less than
                2**64.
        """
        super().__init__(0)
        self.var_name = var_name

    def amount(self) -> 'SymbolicInt':
        self.var_name = self.var_name + '_amount'
        return self


class HoareMethod(Method):
    def __init__(self, *args, **kwargs) -> None:
        Method.__init__(self, *args, **kwargs)
        self._preconditions = []
        self._python_src_preconditions = []
        self._postconditions = []
        self._python_src_postconditions = []

    @staticmethod
    def from_plain_method(m: Method) -> 'HoareMethod':
        return HoareMethod(name=m.name, args=m.args, returns=m.returns, desc=m.desc)


def router_hoare_method(
    self: pyteal.Router, func: Optional[pyteal.ABIReturnSubroutine] = None
) -> pyteal.ABIReturnSubroutine:
    def wrap(func):
        for idx, m in enumerate(self.methods):
            if m.name == func.method_spec().name:
                self.methods[idx] = HoareMethod.from_plain_method(m)
        return func

    if not func:
        return wrap
    return wrap(func)


def router_precondition(
    self: pyteal.Router,
    func: Optional[pyteal.ABIReturnSubroutine] = None,
    /,
    *,
    expr: pyteal.Expr,
) -> pyteal.ABIReturnSubroutine:
    def wrap(func):
        expr_env = {'Int': pyteal.Int}
        for k, v in func.subroutine.abi_args.items():
            expr_env[k] = v.new_instance()

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                target=pyteal.abi.PaymentTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name='payment'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.AssetTransferTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name='asset_transfer'),
                raising=False,
            )
            spec = eval(expr, expr_env)

        for m in self.methods:
            if m.name == func.method_spec().name and isinstance(m, HoareMethod):
                try:
                    m._preconditions.append(pyteal_expr_to_kast(spec))
                    m._python_src_preconditions.append(pyteal_expr_to_python_src(spec))
                except AttributeError:
                    _LOGGER.error(
                        'Skipping precondition to method "{m.name}" as its not market with @router.hoare_method'
                    )
        return func

    if not func:
        return wrap
    return wrap(func)


def router_postcondition(
    self: pyteal.Router,
    func: Optional[pyteal.ABIReturnSubroutine] = None,
    /,
    *,
    expr: pyteal.Expr,
) -> pyteal.ABIReturnSubroutine:
    def wrap(func):
        expr_env = {'Int': pyteal.Int}
        for k, v in func.subroutine.abi_args.items():
            expr_env[k] = v.new_instance()
        for k, v in func.subroutine.output_kwarg.items():
            expr_env[k] = v.new_instance()

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                target=pyteal.abi.PaymentTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name='payment'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.AssetTransferTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name='asset_transfer'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.Uint,
                name='get',
                value=lambda txn: SymbolicInt(var_name='output'),
                raising=False,
            )
            spec = eval(expr, expr_env)

        for m in self.methods:
            if m.name == func.method_spec().name:
                try:
                    m._postconditions.append(last_log_item_eq(pyteal_expr_to_kast(spec.argRight)))
                    m._python_src_postconditions.append(pyteal_expr_to_python_src(spec.argRight))
                except AttributeError:
                    _LOGGER.error(
                        'Skipping precondition to method "{m.name}" as its not market with @router.hoare_method'
                    )
        return func

    if not func:
        return wrap
    return wrap(func)


def remove_duplicates(labels: List) -> List:
    return [*set(labels)]


class SymbolicApplTxn:
    pass


def preprocess_teal_program(term: KInner) -> Tuple[List[KInner], KInner]:
    labels = []

    def preprocess_teal_program_impl(term: KInner) -> KInner:
        def hex_token_to_k_string(ht: str) -> str:
            string = ""
            for i in range(0, len(ht), 2):
                string += "\\x"
                string += ht[i] + ht[i + 1]
            return string

        if type(term) is KApply:
            if len(term.args) == 0:
                return term
            else:
                result = KApply(label=term.label, args=[preprocess_teal_program_impl(arg) for arg in term.args])
                return result
        else:
            if type(term) is KToken:
                if term.sort == KSort(name="Label"):
                    var = KVariable(str(term.token).upper())
                    labels.append(var)
                    return var
                elif term.sort == KSort(name="HexToken"):
                    return stringToken(dequote_str(hex_token_to_k_string(term.token[2:])))

                else:
                    return term
            else:
                return term

    pgm = preprocess_teal_program_impl(term)

    return labels, pgm


class SymbolicApplication:  # noqa: B903
    def __init__(self, app_id: int, app_cell: KInner, labels: List[KInner]):
        self._app_id = app_id
        self._app_cell = app_cell
        self._labels = labels


class SymbolicAsset:  # noqa: B903
    def __init__(self, asset_id: int, asset_cell: KInner):
        self._asset_id = asset_id
        self._asset_cell = asset_cell


class SymbolicAccount:
    def __init__(
        self,
        address: str,
        sdk_account_dict: Dict,
        acc_cell: KInner,
        apps: Optional[Dict[int, SymbolicApplication]],
        assets: Optional[Dict[int, SymbolicAsset]],
    ):
        self._address = address
        self._acc_cell = acc_cell
        self._sdk_account_dict = sdk_account_dict
        self._apps = apps if apps else {}
        self._assets = assets if assets else {}

    @staticmethod
    def from_sdk_account(term_factory: KAVMTermFactory, sdk_account_dict: Dict[str, Any]) -> 'SymbolicAccount':
        try:
            apps = {}
            for sdk_app_dict in sdk_account_dict['created-apps']:
                app_id = sdk_app_dict['id']
                apps[app_id] = SymbolicApplication(app_id, term_factory.app_cell(sdk_app_dict), [])
        except KeyError:
            apps = {}
        try:
            assets = {}
            for sdk_asset_dict in sdk_account_dict['created-assets']:
                asset_id = sdk_asset_dict['index']
                assets[asset_id] = SymbolicAsset(asset_id, term_factory.asset_cell(sdk_asset_dict))
        except KeyError:
            assets = {}
        return SymbolicAccount(
            address=sdk_account_dict['address'],
            sdk_account_dict=sdk_account_dict,
            acc_cell=term_factory.account_cell(sdk_account_dict),
            apps=apps,
            assets=assets,
        )


class KAVMProof:
    def __init__(self, kavm: KAVM, use_directory: Path, claim_name: str) -> None:
        self.kavm = kavm

        self._use_directory = use_directory
        self._claim_name = claim_name

        self._sdk_txns: List[Transaction] = []
        self._txns: List[KInner] = []
        self._txn_ids: List[int] = []
        self._txns_post: List[KInner] = []
        self._accounts: List[SymbolicAccount] = []
        self._preconditions: List[KInner] = []
        self._postconditions: List[KInner] = []
        self._python_src_preconditions: List[str] = []
        self._python_src_postconditions: List[str] = []

    def add_txn(self, sdk_txn: Transaction, txn_pre: KInner, txn_post: KInner) -> None:
        self._sdk_txns.append(sdk_txn)
        self._txns.append(txn_pre)
        self._txns_post.append(txn_post)

    def add_acct(self, acct: SymbolicAccount) -> None:
        self._accounts.append(acct)

    def add_precondition(self, precondition: KInner) -> None:
        self._preconditions.append(precondition)

    def add_postcondition(self, postcondition: KInner) -> None:
        self._postconditions.append(postcondition)

    def build_app_creator_map(self) -> KInner:
        '''Construct the <appCreator> cell Kast term'''
        creator_map = []
        for acct in self._accounts:
            for app_id in acct._apps.keys():
                creator_map.append(KApply("_|->_", [intToken(app_id), algorand_address_to_k_bytes(acct._address)]))
        return build_assoc(KApply(".Map"), KLabel("_Map_"), creator_map)

    def build_asset_creator_map(self) -> KInner:
        '''Construct the <assetCreator> cell Kast term'''
        creator_map = []
        for acct in self._accounts:
            for asset_id in acct._assets.keys():
                creator_map.append(KApply("_|->_", [intToken(asset_id), algorand_address_to_k_bytes(acct._address)]))
        return build_assoc(KApply(".Map"), KLabel("_Map_"), creator_map)

    def build_transactions(self, txns: List[KInner]) -> KInner:
        return build_assoc(
            KApply(".TransactionCellMap"),
            KLabel("_TransactionCellMap_"),
            txns,
        )

    def build_accounts(self) -> KInner:
        return build_assoc(
            KToken(".Bag", "AccountCellMap"),
            KLabel("_AccountCellMap_"),
            [acc._acc_cell for acc in self._accounts],
        )

    def build_deque(self) -> KInner:
        return build_assoc(
            KApply(".List"),
            KLabel("_List_"),
            [KApply("ListItem", stringToken(str(i))) for i in range(0, len(self._txns))],
        )

    def build_deque_set(self) -> KInner:
        return build_assoc(
            KApply(".Set"),
            KLabel("_Set_"),
            [KApply("SetItem", stringToken(str(i))) for i in range(0, len(self._txns))],
        )

    def generate_scenario(self) -> KAVMScenario:
        accounts = [acc._sdk_account_dict for acc in self._accounts]
        stages = [
            {"stage-type": "setup-network", "data": {"accounts": accounts}},
            {
                "stage-type": "submit-transactions",
                "data": {
                    "transactions": KAVMScenario.sanitize_transactions(
                        [KAVMTransaction.sanitize_byte_fields(txn.dictify()) for txn in self._sdk_txns]
                    )
                },
                "expected-returncode": 0,
            },
        ]
        with open(self._use_directory / 'approval.teal') as f:
            approval_src = f.read()
        with open(self._use_directory / 'clear.teal') as f:
            clear_src = f.read()
        return KAVMScenario(stages=stages, teal_programs={'approval.teal': approval_src, 'clear.teal': clear_src})

    def simulate(self, variables: Optional[Dict] = None) -> None:
        pre = ' and '.join(self._python_src_preconditions)

        scenario_json = self.generate_scenario().to_json()
        scenario = KAVMScenario.from_json(scenario_json_str=scenario_json, teal_sources_dir=self._use_directory)

        @settings(
            deadline=timedelta(seconds=1),
            max_examples=25,
            phases=[Phase.generate],
            suppress_health_check=[HealthCheck.filter_too_much],
        )
        @given(st.data())
        def with_hypothesis(data):
            x = data.draw(st.integers())
            expr_env = {'PAYMENT_AMOUNT': x}
            assume(eval(pre, expr_env))
            run(x)

        def run(x):
            scenario._stages[1]['data']['transactions'][0]['amt'] = x
            try:
                self.kavm.run_avm_json(scenario=scenario)
            except RuntimeError as err:
                msg, stdout, stderr = err.args
                _LOGGER.critical(stdout)
                _LOGGER.critical(msg)
                _LOGGER.critical(stderr)
                raise RuntimeError from None

        with_hypothesis()
        # run(10001)

    def prove(self) -> None:

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#evalTxGroup")),
                KApply("<returncode>", intToken(4)),
                KApply("<returnstatus>", stringToken('""')),
                KApply("<transactions>", [self.build_transactions(self._txns)]),
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", stringToken('')),
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", self.build_deque()),
                                KApply("<dequeIndexSet>", self.build_deque_set()),
                            ],
                        ),
                        KApply(
                            "<currentTxnExecution>",
                            [
                                KApply(
                                    "<globals>",
                                    [
                                        KApply("<groupSize>", intToken(0)),
                                        KApply("<globalRound>", intToken(0)),
                                        KApply("<latestTimestamp>", intToken(0)),
                                        KApply("<currentApplicationID>", intToken(0)),
                                        KApply("<currentApplicationAddress>", bytesToken('')),
                                        KApply("<creatorAddress>", bytesToken('')),
                                    ],
                                ),
                                KApply(
                                    "<teal>",
                                    [
                                        KApply("<pc>", intToken(0)),
                                        KApply("<program>", KToken(".Map", "Map")),
                                        KApply("<mode>", KToken("undefined", "TealMode")),
                                        KApply("<version>", KToken("8", "Int")),
                                        KApply("<stack>", KToken(".TStack", "TStack")),
                                        KApply("<stacksize>", intToken(0)),
                                        KApply("<jumped>", KToken("false", "Bool")),
                                        KApply("<labels>", KToken(".Map", "Map")),
                                        KApply("<callStack>", KToken(".List", "List")),
                                        KApply("<scratch>", KToken(".Map", "Map")),
                                        KApply("<intcblock>", KToken(".Map", "Map")),
                                        KApply("<bytecblock>", KToken(".Map", "Map")),
                                    ],
                                ),
                                KApply("<effects>", KToken(".List", "List")),
                                KApply("<lastTxnGroupID>", stringToken("")),
                            ],
                        ),
                        KApply("<innerTransactions>", KToken(".List", "List")),
                        KApply("<activeApps>", KToken(".Set", "Set")),
                        KApply("<touchedAccounts>", KToken(".List", "List")),
                    ],
                ),
                KApply(
                    "<blockchain>",
                    [
                        KApply("<accountsMap>", self.build_accounts()),
                        KApply("<appCreator>", self.build_app_creator_map()),
                        KApply("<assetCreator>", self.build_asset_creator_map()),
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", intToken(0)),
                        KApply("<nextTxnID>", intToken(100)),
                        KApply("<nextAppID>", intToken(100)),
                        KApply("<nextAssetID>", intToken(100)),
                        KApply("<nextGroupID>", intToken(100)),
                        KApply("<txnIndexMap>", KToken(".Bag", "TxnIndexMapGroupCell")),
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),
            ],
        )

        rhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KToken(".K", "KItem ")),
                # KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", intToken(0)),
                KApply("<returnstatus>", KVariable('?_')),
                KApply("<transactions>", [self.build_transactions(self._txns_post + [KVariable('?_')])]),
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KVariable("?_")),
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", KToken(".List", "List")),
                                KApply("<dequeIndexSet>", KVariable("?_")),
                            ],
                        ),
                        KApply(
                            "<currentTxnExecution>",
                            [
                                KApply(
                                    "<globals>",
                                    [
                                        KApply("<groupSize>", KVariable("?_")),
                                        KApply("<globalRound>", KVariable("?_")),
                                        KApply("<latestTimestamp>", KVariable("?_")),
                                        KApply("<currentApplicationID>", KVariable("?_")),
                                        KApply("<currentApplicationAddress>", KVariable("?_")),
                                        KApply("<creatorAddress>", KVariable("?_")),
                                    ],
                                ),
                                KApply(
                                    "<teal>",
                                    [
                                        KApply("<pc>", KVariable("?_")),
                                        KApply("<program>", KVariable("?_")),
                                        KApply("<mode>", KVariable("?_")),
                                        KApply("<version>", KVariable("?_")),
                                        KApply("<stack>", KVariable("?_")),
                                        KApply("<stacksize>", KVariable("?_")),
                                        KApply("<jumped>", KVariable("?_")),
                                        KApply("<labels>", KVariable("?_")),
                                        KApply("<callStack>", KVariable("?_")),
                                        KApply("<scratch>", KVariable("?_")),
                                        KApply("<intcblock>", KVariable("?_")),
                                        KApply("<bytecblock>", KVariable("?_")),
                                    ],
                                ),
                                KApply("<effects>", KToken(".List", "List")),
                                KApply("<lastTxnGroupID>", KVariable("?_")),
                            ],
                        ),
                        KApply("<innerTransactions>", KVariable("?_")),
                        KApply("<activeApps>", KToken(".Set", "Set")),
                        KApply("<touchedAccounts>", KToken(".List", "List")),
                    ],
                ),
                KApply(
                    "<blockchain>",
                    [
                        KApply("<accountsMap>", KVariable("?_")),
                        KApply("<appCreator>", KVariable("?_")),
                        KApply("<assetCreator>", KVariable("?_")),
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", intToken(0)),
                        KApply("<nextTxnID>", KVariable("?_")),
                        KApply("<nextAppID>", KVariable("?_")),
                        KApply("<nextAssetID>", KVariable("?_")),
                        KApply("<nextGroupID>", KVariable("?_")),
                        KApply("<txnIndexMap>", KVariable("?_")),
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),
            ],
        )

        requires = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._preconditions)

        ensures = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._postconditions)

        claim = KClaim(
            body=push_down_rewrites(KRewrite(lhs, rhs)),
            requires=requires,
            ensures=ensures,
        )

        defn = read_kast_definition(self.kavm._verification_definition / 'parsed.json')
        symbol_table = build_symbol_table(defn)
        symbol_table['_+Bytes_'] = paren(lambda a1, a2: a1 + ' +Bytes ' + a2)
        symbol_table['_andBool_'] = paren(symbol_table['_andBool_'])

        proof = KProve(definition_dir=self.kavm._verification_definition, use_directory=self._use_directory)
        proof._symbol_table = symbol_table

        _LOGGER.info(f'Verifying specification for method: {self._claim_name}')
        result = proof.prove_claim(claim=claim, claim_id=self._claim_name)

        if type(result) is KApply and result.label.name == "#Top":
            _LOGGER.info(f'Successfully verified specifiction for method: {self._claim_name}')
        else:
            _LOGGER.error(f'Failed to verifiy specifiction for method: {self._claim_name}')
            self.report_failure(result, symbol_table)

    def report_failure(self, final_term: KInner, symbol_table: Dict):

        final_config_filename = self._use_directory / f'{self._claim_name}_final_configuration.txt'
        scenario_filename = self._use_directory / f'{self._claim_name}_simulation.json'
        with open(final_config_filename, 'w') as file:
            file.write(pretty_print_kast(minimize_term(inline_cell_maps(final_term)), symbol_table=symbol_table))
        config, constraints = split_config_and_constraints(final_term)
        _, subst = split_config_from(config)
        try:
            _LOGGER.info(f"KAVM <returnstatus>: {subst['RETURNSTATUS_CELL'].token}")
        except Exception:
            pass

        pretty_constraints = [
            pretty_print_kast(omit_large_tokens(term), symbol_table=symbol_table)
            for term in flatten_label('#And', constraints)
        ]
        pretty_constraints.reverse()
        pretty_constraints_str = '\n #And '.join(pretty_constraints)
        _LOGGER.info(f'Constraints: \n {pretty_constraints_str}')
        _LOGGER.info(f'Pretty printed final configuration to {final_config_filename}')
        scenario = self.generate_scenario()
        _LOGGER.info(f'Writing concrete simulation scenario to {scenario_filename}')
        with open(scenario_filename, 'w') as file:
            file.write(scenario.to_json(indent=4))


def write_to_file(program: str, path: Path):
    with open(path, "w") as f:
        f.write(program)


class AutoProver:
    @staticmethod
    def _in_bounds_uint64(term: KInner) -> KInner:
        return KApply(
            '_andBool_',
            [
                KApply("_>=Int_", [term, intToken(0)]),
                KApply("_<=Int_", [term, KToken("MAX_UINT64", "Int")]),
            ],
        )

    @classmethod
    def _faucet_account(cls) -> Tuple[str, str]:
        """
        Return a pre-generatd pair of private key and Algorand adress for the faucet account
        """
        return (
            'cz+FBjUbtcM8bkMHCZfs/L9WnZVx7VSEa6KwRk9BQIQVVR6aLOAyPc66Z0b6PMC2TmX2ZEBlyNvG/XhtQmK04g==',
            'CVKR5GRM4AZD3TV2M5DPUPGAWZHGL5TEIBS4RW6G7V4G2QTCWTRIGNDVXQ',
        )

    def prove(self, method_name: str) -> None:
        self._proofs[method_name].prove()

    def simulate(self, method_name: str) -> None:
        self._proofs[method_name].simulate()

    def __init__(
        self,
        pyteal_module_name: str,
        app_id: int,
        sdk_app_creator_account_dict: Dict,
        sdk_app_account_dict: Dict,
        method_names: Optional[List[str]] = None,
        use_directory: Optional[Path] = None,
        definition_dir: Optional[Path] = None,
        verification_definition_dir: Optional[Path] = None,
    ):

        if use_directory:
            self._use_directory = use_directory
        else:
            self._use_directory = Path('.kavm')
        self._use_directory.mkdir(parents=True, exist_ok=True)
        _LOGGER.info(f'KAVM AutoProver will store its artefacts in directory {self._use_directory.resolve()}')

        if not definition_dir:
            definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
            if not definition_dir:
                msg = 'Cannot initialize AutoProver: neither definition_dir is provided nor KAVM_DEFINITION_DIR env variable is set'
                _LOGGER.critical(msg)
                raise RuntimeError(msg)
            definition_dir = Path(definition_dir)
        if not verification_definition_dir:
            verification_definition_dir = os.environ.get('KAVM_VERIFICATION_DEFINITION_DIR')
            if not verification_definition_dir:
                msg = 'Cannot initialize AutoProver: neither verification_definition_dir is provided nor KAVM_VERIFICATION_DEFINITION_DIR env variable is set'
                _LOGGER.critical(msg)
                raise RuntimeError(msg)
            verification_definition_dir = Path(verification_definition_dir)

        self.kavm = KAVM(
            definition_dir=definition_dir,
            use_directory=use_directory,
            verification_definition_dir=verification_definition_dir,
        )

        # monkey path the pyteal.Router class with pre-/post-conditions decorators
        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                target=pyteal.Router,
                name='hoare_method',
                value=router_hoare_method,
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.Router,
                name='precondition',
                value=router_precondition,
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.Router,
                name='postcondition',
                value=router_postcondition,
                raising=False,
            )
            pyteal_module = importlib.import_module(pyteal_module_name)
            approval_pgm, clear_pgm, contract = pyteal_module.router.compile_program(version=8)

        method_names = method_names if method_names else [m.name for m in contract.methods]
        approval_pgm_path = self._use_directory / 'approval.teal'
        clear_pgm_path = self._use_directory / 'clear.teal'
        write_to_file(approval_pgm, approval_pgm_path)
        write_to_file(clear_pgm, clear_pgm_path)

        self._proofs: Dict[str, KAVMProof] = {}

        sp = SuggestedParams(
            fee=1000, first=0, last=1, gh='KAVMKAVMKAVMKAVMKAVMKAVMKAVMKAVMKAVMKAVMKAVM', flat_fee=True
        )

        term_factory = KAVMTermFactory(self.kavm)

        _LOGGER.info(f'Initializing proofs for contract {contract.name}')

        approval_labels, parsed_approval_pgm = preprocess_teal_program(
            self.kavm.kore_to_kast(self.kavm.parse_teal(approval_pgm_path))
        )
        clear_labels, parsed_clear_pgm = preprocess_teal_program(
            self.kavm.kore_to_kast(self.kavm.parse_teal(clear_pgm_path))
        )

        app_account = SymbolicAccount.from_sdk_account(term_factory, sdk_app_account_dict)
        creator_account = SymbolicAccount.from_sdk_account(term_factory, sdk_app_creator_account_dict)

        # Set approval and clear state pgms. BEWARE! This will work only if the account created a single app
        creator_account._acc_cell = set_cell(creator_account._acc_cell, 'APPROVALPGMSRC_CELL', parsed_approval_pgm)
        creator_account._acc_cell = set_cell(creator_account._acc_cell, 'CLEARSTATEPGMSRC_CELL', parsed_clear_pgm)

        asset_id = list(app_account._assets.keys())[0]

        labels = remove_duplicates(approval_labels + clear_labels)
        labels_are_deduped = []
        for i in range(len(labels)):
            labels_are_deduped.append(
                KApply(
                    "_==Int_",
                    [labels[i], intToken(i)],
                )
            )

        contract.methods = [m for m in contract.methods if m.name in method_names]

        for method in contract.methods:
            if not isinstance(method, HoareMethod):
                _LOGGER.info(f'Skipping method {method.name} as it is not marked with @router.hoare_method')
                continue
            proof = KAVMProof(
                kavm=self.kavm,
                use_directory=self._use_directory,
                claim_name=f'{contract.name}-{method.name}',
            )
            proof.add_acct(creator_account)
            proof.add_acct(app_account)

            _LOGGER.info(f'Generating K claim for method {method.name}')
            app_args: List[KInner] = [method_selector_to_k_bytes(method.get_selector())]
            for i, arg in enumerate(method.args):
                _LOGGER.info(f'Analyzing method argument {i} with name {arg.name} of type {arg.type}')
                if str(arg.type) == 'uint64':
                    arg_k_var = KVariable(str(arg.name).upper(), sort=KSort("Int"))
                    app_args.append(int_2_bytes(arg_k_var))
                    arg_pre = AutoProver._in_bounds_uint64(arg_k_var)
                    _LOGGER.info(f'Adding precondiotion on argument {arg.name}: {self.kavm.pretty_print(arg_pre)}')
                    method._preconditions.append(arg_pre)
                elif str(arg.type) == 'pay':
                    concrete_amount = 1000  # will be overriden by symbolic value
                    sdk_txn = PaymentTxn(
                        sender=creator_account._address, receiver=app_account._address, sp=sp, amt=concrete_amount
                    )
                    amount_k_var = KVariable(str(arg.name + '_AMOUNT').upper(), sort=KSort("Int"))
                    txn_pre = transaction_k_term(
                        kavm=self.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                                'RECEIVER_CELL': algorand_address_to_k_bytes(sdk_txn.receiver),
                            }
                        ),
                    )
                    txn_post = transaction_k_term(
                        kavm=self.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                                'RECEIVER_CELL': algorand_address_to_k_bytes(sdk_txn.receiver),
                                'RESUME_CELL': KVariable('?_'),
                            }
                        ),
                    )
                    amount_pre = AutoProver._in_bounds_uint64(amount_k_var)
                    _LOGGER.info(f'Adding precondiotion on argument {arg.name}: {self.kavm.pretty_print(amount_pre)}')
                    method._preconditions.append(amount_pre)
                    proof.add_txn(sdk_txn, txn_pre, txn_post)
                elif str(arg.type) == 'axfer':
                    sdk_txn = AssetTransferTxn(
                        sender=creator_account._address, receiver=app_account._address, sp=sp, index=asset_id, amt=0
                    )
                    amount_k_var = KVariable(str(arg.name + '_AMOUNT').upper(), sort=KSort("Int"))
                    txn_pre = transaction_k_term(
                        kavm=self.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'ASSETAMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                                'ASSETRECEIVER_CELL': algorand_address_to_k_bytes(sdk_txn.receiver),
                            }
                        ),
                    )
                    txn_post = transaction_k_term(
                        kavm=self.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'ASSETAMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                                'ASSETRECEIVER_CELL': algorand_address_to_k_bytes(sdk_txn.receiver),
                                'RESUME_CELL': KVariable('?_'),
                            }
                        ),
                    )
                    amount_pre = AutoProver._in_bounds_uint64(amount_k_var)
                    _LOGGER.info(f'Adding precondiotion on argument {arg.name}: {self.kavm.pretty_print(amount_pre)}')
                    method._preconditions.append(amount_pre)
                    proof.add_txn(sdk_txn, txn_pre, txn_post)
                else:
                    _LOGGER.critical(f"Not yet supported: method argument of type {arg.type}")
                    exit(1)

            for pre in method._preconditions:
                proof.add_precondition(pre)
            for post in method._postconditions:
                proof.add_postcondition(post)

            for pre in method._python_src_preconditions:
                proof._python_src_preconditions.append(pre)
            for post in method._python_src_postconditions:
                proof._python_src_postconditions.append(post)

            # for method_txn in method.txn_calls:
            sdk_txn = ApplicationCallTxn(
                sender=creator_account._address,
                index=app_id,
                on_complete=0,
                sp=sp,
                app_args=[method.get_selector()],
            )
            txn_pre = transaction_k_term(
                kavm=self.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fields_subst=Subst(
                    {
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                    }
                ),
            )
            txn_post = transaction_k_term(
                kavm=self.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fields_subst=Subst(
                    {
                        'SENDER_CELL': algorand_address_to_k_bytes(sdk_txn.sender),
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'TXSCRATCH_CELL': KVariable('?_'),
                        'LOGDATA_CELL': KVariable('?FINAL_LOGDATA_CELL'),
                        'LOGSIZE_CELL': KVariable('?_'),
                        'RESUME_CELL': KVariable('?_'),
                    }
                ),
            )
            proof.add_txn(sdk_txn, txn_pre, txn_post)
            proof._preconditions = proof._preconditions + labels_are_deduped
            self._proofs[method.name] = proof

        _LOGGER.info(
            f'Initialized K proofs for methods: {[contract.name + "-" + proof_name for proof_name in self._proofs.keys()]}'
        )
