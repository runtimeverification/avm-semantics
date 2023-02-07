# type: ignore

import copy
import itertools
import logging
import os
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Set

from algosdk.future.transaction import Transaction
from pyk.kast.inner import (
    KApply,
    KInner,
    KLabel,
    KRewrite,
    KSort,
    KToken,
    KVariable,
    Subst,
    build_assoc,
    var_occurrences,
)
from pyk.kast.manip import (
    inline_cell_maps,
    minimize_term,
    push_down_rewrites,
    split_config_and_constraints,
    split_config_from,
)
from pyk.kast.outer import KClaim
from pyk.ktool.kprint import build_symbol_table, paren, pretty_print_kast
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken

from kavm.adaptors.algod_transaction import transaction_k_term
from kavm.kast.factory import KAVMTermFactory
from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_address_to_k_bytes

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


class SymbolicApplication:  # noqa: B903
    def __init__(self, app_id: int, app_cell: KInner):
        self._app_id = app_id
        self._app_cell = app_cell


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
        self._vars: Set[KVariable] = collect_vars(sdk_account_dict)

    @staticmethod
    def from_sdk_account(
        term_factory: KAVMTermFactory,
        sdk_account_dict: Dict[str, Any],
        teal_sources_dir: Path,
    ) -> 'SymbolicAccount':
        '''
        Traverse the nexted sdk_account dict that holds the account's data,
        including created apps and assets and:
        * Generate K cells for apps and assets
        * Bring created apps and assets to the top level of the resulting SymbolicAccount object.
          indexing them by their ids
        '''
        try:
            apps = {}
            for sdk_app_dict in sdk_account_dict['created-apps']:
                app_id = sdk_app_dict['id']
                apps[app_id] = SymbolicApplication(
                    app_id, term_factory.app_cell(sdk_app_dict=sdk_app_dict, teal_sources_dir=teal_sources_dir)
                )
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
            acc_cell=term_factory.account_cell(sdk_account_dict, teal_sources_dir),
            apps=apps,
            assets=assets,
        )


def collect_vars(symbolic_sdk_dict: Dict[str, Any]) -> Set[KVariable]:
    result = set()

    def doit(d: Dict[str, Any]) -> None:
        for v in d.values():
            if isinstance(v, KVariable):
                result.add(v)
            if isinstance(v, Dict):
                doit(v)

    doit(symbolic_sdk_dict)
    return result


