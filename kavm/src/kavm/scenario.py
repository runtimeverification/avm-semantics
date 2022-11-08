import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast, Set
from collections import OrderedDict

from algosdk.future.transaction import (
    Transaction,
)
from algosdk import encoding


from pyk.kast import KApply, KAst, KInner, KSort, KToken, Subst
from pyk.kastManip import flatten_label, split_config_from
from pyk.prelude.kint import intToken


from kavm.adaptors.algod_account import KAVMAccount
from kavm.constants import MIN_BALANCE
from kavm.pyk_utils import AppCellMap, split_direct_subcells_from


class KAVMScenario:
    """
    Rerpesentation of a JSON testing scenario for KAVM
    """

    def __init__(self, stages: List[Any], teal_files: Set[str]) -> None:
        self._stages = stages
        self._teal_files = teal_files

    @staticmethod
    def sanitize_accounts(accounts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for acc_dict in accounts_data:
            acc_dict_translated = {KAVMAccount.inverted_attribute_map[k]: v for k, v in acc_dict.items()}
            result.append(KAVMAccount(**acc_dict_translated).dictify())
        return result

    @staticmethod
    def sanitize_transactions(txn_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def _sort_txn_dict(txn_dict: Dict[str, Any]) -> OrderedDict[str, Any]:
            od = OrderedDict()
            for k, v in sorted(txn_dict.items()):
                if isinstance(v, dict):
                    od[k] = _sort_txn_dict(v)
                od[k] = v
            return od

        def _insert_defaults(txn_dict: Dict[str, Any]) -> Dict[str, Any]:
            if not 'lv' in txn_dict:
                txn_dict['lv'] = 1
            if not 'gh' in txn_dict:
                txn_dict['gh'] = 'kteal'
            if not 'fee' in txn_dict:
                txn_dict['fee'] = 1000
            if not 'grp' in txn_dict:
                txn_dict['grp'] = 'dummy_grp'
            if txn_dict['type'] == 'appl':
                if not 'apid' in txn_dict:
                    txn_dict['apid'] = 0
                if not 'apan' in txn_dict:
                    txn_dict['apan'] = 0
                if not 'apat' in txn_dict:
                    txn_dict['apat'] = []
                if not 'apfa' in txn_dict:
                    txn_dict['apfa'] = []
                if not 'apas' in txn_dict:
                    txn_dict['apas'] = []
                if not 'apgs' in txn_dict:
                    txn_dict['apgs'] = {'nui': 0, 'nbs': 0}
                if not 'apls' in txn_dict:
                    txn_dict['apls'] = {'nui': 0, 'nbs': 0}
                if not 'apep' in txn_dict:
                    txn_dict['apep'] = 0
                if not 'apap' in txn_dict:
                    txn_dict['apap'] = ''
                if not 'apsu' in txn_dict:
                    txn_dict['apsu'] = ''
            return txn_dict

        result = []
        for txn_dict in txn_data:
            txn_dict_translated = _sort_txn_dict(_insert_defaults(txn_dict))
            result.append(txn_dict_translated)

        return result

    def dictify(self) -> Dict[str, Any]:
        return {"stages": self._stages}

    def to_json(self) -> str:
        return json.dumps(self.dictify())

    @staticmethod
    def from_json(scenario_json_str: str) -> 'KAVMScenario':
        parsed_scenario = json.loads(scenario_json_str)
        teal_files = set()

        stages = parsed_scenario['stages']

        try:
            stages[0]
        except KeyError as e:
            raise ValueError(f'Test scenario {scenario_json_str} does not condaint any stages') from e

        try:
            assert stages[0]['stage-type'] == 'setup-network'
        except (KeyError, AssertionError) as e:
            raise ValueError(
                f'Test scenario {scenario_json_str} does not contain a "setup-network" stage as the first stage'
            ) from e
        try:
            stages[0]['data']['accounts']
        except KeyError as e:
            raise ValueError(
                f'The "setup-network stage of test scenario {scenario_json_str} does not contain "accounts"'
            ) from e

        stages[0]['data']['accounts'] = KAVMScenario.sanitize_accounts(stages[0]['data']['accounts'])
        setup_network_stage = stages[0]
        for acc in setup_network_stage['data']['accounts']:
            for app in acc['created-apps']:
                teal_files.add(app['params']['approval-program'])
                teal_files.add(app['params']['clear-state-program'])

        try:
            assert stages[1]['stage-type'] == 'execute-transactions' and stages[1]['data']['transactions']
        except (KeyError, AssertionError) as e:
            raise ValueError(
                f'Test scenario {scenario_json_str} does not contain an "execute-transactions" stage as the second stage'
            ) from e
        stages[1]['data']['transactions'] = KAVMScenario.sanitize_transactions(stages[1]['data']['transactions'])
        execute_transactions_stage = stages[1]
        for txn in execute_transactions_stage['data']['transactions']:
            if 'apap' in txn:
                teal_files.add(txn['apap'])
            if 'apsu' in txn:
                teal_files.add(txn['apsu'])

        if len(stages) > 2:
            raise ValueError(f'Test scenario {scenario_json_str} contains more than two stages')

        return KAVMScenario(stages=stages, teal_files=teal_files)
