import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Callable, Dict, Final, Iterable, List, Optional, Tuple, Union

from kavm_algod.adaptors.account import KAVMAccount
from kavm_algod.adaptors.transaction import KAVMTransaction
from pyk.cli_utils import run_process
from pyk.kast import KApply, KAst, KInner, KLabel, KSort, KToken, Subst
from pyk.kastManip import collectFreeVars, inlineCellMaps
from pyk.ktool import KRun
from pyk.ktool.kprint import paren
from pyk.prelude import Sorts, build_assoc, buildCons, intToken, stringToken

_LOGGER: Final = logging.getLogger(__name__)


def add_include_arg(includes: List[str]) -> List[Any]:
    return [arg for include in includes for arg in ['-I', include]]


class KAVM(KRun):
    def __init__(
        self,
        definition_dir: Path,
        use_directory: Any = None,
        faucet: Optional[KAVMAccount] = None,
    ) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        KAVM._patch_symbol_table(self.symbol_table)
        self._current_config = self._empty_config
        self._faucet = faucet
        self._accounts: Dict[str, KAVMAccount] = {}

    @property
    def faucet(self) -> KAVMAccount:
        return self._faucet

    @faucet.setter
    def faucet(self, faucet: KAVMAccount) -> None:
        self._faucet = faucet

    @staticmethod
    def kompile(
        definition_dir: Path,
        main_file: Path,
        includes: List[str] = [],
        main_module_name: Optional[str] = None,
        syntax_module_name: Optional[str] = None,
        md_selector: Optional[str] = None,
        hook_namespaces: Optional[List[str]] = None,
        concrete_rules_file: Optional[Path] = None,
        verbose: bool = False,
    ) -> 'KAVM':
        command = [
            'kompile',
            '--output-definition',
            str(definition_dir),
            str(main_file),
        ]
        if verbose:
            command += ['--verbose']
        command += ['--emit-json', '--backend', 'llvm']
        command += ['--main-module', main_module_name] if main_module_name else []
        command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
        command += ['--md-selector', md_selector] if md_selector else []
        command += (
            ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
        )
        command += add_include_arg(includes)
        try:
            run_process(command, logger=_LOGGER)
        except CalledProcessError as err:
            sys.stderr.write(f'\nkompile stdout:\n{err.stdout}\n')
            sys.stderr.write(f'\nkompile stderr:\n{err.stderr}\n')
            sys.stderr.write(f'\nkompile returncode:\n{err.returncode}\n')
            sys.stderr.flush()
            raise
        return KAVM(definition_dir)

    @staticmethod
    def _patch_symbol_table(symbol_table: Dict[str, Callable[..., str]]) -> None:
        symbol_table['_+Int_'] = paren(symbol_table['_+Int_'])

    @property
    def _empty_config(self) -> KInner:
        """Return the KAST term for the empty generated top cell"""
        return self.definition.empty_config(KSort('GeneratedTopCell'))

    @property
    def current_config(self) -> KInner:
        """Return the current configuration KAST term"""
        return self._current_config

    @current_config.setter
    def current_config(self, new_config: KInner) -> None:
        self._current_config = new_config

    @staticmethod
    def accounts_cell(accts: List[KAVMAccount]) -> KInner:
        """Concatenate several accounts"""
        return build_assoc(
            KApply('.AccountCellMap'),
            KLabel('_AccountCellMap_'),
            [acc.account_cell for acc in accts],
        )

    @staticmethod
    def transactions_cell(txns: List[KAVMTransaction]) -> KInner:
        """Concatenate several transactions"""
        return build_assoc(
            KApply('.TransactionCellMap'),
            KLabel('_TransactionCellMap_'),
            [txn.transaction_cell for txn in txns],
        )

    def simulation_config(
        self,
        accounts: List[KAVMAccount],
        transactions: List[KAVMTransaction],
    ) -> KInner:
        """
        Create a configuration to be passed to krun with --term
        """
        txids = [txn.txid for txn in transactions]
        teal_cell_subst = Subst(
            {
                'PC_CELL': intToken(0),
                'PROGRAM_CELL': KApply('.Map'),
                'MODE_CELL': KToken('stateless', KSort('TealMode')),
                'VERSION_CELL': intToken(4),
                'STACK_CELL': KApply('.TStack'),
                'STACKSIZE_CELL': intToken(0),
                'JUMPED_CELL': KToken('false', KSort('Bool')),
                'LABELS_CELL': KApply('.Map'),
                'CALLSTACK_CELL': KApply('.List'),
                'SCRATCH_CELL': KApply('.Map'),
                'INTCBLOCK_CELL': KApply('.Map'),
                'BYTECBLOCK_CELL': KApply('.Map'),
            }
        )

        config = self._empty_config
        return teal_cell_subst.compose(
            Subst(
                {
                    'ACCOUNTSMAP_CELL': KAVM.accounts_cell(accounts),
                    'TRANSACTIONS_CELL': KAVM.transactions_cell(transactions),
                    'GROUPSIZE_CELL': intToken(len(transactions)),
                    'TXGROUPID_CELL': intToken(0),  # TODO: revise
                    # set the current TX to the first submitted txn
                    # TODO: the txn id must in fact be a str token, but we need to first change this in KAVM
                    'CURRENTTX_CELL': intToken(transactions[0].txid),
                    'RETURNCODE_CELL': intToken(4),
                    'RETURNSTATUS_CELL': stringToken('Failure - program is stuck'),
                    'GLOBALROUND_CELL': intToken(6),
                    'LATESTTIMESTAMP_CELL': intToken(50),
                    'CURRENTAPPLICATIONID_CELL': intToken(-1),
                    'CURRENTAPPLICATIONADDRESS_CELL': KToken('b""', KSort('Bytes')),
                    'APPCREATOR_CELL': KApply('.Map'),
                    'ASSETCREATOR_CELL': KApply('.Map'),
                    'EFFECTS_CELL': KApply('.List'),
                    'BLOCKS_CELL': KApply('.Map'),
                    'BLOCKHEIGHT_CELL': intToken(0),
                    'TEALPROGRAMS_CELL': KApply('.TealPrograms'),
                    'K_CELL': KApply(
                        '#evalTxGroup()_AVM-EXECUTION_AlgorandCommand',
                    ),
                    'DEQUE_CELL': buildCons(
                        KApply('.List'),
                        KLabel('_List_'),
                        [KApply(KLabel('ListItem'), intToken(x)) for x in txids],
                    ),
                    'DEQUEINDEXSET_CELL': buildCons(
                        KApply('.Set'),
                        KLabel('_Set_', KSort('Set')),
                        [KApply(KLabel('SetItem'), intToken(x)) for x in txids],
                    ),
                    'GENERATEDCOUNTER_CELL': intToken(0),
                    'NEXTAPPID_CELL': intToken(0),
                    'NEXTASSETID_CELL': intToken(0),
                }
            )
        ).apply(config)

    def run_with_current_config(self) -> Tuple[int, Union[KAst, str]]:
        """
        Run the AVM simulation from the configuration specified by self.current_config.

        If successful, put the resulting configuration as the new current config.
        """
        return self.run_term(self.current_config)

    def run_term(self, configuration: KInner) -> Tuple[int, Union[KAst, str]]:
        """
        Execute krun --term, passing the supplied configuration as a KORE term
        """
        freeVars = collectFreeVars(configuration)
        assert (
            len(freeVars) == 0
        ), f'Cannot run from current configuration due to unbound variables {freeVars}'
        with tempfile.NamedTemporaryFile(
            'w+t', delete=False
        ) as tmp_kast_json_file, tempfile.NamedTemporaryFile(
            'w+t', delete=False
        ) as tmp_kore_file:
            tmp_kast_json_file.write(
                json.dumps(
                    {'format': 'KAST', 'version': 2, 'term': configuration.to_dict()}
                )
            )

            kore_term = self.kast(
                input_file=Path(tmp_kast_json_file.name),
                module='AVM-EXECUTION',
                sort=KSort('GeneratedTopCell'),
            )
            tmp_kore_file.write(kore_term)

            krun_command = f'krun --definition {self.definition_dir} --output json --term --parser cat {tmp_kore_file.name}'

            env = os.environ.copy()
            env['KAVM_DEFITION_DIR'] = str(self.definition_dir)
            output = subprocess.run(
                krun_command, shell=True, capture_output=True, env=env
            )

            try:
                output_kast_term = KAst.from_dict(json.loads(output.stdout)['term'])
            except json.JSONDecodeError:
                return (
                    output.returncode,
                    output.stderr.decode(sys.getfilesystemencoding()),
                )

            return (output.returncode, inlineCellMaps(output_kast_term))

    def run_legacy(self, input_file: Path) -> Tuple[int, Union[KAst, str]]:
        """Run an AVM simulaion scenario with krun"""

        raw_avm_simulation = input_file.read_text()

        teal_paths = re.findall(r'declareTealSource "(.+?)";', raw_avm_simulation)

        teal_programs: str = ''
        for teal_path in teal_paths:
            teal_programs += f'{Path(teal_path).read_text()};'
        teal_programs += '.TealPrograms'

        krun_command = f'krun --definition {self.definition_dir} --output json \'-cTEAL_PROGRAMS={teal_programs}\' -pTEAL_PROGRAMS=lib/scripts/parse-teal-programs.sh --parser lib/scripts/parse-avm-simulation.sh {input_file}'

        env = os.environ.copy()
        env['KAVM_DEFITION_DIR'] = str(self.definition_dir)
        output = subprocess.run(krun_command, shell=True, capture_output=True, env=env)

        try:
            output_kast_term = KAst.from_dict(json.loads(output.stdout)['term'])
        except json.JSONDecodeError:
            return (
                output.returncode,
                output.stderr.decode(sys.getfilesystemencoding()),
            )

        return (output.returncode, inlineCellMaps(output_kast_term))

    def kast(
        self,
        input_file: Path,
        input: str = 'json',
        output: str = 'kore',
        module: str = 'AVM-EXECUTION',
        sort: KSort = Sorts.K,
        args: Iterable[str] = (),
    ) -> str:
        kast_command = ['kast', '--definition', str(self.definition_dir)]
        kast_command += ['--input', input, '--output', output]
        kast_command += ['--module', module]
        kast_command += ['--sort', sort.name]
        kast_command += [str(input_file)]
        command_env = os.environ.copy()
        command_env['KAVM_DEFITION_DIR'] = str(self.definition_dir)
        proc_result = run_process(kast_command, env=command_env, logger=_LOGGER)
        if proc_result.returncode != 0:
            raise RuntimeError(f'Calling kast failed: {kast_command}')
        return proc_result.stdout
