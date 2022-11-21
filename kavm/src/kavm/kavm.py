import logging
import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, Final, Iterable, List, Optional, Union

from pyk.cli_utils import run_process
from pyk.kast.inner import KInner, KSort
from pyk.kore.parser import KoreParser
from pyk.kore.syntax import Pattern
from pyk.ktool.kprint import paren
from pyk.ktool.krun import KRun
from pyk.prelude.k import K

from kavm.scenario import KAVMScenario

_LOGGER: Final = logging.getLogger(__name__)


class KAVM(KRun):
    """
    Interact with the K semantics of AVM: evaluate Algorand transaction groups
    """

    def __init__(
        self,
        definition_dir: Path,
        use_directory: Any = None,
        teal_parser: Optional[Path] = None,
        scenario_parser: Optional[Path] = None,
    ) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        self._catcat_parser = definition_dir / 'catcat'
        self._teal_parser = teal_parser if teal_parser else definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
        self._scenario_parser = (
            scenario_parser if scenario_parser else definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
        )

    @staticmethod
    def prove(
        definition: Path,
        main_file: Path,
        debugger: bool,
        debug_script: Path,
    ) -> CompletedProcess:
        command = [
            'kprove',
            '--definition',
            str(definition),
            str(main_file),
        ]

        command += ['--debugger'] if debugger else []
        command += ['--debug-script', str(debug_script)] if debug_script else []

        return subprocess.run(command, check=True, text=True)

    # def extract_teals(self, scenario: str, teal_sources_dir: Path) -> str:
    #     """Extract TEAL programs filenames and source code from a test scenario"""
    #     parsed_scenario = json.loads(scenario)
    #     teal_paths = set()
    #     try:
    #         setup_network_stage = [
    #             stage for stage in parsed_scenario['stages'] if stage['stage-type'] == 'setup-network'
    #         ][0]
    #     except KeyError as e:
    #         raise ValueError(f'Test scenario {scenario} does not contain a "setup-network" stage') from e
    #     for acc in setup_network_stage['data']['accounts']:
    #         for app in acc['created-apps']:
    #             teal_paths.add(app['params']['approval-program'])
    #             teal_paths.add(app['params']['clear-state-program'])

    #     try:
    #         execute_transactions_stage = [
    #             stage for stage in parsed_scenario['stages'] if stage['stage-type'] == 'execute-transactions'
    #         ][0]
    #     except KeyError as e:
    #         raise ValueError(f'Test scenario {scenario} does not contain an "execute-transactions" stage') from e
    #     for txn in execute_transactions_stage['data']['transactions']:
    #         if 'apap' in txn:
    #             teal_paths.add(txn['apap'])
    #         if 'apsu' in txn:
    #             teal_paths.add(txn['apsu'])

    #     def run_process_on_bison_parser(path: Path) -> str:
    #         command = [self._teal_parser] + [str(path)]
    #         res = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)

    #         return res.stdout

    #     map_union_op = "Lbl'Unds'Map'Unds'{}"
    #     map_item_op = "Lbl'UndsPipe'-'-GT-Unds'{}"
    #     empty_map_label = "Lbl'Stop'Map{}()"
    #     current_teal_pgms_map = empty_map_label
    #     for teal_path in teal_paths:
    #         teal_path_parsed = 'inj{SortString{},SortKItem{}}(\\dv{SortString{}}("' + str(teal_path) + '"))'
    #         teal_parsed = (
    #             'inj{SortTealInputPgm{},SortKItem{}}(' + run_process_on_bison_parser(teal_sources_dir / teal_path) + ')'
    #         )
    #         teal_kore_map_item = map_item_op + '(' + teal_path_parsed + ',' + teal_parsed + ')'
    #         current_teal_pgms_map = map_union_op + "(" + current_teal_pgms_map + "," + teal_kore_map_item + ")"

    #     return current_teal_pgms_map

    def parse_teals(self, teal_paths: Iterable[str], teal_sources_dir: Path) -> Pattern:
        """Extract TEAL programs filenames and source code from a test scenario"""

        def run_process_on_bison_parser(path: Path) -> str:
            command = [self._teal_parser] + [str(path)]
            res = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)

            return res.stdout

        map_union_op = "Lbl'Unds'Map'Unds'{}"
        map_item_op = "Lbl'UndsPipe'-'-GT-Unds'{}"
        empty_map_label = "Lbl'Stop'Map{}()"
        current_teal_pgms_map = empty_map_label
        for teal_path in teal_paths:
            teal_path_parsed = 'inj{SortString{},SortKItem{}}(\\dv{SortString{}}("' + str(teal_path) + '"))'
            teal_parsed = (
                'inj{SortTealInputPgm{},SortKItem{}}(' + run_process_on_bison_parser(teal_sources_dir / teal_path) + ')'
            )
            teal_kore_map_item = map_item_op + '(' + teal_path_parsed + ',' + teal_parsed + ')'
            current_teal_pgms_map = map_union_op + "(" + current_teal_pgms_map + "," + teal_kore_map_item + ")"

        return KoreParser(current_teal_pgms_map).pattern()

    def run_avm_json(
        self,
        scenario: KAVMScenario,
        depth: Optional[int] = None,
        profile: bool = False,
        check: bool = True,
        existing_decompiled_teal_dir: Optional[Path] = None,
    ) -> KInner:
        """Run an AVM simulaion scenario with krun"""

        with tempfile.NamedTemporaryFile('w+t', delete=False) as tmp_scenario_file, (
            existing_decompiled_teal_dir if existing_decompiled_teal_dir else tempfile.TemporaryDirectory()  # type: ignore
        ) as decompiled_teal_dir:

            _LOGGER.info('Parsing TEAL_PROGRAMS')
            for teal_file, teal_src in scenario._teal_programs.items():
                (Path(decompiled_teal_dir) / teal_file).write_text(teal_src)
            parsed_teal = self.parse_teals(scenario._teal_programs.keys(), Path(decompiled_teal_dir))

            _LOGGER.info('Parsing PGM')
            tmp_scenario_file.write(scenario.to_json())
            tmp_scenario_file.flush()
            _pgm_parsed = run_process(
                [str(self._scenario_parser), str(tmp_scenario_file.name)], logger=_LOGGER, profile=profile
            )
            pgm_parsed = KoreParser(_pgm_parsed.stdout).pattern()

            # _LOGGER.warning(f'Executing scenario: {json.dumps(scenario.dictify(), indent=4, sort_keys=True)}')
            _LOGGER.info('Running KAVM')
            kore_config = {
                'TEAL_PROGRAMS': parsed_teal,
                'PGM': pgm_parsed,
            }
            os.environ['KAVM_DEFINITION_DIR'] = str(self.definition_dir)
            final_pattern = self.run_kore_config(kore_config, depth=depth, expand_macros=False)
            _LOGGER.info('Converting Kore => Kast')
            return self.kore_to_kast(final_pattern)

    def kast(
        self,
        input_file: Path,
        input: str = 'json',
        output: str = 'kore',
        module: str = 'AVM-EXECUTION',
        sort: Union[KSort, str] = K,
        args: Iterable[str] = (),
    ) -> CompletedProcess:
        kast_command = ['kast', '--definition', str(self.definition_dir)]
        kast_command += ['--input', input, '--output', output]
        kast_command += ['--module', module]
        kast_command += ['--sort', sort.name if isinstance(sort, KSort) else sort]
        kast_command += [str(input_file)]
        command_env = os.environ.copy()
        command_env['KAVM_DEFINITION_DIR'] = str(self.definition_dir)
        return run_process(kast_command, env=command_env, logger=_LOGGER, profile=True)

    def kast_expr(
        self,
        expr: str,
        input: str = 'json',
        output: str = 'kore',
        module: str = 'AVM-EXECUTION',
        sort: Union[KSort, str] = K,
        args: Iterable[str] = (),
    ) -> CompletedProcess:
        kast_command = ['kast', '--definition', str(self.definition_dir)]
        kast_command += ['--input', input, '--output', output]
        kast_command += ['--module', module]
        kast_command += ['--sort', sort.name if isinstance(sort, KSort) else sort]
        kast_command += ['--expression', expr]
        command_env = os.environ.copy()
        command_env['KAVM_DEFINITION_DIR'] = str(self.definition_dir)
        return run_process(kast_command, env=command_env, logger=_LOGGER, profile=True)

    @staticmethod
    def _patch_symbol_table(symbol_table: Dict[str, Callable[..., str]]) -> None:
        symbol_table['_+Int_'] = paren(symbol_table['_+Int_'])

    @staticmethod
    def concrete_rules() -> List[str]:
        return [
            'TEAL-TYPES.getAppAddressBytes',
        ]

    # @property
    # def _empty_config(self) -> KInner:
    #     """Return the KAST term for the empty generated top cell"""
    #     return self.definition.empty_config(KSort('GeneratedTopCell'))

    # @property
    # def current_config(self) -> KInner:
    #     """Return the current configuration KAST term"""
    #     return self._current_config

    # @current_config.setter
    # def current_config(self, new_config: KInner) -> None:
    #     self._current_config = new_config

    # def eval_transactions(self, txns: List[KAVMTransaction], new_addresses: Optional[Set[str]]) -> Any:
    #     """
    #     Evaluate a transaction group

    #     Parameters
    #     ----------
    #     txns
    #         transaction group
    #     new_addresses
    #         Algorand addresses discovered while pre-precessing the transactions in the KAVMClinet class

    #     Embed the group into the current configuration, and trigger its evaluation

    #     If the group is accepted, put resulting configuration as the new current, and roll back if regected.
    #     """

    #     if not new_addresses:
    #         new_addresses = set()

    #     # start tracking any newly discovered addresses with empty accounts
    #     for addr in new_addresses.difference(self.accounts.keys()):
    #         self.accounts[addr] = KAVMAccount(addr)

    #     self.current_config = self.simulation_config(txns)

    #     # construct the KAVM configuration and run it via krun
    #     try:
    #         (krun_return_code, output) = self._run_with_current_config()
    #     except Exception:
    #         _LOGGER.critical(
    #             f'Transaction group evaluation failed, last configuration was: {self.pretty_print(self._current_config)}'
    #         )
    #         raise
    #     if isinstance(output, KAst) and krun_return_code == 0:
    #         # Finilize successful evaluation
    #         self.current_config = cast(KInner, output)
    #         (_, subst) = carefully_split_config_from(cast(KInner, self.current_config), ignore_cells={'<transaction>'})
    #         # * update self.accounts with the new configuration cells
    #         modified_accounts = AccountCellMap(subst['ACCOUNTSMAP_CELL'])
    #         for address in self.accounts.keys():
    #             self.accounts[address] = modified_accounts[address]
    #             # * update self.apps with the new configuration cells
    #             for appid, app in self.accounts[address]._apps_created.items():
    #                 self.apps[appid] = app
    #         # * TODO: update self.assets with the new configuration cells
    #         # * save committed txns
    #         post_txns = TransactionCellMap(self, subst['TRANSACTIONS_CELL'])
    #         for txn in post_txns.values():
    #             self._committed_txns[txn.txid] = self._commit_transaction(txn)
    #         return {'txId': f'{txns[0].txid}'}
    #     else:
    #         _LOGGER.critical(output)
    #         exit(krun_return_code)
