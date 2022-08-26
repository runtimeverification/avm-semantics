import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from pyk.cli_utils import run_process
from pyk.kast import KApply, KAst, KInner, KLabel, KSort, KToken, Subst
from pyk.kastManip import free_vars, inline_cell_maps, split_config_from
from pyk.ktool import KRun
from pyk.ktool.kprint import paren
from pyk.prelude import Sorts, build_assoc, build_cons, intToken, stringToken

from kavm_algod import constants
from kavm_algod.adaptors.account import KAVMAccount
from kavm_algod.adaptors.transaction import KAVMTransaction

_LOGGER: Final = logging.getLogger(__name__)


def add_include_arg(includes: List[str]) -> List[Any]:
    return [arg for include in includes for arg in ['-I', include]]


class KAVM(KRun):
    """
    Interact with the K semantics of AVM: evaluate Algorand transaction groups
    """

    def __init__(
        self,
        definition_dir: Path,
        use_directory: Any = None,
        faucet_address: Optional[str] = None,
    ) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        KAVM._patch_symbol_table(self.symbol_table)
        self._accounts: Dict[str, KAVMAccount] = {}
        if faucet_address is not None:
            self._faucet = KAVMAccount(faucet_address, constants.FAUCET_ALGO_SUPPLY)
            # TODO: possible bug in pyk, if a Map cell only contains one item,
            #       split_config_from will recurse into the Map cell and substitute
            #       the item's cells with vars. Is that intended?
            self._accounts['dummy'] = KAVMAccount('dummy')
            self._accounts[faucet_address] = self._faucet
        self._current_config = self._initial_config()

    @property
    def accounts(self) -> Dict[str, KAVMAccount]:
        return self._accounts

    @property
    def faucet(self) -> KAVMAccount:
        return self._faucet

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
    def current_config(self) -> KAst:
        """Return the current configuration KAST term"""
        return self._current_config

    @current_config.setter
    def current_config(self, new_config: KAst) -> None:
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

    def eval_transactions(
        self, txns: List[KAVMTransaction], new_addresses: Set[str] = set()
    ) -> Any:
        """
        Evaluate a transaction group

        Parameters
        ----------
        txns
            transaction group
        new_accounts
            Algorand addresses discovered while pre-precessing the transactions in the KAVMClinet class

        Embed the group into the current configuration, and trigger its evaluation

        If the group is accepted, put resulting configuration as the new current, and roll back if regected.
        """

        pre_state = self.current_config

        # start tracking any newly discovered addresses with empty accounts
        for addr in new_addresses.difference(self.accounts.keys()):
            self.accounts[addr] = KAVMAccount(addr)

        self.current_config = self.simulation_config(txns)

        # construct the KAVM configuration and run it via krun
        (krun_return_code, output) = self._run_with_current_config()
        if isinstance(output, KAst) and krun_return_code == 0:
            # Finilize successful evaluation: self._current_config and self._accounts
            self.current_config = output
            # TODO: update self.accounts
            return {'txId': f'{txns[0].txid}'}
        else:
            exit(krun_return_code)

    def _initial_config(self) -> KAst:
        """
        Create the initial configuration term with cells containing defaults
        """
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
                    'ACCOUNTSMAP_CELL': KAVM.accounts_cell(
                        list(self.accounts.values())
                    ),
                    # 'ACCOUNTSMAP_CELL': KAVM.accounts_cell([]),
                    'TRANSACTIONS_CELL': KAVM.transactions_cell([]),
                    'GROUPSIZE_CELL': intToken(0),
                    'TXGROUPID_CELL': intToken(0),  # TODO: revise
                    # TODO: CURRENTTX_CELL should be of sort String in the semantics
                    'CURRENTTX_CELL': intToken(0),
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
                        '.AS_AVM-EXECUTION-SYNTAX_AVMSimulation',
                    ),
                    'DEQUE_CELL': build_cons(
                        KApply('.List'),
                        KLabel('_List_'),
                        [],
                    ),
                    'DEQUEINDEXSET_CELL': build_cons(
                        KApply('.Set'),
                        KLabel('_Set_', KSort('Set')),
                        [],
                    ),
                    'GENERATEDCOUNTER_CELL': intToken(0),
                    'NEXTAPPID_CELL': intToken(0),
                    'NEXTASSETID_CELL': intToken(0),
                }
            )
        ).apply(config)

    def simulation_config(
        self,
        transactions: List[KAVMTransaction],
    ) -> KAst:
        """
        Create a configuration to be passed to krun with --term
        """
        txids = [txn.txid for txn in transactions]

        (current_symbolic_config, current_subst) = split_config_from(
            self.current_config
        )

        txns_and_accounts_subst = Subst(
            {
                'ACCOUNTSMAP_CELL': KAVM.accounts_cell(list(self.accounts.values())),
                'TRANSACTIONS_CELL': KAVM.transactions_cell(transactions),
                'GROUPSIZE_CELL': intToken(len(transactions)),
                'TXGROUPID_CELL': intToken(0),  # TODO: revise
                'CURRENTTX_CELL': intToken(transactions[0].txid),
                'K_CELL': KApply(
                    '#evalTxGroup()_AVM-EXECUTION_AlgorandCommand',
                ),
                'DEQUE_CELL': build_cons(
                    KApply('.List'),
                    KLabel('_List_'),
                    [KApply(KLabel('ListItem'), intToken(x)) for x in txids],
                ),
                'DEQUEINDEXSET_CELL': build_cons(
                    KApply('.Set'),
                    KLabel('_Set_', KSort('Set')),
                    [KApply(KLabel('SetItem'), intToken(x)) for x in txids],
                ),
            }
        )

        return (
            Subst(current_subst)
            .compose(txns_and_accounts_subst)
            .apply(current_symbolic_config)
        )

    def _run_with_current_config(self) -> Tuple[int, Union[KAst, str]]:
        """
        Run the AVM simulation from the configuration specified by self.current_config.

        If successful, put the resulting configuration as the new current config.
        """
        return self.run_term(self.current_config)

    def run_term(self, configuration: KAst) -> Tuple[int, Union[KAst, str]]:
        """
        Execute krun --term, passing the supplied configuration as a KORE term
        """
        freeVars = free_vars(cast(KInner, configuration))
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

            return (output.returncode, inline_cell_maps(output_kast_term))

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

        return (output.returncode, inline_cell_maps(output_kast_term))

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
