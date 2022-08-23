import logging
import sys
from pathlib import Path
from subprocess import CalledProcessError
import subprocess
import os
import json
from typing import Any, Callable, Dict, Final, List, Optional, Union, Iterable
import re
import tempfile

from pyk.kast import KAst, KInner, KSort, Subst, KApply, KLabel, KToken
from pyk.kastManip import inlineCellMaps, collectFreeVars
from pyk.cli_utils import run_process
from pyk.ktool import KRun, paren
from pyk.prelude import intToken, stringToken, build_assoc, buildCons, Sorts

_LOGGER: Final = logging.getLogger(__name__)


def add_include_arg(includes: List[str]) -> List[Any]:
    return [arg for include in includes for arg in ['-I', include]]


class KAVM(KRun):
    def __init__(self, definition_dir: Path, use_directory: Any = None) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        KAVM._patch_symbol_table(self.symbol_table)
        self._current_config = self._empty_config

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
            run_process(command, _LOGGER)
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
        """Return the KAST term for the empty top-level KavmCell"""
        # return self.definition.empty_config(KSort('KavmCell'))
        return self.definition.empty_config(KSort('GeneratedTopCell'))

    @property
    def current_config(self) -> KInner:
        """Return the current configuration KAST term"""
        return self._current_config

    @current_config.setter
    def current_config(self, new_config: KInner) -> None:
        self._current_config = new_config

    def account(self, address: str, balance: int = 0) -> KInner:
        """
        Create an Algorand account cell.
        """
        from kavm_algod.pyk_utils import maybeTValue

        account_subcells_subst = Subst(
            {
                # 'ADDRESS_CELL': stringToken(address.strip("'")),
                # 'ADDRESS_CELL': KToken(address.strip('"'), KSort('Bytes')),
                # 'ADDRESS_CELL': KToken(address, KSort('Bytes')),
                'ADDRESS_CELL': maybeTValue(self, address),
                'BALANCE_CELL': intToken(balance),
                'MINBALANCE_CELL': intToken(100000),
                'ROUND_CELL': intToken(0),
                'PREREWARDS_CELL': intToken(0),
                'REWARDS_CELL': intToken(0),
                'STATUS_CELL': intToken(0),
                'KEY_CELL': maybeTValue(self, address),
                'APPSCREATED_CELL': KApply('.AppCellMap'),
                'APPSOPTEDIN_CELL': KApply('.OptInAppCellMap'),
                'ASSETSCREATED_CELL': KApply('.AssetCellMap'),
                'ASSETSOPTEDIN_CELL': KApply('.OptInAssetCellMap'),
            }
        )
        account_cell = account_subcells_subst.apply(
            self.definition.empty_config(KSort('AccountCell'))
        )
        return account_cell

    @staticmethod
    def accounts(accts: List[KInner]) -> KInner:
        """Concatenate several accounts"""
        return build_assoc(KApply('.AccountCellMap'), KLabel('_AccountCellMap_'), accts)

    @staticmethod
    def transactions(txns: List[KInner]) -> KInner:
        """Concatenate several transactions"""
        return build_assoc(
            KApply('.TransactionCellMap'), KLabel('_TransactionCellMap_'), txns
        )

    def simulation_config(
        self, accounts: List[KInner], transactions: List[KInner]
    ) -> KInner:
        """Create a configuration to be passed to krun with --term"""
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

        # ['RETURNCODE_CELL', 'RETURNSTATUS_CELL', 'GROUPSIZE_CELL', 'GLOBALROUND_CELL', 'LATESTTIMESTAMP_CELL', 'CURRENTAPPLICATIONID_CELL', 'CURRENTAPPLICATIONADDRESS_CELL',

        # , 'EFFECTS_CELL']

        config = self._empty_config
        return teal_cell_subst.compose(
            Subst(
                {
                    'ACCOUNTSMAP_CELL': KAVM.accounts(accounts),
                    'TRANSACTIONS_CELL': KAVM.transactions(transactions),
                    'GROUPSIZE_CELL': intToken(2),  # TODO: revise
                    'TXGROUPID_CELL': intToken(0),  # TODO: revise
                    'CURRENTTX_CELL': intToken(0),  # TODO: revise
                    'RETURNCODE_CELL': intToken(4),
                    'RETURNSTATUS_CELL': stringToken('Failure - program is stuck'),
                    'GLOBALROUND_CELL': intToken(6),
                    'LATESTTIMESTAMP_CELL': intToken(50),
                    'CURRENTAPPLICATIONID_CELL': intToken(0),
                    'CURRENTAPPLICATIONADDRESS_CELL': KToken('b""', KSort('Bytes')),
                    'APPCREATOR_CELL': KApply('.Map'),
                    'ASSETCREATOR_CELL': KApply('.Map'),
                    'EFFECTS_CELL': KApply('.List'),
                    'BLOCKS_CELL': KApply('.Map'),
                    'BLOCKHEIGHT_CELL': intToken(0),
                    'TEALPROGRAMS_CELL': KApply('.TealPrograms'),
                    # 'K_CELL': buildCons(
                    #     KToken(
                    #         '.AS_AVM-EXECUTION-SYNTAX_AVMSimulation',
                    #         KSort('AVMSimulation'),
                    #     ),
                    #     KLabel(
                    #         '_;__AVM-EXECUTION-SYNTAX_AVMSimulation_AlgorandCommand_AVMSimulation',
                    #         KSort('AVMSimulation'),
                    #     ),
                    #     [
                    #         # KLabel(
                    #         #     '#initTxGroup()_AVM-INITIALIZATION_AlgorandCommand',
                    #         #     KSort('AlgorandCommand'),
                    #         # ),
                    #         # KToken('#initGlobals()', KSort('AlgorandCommand')),
                    #         # KToken('#evalTxGroup()', KSort('AlgorandCommand')),
                    #         KToken('#evalTx()', KSort('AlgorandCommand')),
                    #         # KToken(
                    #         #     '.AS_AVM-EXECUTION-SYNTAX_AVMSimulation',
                    #         #     KSort('AVMSimulation'),
                    #         # ),
                    #     ],
                    # ),
                    'K_CELL': KApply(
                        '#evalTxGroup()_AVM-EXECUTION_AlgorandCommand',
                    ),
                    'DEQUE_CELL': buildCons(
                        KApply('.List'),
                        KLabel('_List_'),
                        [
                            KApply(KLabel('ListItem'), intToken(0)),
                            KApply(KLabel('ListItem'), intToken(1)),
                        ],
                    ),
                    # 'DEQUE_CELL': KApply('.List'),
                    'DEQUEINDEXSET_CELL': buildCons(
                        KApply('.Set'),
                        KLabel('_Set_', KSort('Set')),
                        [
                            KApply('SetItem', intToken(0)),
                            KApply('SetItem', intToken(1)),
                        ],
                    ),
                    # 'DEQUEINDEXSET_CELL': KApply('.Set'),
                    # 'DEQUEINDEXSET_CELL': KToken('.Set', KSort('Set')),
                    'GENERATEDCOUNTER_CELL': intToken(0),
                }
            )
        ).apply(config)

    # def run_with_current_config(self) -> (int, Union[KAst, str]):
    #     """
    #     Run the AVM simulation from the configuration specified by self.current_config.

    #     If successful, put the resulting configuration as the new current config.
    #     """

    #     freeVars = collectFreeVars(self.current_config)
    #     assert (
    #         len(freeVars) == 0
    #     ), f'Cannot run from current configuration due to unbound variables {freeVars}'

    def run_term(self, configuration: KInner) -> (int, Union[KAst, str]):
        # print(self.definition.modules)
        # print(self.definition.production_for_klabel('List'))
        # print(self.definition.syntax_productions)

        # assert False

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
                input_file=tmp_kast_json_file.name,
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

    def run(self, input_file: Path) -> (int, Union[KAst, str]):
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
