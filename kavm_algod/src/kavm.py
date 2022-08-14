import logging
import sys
from subprocess import CalledProcessError
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Callable

from pyk.cli_utils import run_process
from pyk.kast import KApply, KInner
from pyk.kastManip import flatten_label, getCell
from pyk.ktool import KRun, paren
from pyk.prelude import intToken, stringToken

_LOGGER: Final = logging.getLogger(__name__)


def add_include_arg(includes):
    return [arg for include in includes for arg in ['-I', include]]


class KAVM(KRun):
    def __init__(self, definition_dir, use_directory=None):
        super().__init__(definition_dir, use_directory=use_directory)
        KAVM._patch_symbol_table(self.symbol_table)

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

    def parse_avm_simulation(self, scenario_file: Path):
        kast_command = f'kast --sort AVMSimulation --definition {self.definition_dir} --module AVM-EXECUTION {scenario_file} --output KORE'
        return subprocess.run(kast_command, shell=True, capture_output=True).stdout

    def parse_teal_programs(self, teal_program_files: List[Path]):
        teal_programs: str = ''
        for teal_path in teal_program_files:
            teal_programs += f'{Path(teal_path).read_text()};'
        teal_programs += '.TealPrograms'
        teal_programs = f'\'{teal_programs}\''

        kast_command = f'kast --sort TealPrograms --definition {self.definition_dir} --module TEAL-PARSER-SYNTAX --output KORE --expression {teal_programs}'
        return subprocess.run(kast_command, shell=True, capture_output=True).stdout
