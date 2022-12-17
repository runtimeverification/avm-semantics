import logging
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple, Set, Any, Callable
import pytest

from algosdk.abi.contract import Contract
from algosdk.abi.method import Method
from algosdk.encoding import checksum, decode_address, encode_address
from algosdk.future.transaction import ApplicationCallTxn, AssetTransferTxn, PaymentTxn, StateSchema

import pyteal
from pyteal.ir import Op

from pyk.kast.inner import KApply, KInner, KLabel, KRewrite, KSort, KToken, KVariable, Subst, build_assoc
from pyk.kast.manip import inline_cell_maps, push_down_rewrites, set_cell
from pyk.kast.outer import KClaim, read_kast_definition
from pyk.ktool.kprint import build_symbol_table, paren, pretty_print_kast
from pyk.ktool.kprove import KProve
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken
from pyk.prelude.bytes import bytesToken

from kavm.adaptors.algod_transaction import transaction_k_term
from kavm.adaptors.algod_account import sdk_account_created_app_ids, sdk_account_created_asset_ids
from kavm.algod import KAVMClient
from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_addres_to_k_bytes, generate_tvalue_list, int_2_bytes, method_selector_to_k_bytes
from kavm.kast.factory import KAVMTermFactory

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def last_log_item_eq(int_term: KInner):
    return KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(int_term, BE, Unsigned), 8, 0)
        "_==K_",
        [
            KVariable('?FINAL_LOGDATA_CELL'),
            KApply(
                '_+Bytes_',
                [
                    bytesToken("\\x15\\x1f|u"),
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
    # if not (isinstance(expr, pyteal.BinaryExpr) and expr.op in pyteal_op_to_k_op.keys()):
    #     raise ValueError(f'Unsupported PyTeal expression: {expr}. Must be an "lhs ==,!=,>,>=,<,<= rhs"')


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

    def amount(self):
        self.var_name = self.var_name + '_amount'
        return self


class HoareMethod(Method):
    def __init__(self, *args, **kwargs) -> None:
        Method.__init__(self, *args, **kwargs)
        self._preconditions = []
        self._postconditions = []

    @staticmethod
    def from_plain_method(m: Method):
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
                value=lambda txn: SymbolicInt(var_name=f'payment'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.AssetTransferTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name=f'asset_transfer'),
                raising=False,
            )
            spec = eval(expr, expr_env)

        for m in self.methods:
            if m.name == func.method_spec().name and isinstance(m, HoareMethod):
                m._preconditions.append(pyteal_expr_to_kast(spec))
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
                value=lambda txn: SymbolicInt(var_name=f'payment'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.AssetTransferTransaction,
                name='get',
                value=lambda txn: SymbolicInt(var_name=f'asset_transfer'),
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.abi.Uint,
                name='get',
                value=lambda txn: SymbolicInt(var_name=f'output'),
                raising=False,
            )
            spec = eval(expr, expr_env)

        for m in self.methods:
            if m.name == func.method_spec().name:
                m._postconditions.append(last_log_item_eq(pyteal_expr_to_kast(spec.argRight)))
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
            if term.label.name == "method__TEAL-OPCODES_PseudoOpCode_TBytesLiteral":
                if type(term.args[0]) is KToken:
                    selector = str(Method.from_signature(term.args[0].token[1:-1]).get_selector())[2:-1]
                    return KApply("byte__TEAL-OPCODES_PseudoOpCode_TBytesLiteral", stringToken(selector))
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
                    return stringToken(hex_token_to_k_string(term.token[2:]))

                else:
                    return term
            else:
                return term

    pgm = preprocess_teal_program_impl(term)

    return labels, pgm


class SymbolicApplication:
    def __init__(self, app_id: int, app_cell: KInner, labels: List[KInner]):
        self._app_id = app_id
        self._app_cell = app_cell
        self._labels = labels


class SymbolicAsset:
    def __init__(self, asset_id: int, asset_cell: KInner):
        self._asset_id = asset_id
        self._asset_cell = asset_cell


class SymbolicAccount:
    def __init__(
        self,
        address: str,
        acc_cell: KInner,
        apps: Optional[Dict[int, SymbolicApplication]],
        assets: Optional[Dict[int, SymbolicAsset]],
    ):
        self._address = address
        self._acc_cell = acc_cell
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
            acc_cell=term_factory.account_cell(sdk_account_dict),
            apps=apps,
            assets=assets,
        )


class KAVMProof:
    def __init__(self, kavm: KAVM, use_directory: Path, claim_name: str) -> None:
        self.kavm = kavm

        self._use_directory = use_directory
        self._claim_name = claim_name

        self._txns: List[KInner] = []
        self._txn_ids: List[int] = []
        self._txns_post: List[KInner] = []
        self._accounts: List[SymbolicAccount] = []
        self._preconditions: List[KInner] = []
        self._postconditions: List[KInner] = []

    def add_txn(self, txn_pre: KInner, txn_post: KInner) -> None:
        self._txns.append(txn_pre)
        self._txns_post.append(txn_post)

    def add_acct(self, acct: SymbolicAccount) -> None:
        self._accounts.append(acct)
        # self._accounts.append(acct)

    def add_precondition(self, precondition: KInner) -> None:
        self._preconditions.append(precondition)

    def add_postcondition(self, postcondition: KInner) -> None:
        self._postconditions.append(postcondition)

    def build_app_creator_map(self) -> KInner:
        '''Construct the <appCreator> cell Kast term'''
        creator_map = []
        for acct in self._accounts:
            for app_id in acct._apps.keys():
                creator_map.append(KApply("_|->_", [intToken(app_id), algorand_addres_to_k_bytes(acct._address)]))
        return build_assoc(KApply(".Map"), KLabel("_Map_"), creator_map)

    def build_asset_creator_map(self) -> KInner:
        '''Construct the <assetCreator> cell Kast term'''
        creator_map = []
        for acct in self._accounts:
            for asset_id in acct._assets.keys():
                creator_map.append(KApply("_|->_", [intToken(asset_id), algorand_addres_to_k_bytes(acct._address)]))
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

    def prove(self) -> None:

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#evalTxGroup")),
                KApply("<panicstatus>", stringToken("")),
                KApply("<paniccode>", intToken(0)),
                KApply("<returnstatus>", stringToken("Failure - AVM is stuck")),
                KApply("<returncode>", intToken(4)),
                KApply("<transactions>", [self.build_transactions(self._txns)]),
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KToken("\"\"", "String")),
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
                                        KApply("<currentApplicationAddress>", KToken(".Bytes", "Bytes")),
                                        KApply("<creatorAddress>", KToken(".Bytes", "Bytes")),
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
                        KApply("<assetCreator>", KToken(".Map", "Map")),
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
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", intToken(0)),
                KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", intToken(0)),
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

        result = proof.prove_claim(claim=claim, claim_id=self._claim_name)

        if type(result) is KApply and result.label.name == "#Top":
            print(f"Proved {self._claim_name}")
        else:
            print(f"Failed to prove {self._claim_name}")
            print("counterexample:")

            print(pretty_print_kast(inline_cell_maps(result), symbol_table=symbol_table))


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

    def __init__(
        self,
        definition_dir: Path,
        contract: Contract,
        approval_pgm: Path,
        clear_pgm: Path,
        app_id: int,
        sdk_app_creator_account_dict: Dict,
        sdk_app_account_dict: Dict,
    ):

        self._proofs: Dict[str, KAVMProof] = {}

        _, faucet_addr = AutoProver._faucet_account()
        self.algod = KAVMClient(faucet_address=str(faucet_addr))
        self.algod.kavm._verification_definition = definition_dir
        # _, creator_addr = AutoProver._creator_account()
        sp = self.algod.suggested_params()

        term_factory = KAVMTermFactory(self.algod.kavm)

        _LOGGER.info(f'Initializing proofs for contract {contract.name}')

        approval_labels, parsed_approval_pgm = preprocess_teal_program(
            self.algod.kavm.kore_to_kast(self.algod.kavm.parse_teal(approval_pgm))
        )
        clear_labels, parsed_clear_pgm = preprocess_teal_program(
            self.algod.kavm.kore_to_kast(self.algod.kavm.parse_teal(clear_pgm))
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
            for j in range(len(labels)):
                if i == j:
                    continue
                labels_are_deduped.append(KApply("_=/=K_", [labels[i], labels[j]]))

        for method in contract.methods:
            if not isinstance(method, HoareMethod):
                _LOGGER.info(f'Skipping method {method.name} as it is not marked with @router.hoare_method')
                continue
            proof = KAVMProof(
                kavm=self.algod.kavm,
                use_directory=Path("proofs"),
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
                    _LOGGER.info(
                        f'Adding precondiotion on argument {arg.name}: {self.algod.kavm.pretty_print(arg_pre)}'
                    )
                    method._preconditions.append(arg_pre)
                elif str(arg.type) == 'pay':
                    sdk_txn = PaymentTxn(sender=creator_account._address, receiver=app_account._address, sp=sp, amt=0)
                    amount_k_var = KVariable(str(arg.name + '_AMOUNT').upper(), sort=KSort("Int"))
                    txn_pre = transaction_k_term(
                        kavm=self.algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_addres_to_k_bytes(sdk_txn.sender),
                                'RECEIVER_CELL': algorand_addres_to_k_bytes(sdk_txn.receiver),
                            }
                        ),
                    )
                    txn_post = transaction_k_term(
                        kavm=self.algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': KToken(
                                    "b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"
                                ),
                                'RECEIVER_CELL': KToken(
                                    "b\"" + str(decode_address(sdk_txn.receiver))[2:-1] + "\"", "Bytes"
                                ),
                                'RESUME_CELL': KVariable('?_'),
                            }
                        ),
                    )
                    amount_pre = AutoProver._in_bounds_uint64(amount_k_var)
                    _LOGGER.info(
                        f'Adding precondiotion on argument {arg.name}: {self.algod.kavm.pretty_print(amount_pre)}'
                    )
                    method._preconditions.append(amount_pre)
                    proof.add_txn(txn_pre, txn_post)
                elif str(arg.type) == 'axfer':
                    _LOGGER.info(f'Skipping {method.name}')
                    sdk_txn = AssetTransferTxn(
                        sender=creator_account._address, receiver=app_account._address, sp=sp, index=asset_id, amt=0
                    )
                    amount_k_var = KVariable(str(arg.name + '_AMOUNT').upper(), sort=KSort("Int"))
                    txn_pre = transaction_k_term(
                        kavm=self.algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'ASSETAMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_addres_to_k_bytes(sdk_txn.sender),
                                'ASSETRECEIVER_CELL': algorand_addres_to_k_bytes(sdk_txn.receiver),
                            }
                        ),
                    )
                    txn_post = transaction_k_term(
                        kavm=self.algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fields_subst=Subst(
                            {
                                'ASSETAMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_addres_to_k_bytes(sdk_txn.sender),
                                'ASSETRECEIVER_CELL': algorand_addres_to_k_bytes(sdk_txn.receiver),
                                'RESUME_CELL': KVariable('?_'),
                            }
                        ),
                    )
                    amount_pre = AutoProver._in_bounds_uint64(amount_k_var)
                    _LOGGER.info(
                        f'Adding precondiotion on argument {arg.name}: {self.algod.kavm.pretty_print(amount_pre)}'
                    )
                    method._preconditions.append(amount_pre)
                    proof.add_txn(txn_pre, txn_post)
                else:
                    _LOGGER.critical(f"Not yet supported: method argument of type {arg.type}")
                    exit(1)

            for pre in method._preconditions:
                proof.add_precondition(pre)
            for post in method._postconditions:
                proof.add_postcondition(post)

            # for method_txn in method.txn_calls:
            sdk_txn = ApplicationCallTxn(sender=creator_account._address, index=app_id, on_complete=0, sp=sp)
            txn_pre = transaction_k_term(
                kavm=self.algod.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fields_subst=Subst(
                    {
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'SENDER_CELL': KToken("b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"),
                    }
                ),
            )
            txn_post = transaction_k_term(
                kavm=self.algod.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fields_subst=Subst(
                    {
                        'SENDER_CELL': KToken("b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"),
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'TXSCRATCH_CELL': KVariable('?_'),
                        'LOGDATA_CELL': KVariable('?FINAL_LOGDATA_CELL'),
                        'LOGSIZE_CELL': KVariable('?_'),
                        'RESUME_CELL': KVariable('?_'),
                    }
                ),
            )
            proof.add_txn(txn_pre, txn_post)
            proof._preconditions = proof._preconditions + labels_are_deduped
            self._proofs[method.name] = proof

        _LOGGER.info(
            f'Initialized K proofs for methods: {[contract.name + "-" + proof_name for proof_name in self._proofs.keys()]}'
        )
