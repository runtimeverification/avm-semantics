import json
import logging
import os
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Callable, Dict, Final, Iterable, Optional, Union, List
import tempfile

from algosdk.future.transaction import Transaction
from pyk.cli_utils import run_process
from pyk.kast import KInner, KSort
from pyk.ktool.kprint import paren
from pyk.ktool.krun import KRun
from pyk.prelude.k import K
from pyk.prelude.kint import intToken

from kavm import constants
from kavm.adaptors.account import KAVMAccount
from kavm.adaptors.transaction import KAVMTransaction
from kavm.pyk_utils import AccountCellMap, AppCellMap

_LOGGER: Final = logging.getLogger(__name__)


class KAVM(KRun):
    """
    Interact with the K semantics of AVM: evaluate Algorand transaction groups
    """

    def __init__(
        self,
        definition_dir: Path,
        use_directory: Any = None,
        logger: Optional[logging.Logger] = None,
        init_pyk: bool = False,
        teals_parser: Optional[Path] = None,
        scenario_parser: Optional[Path] = None,
    ) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        if not logger:
            self._logger = _LOGGER
        else:
            self._logger = logger
        self._teals_parser = (
            teals_parser if teals_parser else definition_dir / 'parser_TealProgramsStore_TEAL-PARSER-SYNTAX'
        )
        self._scenario_parser = (
            scenario_parser if scenario_parser else definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
        )

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    # @property
    # def accounts(self) -> AccountCellMap:
    #     return self._accounts

    # @property
    # def next_valid_txid(self) -> str:
    #     """Return a txid consequative to the last commited one"""
    #     return str(int(sorted(self._committed_txns.keys())[-1]) + 1) if len(self._committed_txns) > 0 else str(0)

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

    @staticmethod
    def paste_teals(teals: Dict[str, str]) -> str:
        teal_programs: str = ''
        for k, v in teals.items():
            teal_programs += f'"{k}" |-> {v};'
        teal_programs += '.TealProgramsStore'
        return teal_programs

    @staticmethod
    def extract_teals(scenario: str, teal_sources_dir: Path) -> Dict[str, str]:
        """Extract TEAL programs filenames and source code from a test scenario"""
        parsed_scenario = json.loads(scenario)
        teal_paths = set()
        try:
            setup_network_stage = [
                stage for stage in parsed_scenario['stages'] if stage['stage-type'] == 'setup-network'
            ][0]
        except KeyError:
            print(f'Test scenario {scenario} does not contain a "setup-network" stage')
            exit(1)
        for acc in setup_network_stage['data']['accounts']:
            for app in acc['created-apps']:
                teal_paths.add(app['params']['approval-program'])
                teal_paths.add(app['params']['clear-state-program'])
        return {teal_path: (teal_sources_dir / teal_path).read_text() for teal_path in teal_paths}

    def run_avm_json(
        self,
        scenario: str,
        teals: str,
        depth: Optional[int],
        output: str = 'none',
        profile: bool = False,
        check: bool = True,
    ) -> CompletedProcess:
        """Run an AVM simulaion scenario with krun"""

        with tempfile.NamedTemporaryFile('w+t', delete=False) as tmp_scenario_file, tempfile.NamedTemporaryFile(
            'w+t', delete=False
        ) as tmp_teals_file:
            tmp_scenario_file.write(scenario)
            tmp_scenario_file.seek(0)
            tmp_teals_file.write(teals)

            krun_command = ['krun', '--definition', str(self.definition_dir)]
            krun_command += ['--output', output]
            krun_command += [f'-cTEAL_PROGRAMS={teals}']
            krun_command += [f'-pTEAL_PROGRAMS={str(self._teals_parser)}']
            krun_command += ['--parser', str(self._scenario_parser)]
            krun_command += ['--depth', str(depth)] if depth else []
            krun_command += [tmp_scenario_file.name]
            command_env = os.environ.copy()
            command_env['KAVM_DEFINITION_DIR'] = str(self.definition_dir)

            return run_process(krun_command, env=command_env, logger=self._logger, profile=profile, check=check)

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
        return run_process(kast_command, env=command_env, logger=self._logger, profile=True)

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
        return run_process(kast_command, env=command_env, logger=self._logger, profile=True)

    @staticmethod
    def _patch_symbol_table(symbol_table: Dict[str, Callable[..., str]]) -> None:
        symbol_table['_+Int_'] = paren(symbol_table['_+Int_'])

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
    #         self.logger.critical(
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
    #         self.logger.critical(output)
    #         exit(krun_return_code)
