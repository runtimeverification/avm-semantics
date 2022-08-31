import logging
import os
import re
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Final, Iterable, List, Optional, Union

from pyk.cli_utils import run_process
from pyk.kast import KSort
from pyk.ktool import KRun
from pyk.prelude import Sorts

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
    ) -> None:
        super().__init__(definition_dir, use_directory=use_directory)
        if not logger:
            self._logger = _LOGGER
        else:
            self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @staticmethod
    def kompile(
        definition_dir: Path,
        main_file: Path,
        includes: Optional[List[str]] = None,
        main_module_name: Optional[str] = None,
        syntax_module_name: Optional[str] = None,
        md_selector: Optional[str] = None,
        hook_namespaces: Optional[List[str]] = None,
        concrete_rules_file: Optional[Path] = None,
        verbose: bool = True,
    ) -> CompletedProcess:
        command = [
            'kompile',
            '--output-definition',
            str(definition_dir),
            str(main_file),
        ]

        command += ['--verbose']
        command += ['--emit-json', '--backend', 'llvm']
        command += ['--main-module', main_module_name] if main_module_name else []
        command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
        command += ['--md-selector', md_selector] if md_selector else []
        command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
        command += [arg for include in includes for arg in ['-I', include]] if includes else []

        return subprocess.run(command, check=True, text=True)

    def run_avm_simulation(
        self,
        input_file: Path,
        teal_programs_parser: Path,
        avm_simulation_parser: Path,
        output: str = 'json',
        teal_sources_dir: Optional[Path] = None,
    ) -> CompletedProcess:
        """Run an AVM simulaion scenario with krun"""

        if not teal_sources_dir:
            teal_sources_dir = Path()

        raw_avm_simulation = input_file.read_text()

        teal_paths = re.findall(r'declareTealSource "(.+?)";', raw_avm_simulation)

        teal_programs: str = ''
        for teal_path in teal_paths:
            teal_programs += f'{(teal_sources_dir / teal_path).read_text()};'
        teal_programs += '.TealPrograms'

        krun_command = ['krun', '--definition', str(self.definition_dir)]
        krun_command += ['--output', output]
        krun_command += [f'-cTEAL_PROGRAMS={teal_programs}']
        krun_command += [f'-pTEAL_PROGRAMS={str(teal_programs_parser)}']
        krun_command += ['--parser', str(avm_simulation_parser)]
        krun_command += [str(input_file)]
        command_env = os.environ.copy()
        command_env['KAVM_DEFINITION_DIR'] = str(self.definition_dir)

        return run_process(krun_command, env=command_env, logger=self._logger, profile=True)

    def kast(
        self,
        input_file: Path,
        input: str = 'json',
        output: str = 'kore',
        module: str = 'AVM-EXECUTION',
        sort: Union[KSort, str] = Sorts.K,
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