class KAVMProof:
    def __init__(
        self,
        kavm: KAVM,
        claim_name: str,
        accts: List[Dict[str, Any]],
        sdk_txns: List[Transaction],
        teal_sources_dir: Optional[Path] = None,
        preconditions: Optional[List[KInner]] = None,
    ) -> None:
        self.kavm = kavm

        self._use_directory = kavm.use_directory
        self._claim_name = claim_name

        self._accounts: List[SymbolicAccount] = [
            SymbolicAccount.from_sdk_account(
                term_factory=KAVMTermFactory(self.kavm),
                sdk_account_dict=acc,
                teal_sources_dir=teal_sources_dir,
            )
            for acc in accts
        ]
        txn_fields_subst = lambda i: Subst({'GROUPIDX_CELL': intToken(i)})
        self._txns_pre = [
            transaction_k_term(kavm=kavm, txid=str(txn_id), txn=txn, symbolic_fields_subst=txn_fields_subst(txn_id))
            for txn_id, txn in enumerate(sdk_txns)
        ]

        self._preconditions: List[KInner] = preconditions if preconditions else []
        self._postconditions: List[KInner] = []

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

    @staticmethod
    def build_deque(txn_ids: List[str]) -> KInner:
        return build_assoc(
            KApply(".List"),
            KLabel("_List_"),
            [KApply("ListItem", stringToken(txn_id)) for txn_id in txn_ids],
        )

    @staticmethod
    def build_deque_set(txn_ids: List[str]) -> KInner:
        return build_assoc(
            KApply(".Set"),
            KLabel("_Set_"),
            [KApply("SetItem", stringToken(txn_id)) for txn_id in txn_ids],
        )

    def build_claim(self) -> KClaim:
        symbolic_config, subst = split_config_from(self.kavm.definition.init_config(KSort('KavmCell')))

        txn_ids = [str(idx) for idx, _ in enumerate(self._txns_pre)]

        ### build LHS substitution from provided account and transaction data
        lhs_subst = copy.deepcopy(subst)
        lhs_subst['ACCOUNTSMAP_CELL'] = self.build_accounts()
        lhs_subst['APPCREATOR_CELL'] = self.build_app_creator_map()
        lhs_subst['ASSETCREATOR_CELL'] = self.build_asset_creator_map()
        lhs_subst['TRANSACTIONS_CELL'] = self.build_transactions(txns=self._txns_pre)
        lhs_subst['DEQUE_CELL'] = KAVMProof.build_deque(txn_ids)
        lhs_subst['DEQUEINDEXSET_CELL'] = KAVMProof.build_deque_set(txn_ids)
        lhs_subst['TXNINDEXMAP_CELL'] = KToken('.Bag', 'TxnIndexMapGroupCell')
        lhs_subst['K_CELL'] = KApply('#evalTxGroup')
        lhs_subst['NEXTTXNID_CELL'] = intToken(len(self._txns_pre))
        lhs_subst['NEXTGROUPID_CELL'] = intToken(2)
        lhs_subst['NEXTAPPID_CELL'] = intToken(2)
        lhs_subst['NEXTASSETID_CELL'] = intToken(2)

        lhs = Subst(lhs_subst).apply(symbolic_config)

        # free variables of sort Int in accounts (TODO: and transactions)
        # should be uint64. Build range predicates:
        lhs_range_predicates = []
        acc_vars = set().union(*[acc._vars for acc in self._accounts])
        txn_vars = set()
        for txn in self._txns_pre:
            txn_vars = txn_vars.union(itertools.chain.from_iterable(var_occurrences(txn).values()))
        for var in acc_vars.union(txn_vars):
            if var.sort is not None and var.sort == KSort('Int'):
                range_predicate_term = KAVMTermFactory.range_uint(64, var)
                lhs_range_predicates.append(range_predicate_term)
                _LOGGER.info(f'adding range predicate as precondition: {self.kavm.pretty_print(range_predicate_term)}')

        requires = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._preconditions + lhs_range_predicates)

        ### build RHS substitution with either LHS data or existential variables
        rhs_subst = copy.deepcopy(subst)
        rhs_subst['ACCOUNTSMAP_CELL'] = KVariable('?_')
        rhs_subst['APPCREATOR_CELL'] = lhs_subst['APPCREATOR_CELL']
        rhs_subst['ASSETCREATOR_CELL'] = lhs_subst['ASSETCREATOR_CELL']
        rhs_subst['TRANSACTIONS_CELL'] = KVariable('?_')
        rhs_subst['DEQUEINDEXSET_CELL'] = lhs_subst['DEQUEINDEXSET_CELL']
        rhs_subst['DEQUE_CELL'] = KToken('.List', 'List')
        rhs_subst['TXNINDEXMAP_CELL'] = KVariable('?_')

        # <avmExecution> post-state
        rhs_subst['CURRENTTX_CELL'] = KVariable('?_')
        rhs_subst['DEQUE_CELL'] = KVariable('?_')
        rhs_subst['DEQUEINDEXSET_CELL'] = KVariable('?_')
        rhs_subst['GROUPSIZE_CELL'] = KVariable('?_')
        rhs_subst['GLOBALROUND_CELL'] = KVariable('?_')
        rhs_subst['LATESTTIMESTAMP_CELL'] = KVariable('?_')
        rhs_subst['CURRENTAPPLICATIONID_CELL'] = KVariable('?_')
        rhs_subst['CURRENTAPPLICATIONADDRESS_CELL'] = KVariable('?_')
        rhs_subst['CREATORADDRESS_CELL'] = KVariable('?_')
        rhs_subst['PC_CELL'] = KVariable('?_')
        rhs_subst['PROGRAM_CELL'] = KVariable('?_')
        rhs_subst['MODE_CELL'] = KVariable('?_')
        rhs_subst['VERSION_CELL'] = KVariable('?_')
        rhs_subst['STACK_CELL'] = KVariable('?_')
        rhs_subst['STACKSIZE_CELL'] = KVariable('?_')
        rhs_subst['JUMPED_CELL'] = KVariable('?_')
        rhs_subst['LABELS_CELL'] = KVariable('?_')
        rhs_subst['CALLSTACK_CELL'] = KVariable('?_')
        rhs_subst['SCRATCH_CELL'] = KVariable('?_')
        rhs_subst['INTCBLOCK_CELL'] = KVariable('?_')
        rhs_subst['BYTECBLOCK_CELL'] = KVariable('?_')
        rhs_subst['EFFECTS_CELL'] = KVariable('?_')
        rhs_subst['LASTTXNGROUPID_CELL'] = KVariable('?_')
        rhs_subst['INNERTRANSACTIONS_CELL'] = KVariable('?_')
        rhs_subst['ACTIVEAPPS_CELL'] = KVariable('?_')
        rhs_subst['TOUCHEDACCOUNTS_CELL'] = KVariable('?_')

        # <k> and friends post-state
        rhs_subst['RETURNSTATUS_CELL'] = KVariable('?_')
        rhs_subst['RETURNCODE_CELL'] = intToken(0)
        rhs_subst['K_CELL'] = KVariable('.K')
        # rhs_subst['K_CELL'] = KVariable('#panic(1000)')
        rhs_subst['NEXTTXNID_CELL'] = KVariable('?_')
        rhs_subst['NEXTGROUPID_CELL'] = KVariable('?_')
        rhs_subst['NEXTAPPID_CELL'] = KVariable('?_')
        rhs_subst['NEXTASSETID_CELL'] = KVariable('?_')

        rhs = Subst(rhs_subst).apply(symbolic_config)
        ensures = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._postconditions)

        claim = KClaim(
            body=push_down_rewrites(KRewrite(lhs, rhs)),
            requires=requires,
            ensures=ensures,
        )

        return claim

    def prove(self) -> None:
        claim = self.build_claim()

        kavm_haskell = KAVM(
            definition_dir=Path(os.environ.get('KAVM_VERIFICATION_DEFINITION_DIR')), use_directory=self._use_directory
        )
        kavm_haskell._write_claim_definition(claim, self._claim_name)

        # defn = read_kast_definition(self.kavm._verification_definition / 'parsed.json')
        symbol_table = build_symbol_table(kavm_haskell.definition)
        symbol_table['_+Bytes_'] = paren(lambda a1, a2: a1 + ' +Bytes ' + a2)
        symbol_table['_andBool_'] = paren(symbol_table['_andBool_'])
        kavm_haskell._symbol_table = symbol_table

        result = kavm_haskell.prove_claim(claim=claim, claim_id=self._claim_name)

        if type(result) is KApply and result.label.name == "#Top":
            _LOGGER.info(f"Proved {self._claim_name}")
        else:
            _LOGGER.error(f"Failed to prove {self._claim_name}:")
            self.report_failure(result, self.kavm.symbol_table)

    def report_failure(self, final_term: KInner, symbol_table: Dict):
        final_config_filename = self._use_directory / f'{self._claim_name}_final_configuration.txt'
        with open(final_config_filename, 'w') as file:
            file.write(pretty_print_kast(minimize_term(inline_cell_maps(final_term)), symbol_table=symbol_table))
        config, constraints = split_config_and_constraints(final_term)
        symbolic_config, subst = split_config_from(config)
        _LOGGER.info('KAVM return code: ' + pretty_print_kast(subst['RETURNCODE_CELL'], symbol_table=symbol_table))
        _LOGGER.info('KAVM return status: ' + pretty_print_kast(subst['RETURNSTATUS_CELL'], symbol_table=symbol_table))
        _LOGGER.info('Constraints: ')
        _LOGGER.info(pretty_print_kast(constraints, symbol_table=symbol_table))
        # print(pretty_print_kast(get_cell(final_term, 'TEAL_CELL'), symbol_table=symbol_table))
        _LOGGER.info(f'Pretty printed final configuration to {final_config_filename}')
        exit(1)
