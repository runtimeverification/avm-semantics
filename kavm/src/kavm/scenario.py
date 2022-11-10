import json
from collections import OrderedDict
from typing import Any, Dict, List, Set

from kavm.adaptors.algod_account import KAVMAccount
from kavm.adaptors.algod_application import KAVMApplication, KAVMApplicationParams


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
            acc = KAVMAccount(**acc_dict_translated).dictify()
            if not acc['created-apps']:
                acc['created-apps'] = []
            else:
                acc['created-apps'] = KAVMScenario.sanitize_apps(acc['created-apps'])
            if not acc['created-assets']:
                acc['created-assets'] = []
            result.append(acc)
        return result

    @staticmethod
    def sanitize_apps(apps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for app_dict in apps_data:
            app_params_translated = {
                KAVMApplicationParams.inverted_attribute_map[k]: v for k, v in app_dict['params'].items()
            }
            app_params_dict = KAVMApplicationParams(**app_params_translated)
            app = KAVMApplication(id=app_dict['id'], params=app_params_dict).dictify()
            result.append(app)
        return result

    @staticmethod
    def sanitize_transactions(txn_data: List[Dict[str, Any]]) -> List[OrderedDict[str, Any]]:
        def _sort_txn_dict(txn_dict: Dict[str, Any]) -> OrderedDict[str, Any]:
            od = OrderedDict()
            for k, v in sorted(txn_dict.items()):
                if isinstance(v, dict):
                    od[k] = _sort_txn_dict(v)
                od[k] = v
            return od

        def _insert_defaults(txn_dict: Dict[str, Any]) -> Dict[str, Any]:
            if not 'fv' in txn_dict:
                txn_dict['fv'] = 1
            if not 'lv' in txn_dict:
                txn_dict['lv'] = 1001
            if not 'gen' in txn_dict:
                txn_dict['gen'] = 'kteal'
            if not 'gh' in txn_dict:
                txn_dict['gh'] = 'kteal'
            if not 'fee' in txn_dict:
                txn_dict['fee'] = 1000
            if not 'grp' in txn_dict:
                txn_dict['grp'] = 'dummy_grp'
            if txn_dict['type'] == 'appl':
                if not 'apaa' in txn_dict:
                    txn_dict['apaa'] = []
                if not 'apid' in txn_dict:
                    txn_dict['apid'] = 0
                if not 'apan' in txn_dict or txn_dict['apan'] is None:
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
                    txn_dict['apap'] = None
                if not 'apsu' in txn_dict:
                    txn_dict['apsu'] = None
                if not 'apbx' in txn_dict:
                    txn_dict['apbx'] = []
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
            raise ValueError(f'Test scenario {scenario_json_str} does not contain any stages') from e

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
            if acc and 'created-apps' in acc and acc['created-apps']:
                for app in acc['created-apps']:
                    if app['params']['approval-program']:
                        teal_files.add(app['params']['approval-program'])
                    if app['params']['clear-state-program']:
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
            if 'apap' in txn and txn['apap']:
                teal_files.add(txn['apap'])
            if 'apsu' in txn and txn['apsu']:
                teal_files.add(txn['apsu'])

        if len(stages) > 2:
            raise ValueError(f'Test scenario {scenario_json_str} contains more than two stages')

        return KAVMScenario(stages=stages, teal_files=teal_files)
