import json
from base64 import b64decode
from hashlib import sha512
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from kavm.adaptors.algod_account import KAVMAccount
from kavm.adaptors.algod_application import KAVMApplication, KAVMApplicationParams
from kavm.constants import ZERO_ADDRESS


def _sort_dict(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    od = {}
    for k, v in sorted(input_dict.items()):
        if isinstance(v, Dict):
            od[k] = _sort_dict(v)
        od[k] = v
    return od


class KAVMScenario:
    """
    Rerpesentation of a JSON testing scenario for KAVM
    """

    def __init__(self, stages: List[Any], teal_programs: Dict[str, str]) -> None:
        self._stages = stages
        self._teal_programs = teal_programs

    @staticmethod
    def sanitize_accounts(accounts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Given a dictionary representing an Account, insert missing keys with default values"""
        result = []
        for acc_dict in accounts_data:
            acc_dict_translated = {KAVMAccount.inverted_attribute_map[k]: v for k, v in acc_dict.items()}
            acc = KAVMAccount(**acc_dict_translated).dictify()
            if not acc['auth-addr']:
                acc['auth-addr'] = ZERO_ADDRESS
            if not acc['created-apps']:
                acc['created-apps'] = []
            else:
                acc['created-apps'] = KAVMScenario.sanitize_apps(acc['created-apps'])
            if not acc['created-assets']:
                acc['created-assets'] = []
            if not acc['apps-local-state']:
                acc['apps-local-state'] = []
            if not acc['assets']:
                acc['assets'] = []
            result.append(acc)
        return result

    @staticmethod
    def sanitize_apps(apps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Given a dictionary representing an Applicaiton, insert missing keys with default values"""
        result = []
        for app_dict in apps_data:
            app_params_translated = {
                KAVMApplicationParams.inverted_attribute_map[k]: v for k, v in app_dict['params'].items()
            }
            app_params_dict = KAVMApplicationParams(**app_params_translated)
            app = KAVMApplication(id=app_dict['id'], params=app_params_dict).dictify()
            if not app['params']['global-state']:
                app['params']['global-state'] = []
            result.append(app)
        return result

    @staticmethod
    def sanitize_state_dict(state_dict: List[Dict[str, str | int]]) -> None:
        pass

    @staticmethod
    def sanitize_transactions(txn_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Given a dictionary representing a Transaction, insert missing keys with default values,
        and sort the keys in lexicographic order"""

        print("test")

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
            if not 'note' in txn_dict:
                txn_dict['note'] = ''
            if not 'rekey' in txn_dict:
                txn_dict['rekey'] = ZERO_ADDRESS
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
                    txn_dict['apgs'] = {
                        'nbs': 0,
                        'nui': 0,
                    }
                else:
                    if not 'nbs' in txn_dict['apgs']:
                        txn_dict['apgs']['nbs'] = 0
                    if not 'nui' in txn_dict['apgs']:
                        txn_dict['apgs']['nui'] = 0
                if not 'apls' in txn_dict:
                    txn_dict['apls'] = {
                        'nbs': 0,
                        'nui': 0,
                    }
                if not 'apep' in txn_dict:
                    txn_dict['apep'] = 0
                if not 'apap' in txn_dict:
                    txn_dict['apap'] = None
                if not 'apsu' in txn_dict:
                    txn_dict['apsu'] = None
                if not 'apbx' in txn_dict:
                    txn_dict['apbx'] = []
            if txn_dict['type'] == 'acfg':
                if not 'caid' in txn_dict:
                    txn_dict['caid'] = 0
                if not 'am' in txn_dict['apar']:
                    txn_dict['apar']['am'] = ''
                if not 'df' in txn_dict['apar']:
                    txn_dict['apar']['df'] = False
                if not 'm' in txn_dict['apar']:
                    txn_dict['apar']['m'] = txn_dict['apar']['c']
            if txn_dict['type'] == 'axfer':
                if not 'xaid' in txn_dict:
                    txn_dict['xaid'] = 0
                if not 'aamt' in txn_dict:
                    txn_dict['aamt'] = 0
                if not 'asnd' in txn_dict:
                    txn_dict['asnd'] = None
                if not 'arcv' in txn_dict:
                    txn_dict['arcv'] = None
                if not 'aclose' in txn_dict:
                    txn_dict['aclose'] = None
            return txn_dict

        result = []
        for txn_dict in txn_data:
            txn_dict_translated = _sort_dict(_insert_defaults(txn_dict))
            result.append(txn_dict_translated)

        return result

    def dictify(self) -> Dict[str, Any]:
        return {"stages": self._stages}

    def to_json(self, indent: int = 0) -> str:
        """
        Serialize the scenario to JSON with sorted keys
        """
        return json.dumps(self.dictify(), sort_keys=True, indent=indent)

    @staticmethod
    def from_json(
        scenario_json_str: str,
        teal_sources_dir: Optional[Path] = None,
        teal_decompiler: Optional[Callable[[str], str]] = None,
    ) -> 'KAVMScenario':
        """
        Parameters
        ----------
        scenario_json_str
            JSON-encoded string of a KAVM simulation scenario
        teal_sources_dir
            The directory to lookup TEAL progams in.
            Defults to the current directory if None is supplied.

        teal_decompiler
            The function to decompile a TEAL program.
            Defults to b64decode if None is supplied.
        """

        parsed_scenario = json.loads(scenario_json_str)
        teal_programs: Dict[str, str] = {}
        teal_sources_dir = teal_sources_dir if teal_sources_dir else Path('.')
        teal_decompiler = teal_decompiler if teal_decompiler else lambda src: b64decode(src).decode('ascii')

        def _extract_teal_program(teal_filename_or_src: str) -> Tuple[str, str]:
            if teal_filename_or_src.endswith('.teal'):
                assert teal_sources_dir
                teal_src = (teal_sources_dir / teal_filename_or_src).read_text()
                pgm_name = teal_filename_or_src
            else:
                assert teal_decompiler
                teal_src = teal_decompiler(teal_filename_or_src)
                pgm_name = sha512(teal_src.encode()).hexdigest() + '.teal'
            return (pgm_name, teal_src)

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
                        (pgm_name, pgm_src) = _extract_teal_program(app['params']['approval-program'])
                        teal_programs[pgm_name] = pgm_src
                        app['params']['approval-program'] = pgm_name
                    if app['params']['clear-state-program']:
                        (pgm_name, pgm_src) = _extract_teal_program(app['params']['clear-state-program'])
                        teal_programs[pgm_name] = pgm_src
                        app['params']['clear-state-program'] = pgm_name
        try:
            assert stages[1]['stage-type'] == 'submit-transactions' and stages[1]['data']['transactions']
        except (KeyError, AssertionError) as e:
            raise ValueError(
                f'Test scenario {scenario_json_str} does not contain an "submit-transactions" stage as the second stage'
            ) from e
        stages[1]['data']['transactions'] = KAVMScenario.sanitize_transactions(stages[1]['data']['transactions'])
        execute_transactions_stage = stages[1]
        for txn in execute_transactions_stage['data']['transactions']:
            if 'apap' in txn and txn['apap']:
                (pgm_name, pgm_src) = _extract_teal_program(txn['apap'])
                teal_programs[pgm_name] = pgm_src
                txn['apap'] = pgm_name
            if 'apsu' in txn and txn['apsu']:
                (pgm_name, pgm_src) = _extract_teal_program(txn['apsu'])
                teal_programs[pgm_name] = pgm_src
                txn['apsu'] = pgm_name

        if len(stages) > 2:
            raise ValueError(f'Test scenario {scenario_json_str} contains more than two stages')

        return KAVMScenario(stages=stages, teal_programs=teal_programs)
