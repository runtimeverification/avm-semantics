import logging
import os
import subprocess
import tempfile
import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Callable, Dict, Final, Iterable, List, Optional, Tuple, Union

from pyk.cli_utils import run_process
from pyk.utils import unique
from pyk.kast.inner import KSort, KInner
from pyk.kore.parser import KoreParser
from pyk.kore.syntax import Pattern
from pyk.ktool.kprint import paren
from pyk.ktool.kprove import KProve, KoreExecLogFormat, _kprove, KProveOutput, _get_rule_log
from pyk.ktool.krun import KRun, KRunOutput, _krun
from pyk.prelude.k import K
from pyk.prelude.ml import is_top

from kavm.scenario import KAVMScenario

_LOGGER: Final = logging.getLogger(__name__)


class KAVM(KRun, KProve):
    """
    Interact with the K semantics of AVM: evaluate Algorand transaction groups
    """

    def __init__(
        self,
        definition_dir: Path,
        use_directory: Optional[Path] = None,
        teal_parser: Optional[Path] = None,
        scenario_parser: Optional[Path] = None,
        profile: bool = False,
        definition: Optional[Path] = None,
        main_file: Optional[Path] = None,
    ) -> None:
        KRun.__init__(self, definition_dir, use_directory=use_directory, profile=profile)
        KProve.__init__(
            self, definition, use_directory=use_directory, main_file=main_file, profile=profile
        ) if definition else None

        self._catcat_parser = definition_dir / 'catcat'
        self._teal_parser = teal_parser if teal_parser else definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
        self._scenario_parser = (
            scenario_parser if scenario_parser else definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
        )


    def prove(
        self,
        spec_file: Path,
        spec_module_name: Optional[str] = None,
        args: Iterable[str] = (),
        haskell_args: Iterable[str] = (),
        haskell_log_entries: Iterable[str] = (),
        log_axioms_file: Optional[Path] = None,
        allow_zero_step: bool = False,
        dry_run: bool = False,
        depth: Optional[int] = None,
        haskell_log_format: KoreExecLogFormat = KoreExecLogFormat.ONELINE,
        haskell_log_debug_transition: bool = True,
    ) -> KInner:
        log_file = spec_file.with_suffix('.debug-log') if log_axioms_file is None else log_axioms_file
        if log_file.exists():
            log_file.unlink()
        haskell_log_entries = unique(
            list(haskell_log_entries) + (['DebugTransition'] if haskell_log_debug_transition else [])
        )
        haskell_log_args = [
            '--log',
            str(log_file),
            '--log-format',
            haskell_log_format.value,
            '--log-entries',
            ','.join(haskell_log_entries),
        ]

        kore_exec_opts = ' '.join(list(haskell_args) + haskell_log_args)
        _LOGGER.debug(f'export KORE_EXEC_OPTS="{kore_exec_opts}"')
        env = os.environ.copy()
        env['KORE_EXEC_OPTS'] = kore_exec_opts

        proc_result = _kprove(
            spec_file=spec_file,
            command=self.prover,
            kompiled_dir=self.definition_dir,
            spec_module_name=spec_module_name,
            output=KProveOutput.JSON,
            dry_run=dry_run,
            args=self.prover_args + list(args),
            env=env,
            check=False,
            profile=self._profile,
            depth=depth,
        )

        final_state = KInner.from_dict(json.loads(proc_result.stdout)['term'])
        print(proc_result)
        print(self.pretty_print(final_state) + '\n')

        if proc_result.returncode not in (0, 1):
            raise RuntimeError('kprove failed!')

        if dry_run:
            return mlBottom()

        debug_log = _get_rule_log(log_file)
        if is_top(final_state) and len(debug_log) == 0 and not allow_zero_step:
            raise ValueError(f'Proof took zero steps, likely the LHS is invalid: {spec_file}')
        return final_state

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
    ) -> Tuple[Pattern, str, int]:
        """Run an AVM simulaion scenario with krun"""

        with tempfile.NamedTemporaryFile('w+t', delete=False) as tmp_scenario_file, (
            existing_decompiled_teal_dir if existing_decompiled_teal_dir else tempfile.TemporaryDirectory()  # type: ignore
        ) as decompiled_teal_dir, tempfile.NamedTemporaryFile('w+t', delete=False) as tmp_teals_file:

            _LOGGER.info('Parsing TEAL_PROGRAMS')
            for teal_file, teal_src in scenario._teal_programs.items():
                (Path(decompiled_teal_dir) / teal_file).write_text(teal_src)
            parsed_teal = self.parse_teals(scenario._teal_programs.keys(), Path(decompiled_teal_dir))
            tmp_teals_file.write(parsed_teal.text)
            tmp_teals_file.flush()

            _LOGGER.info('Parsing PGM')
            tmp_scenario_file.write(scenario.to_json())
            tmp_scenario_file.flush()
            _LOGGER.info('Running KAVM')
            os.environ['KAVM_DEFINITION_DIR'] = str(self.definition_dir)

            proc_result = _krun(
                input_file=Path(tmp_scenario_file.name),
                definition_dir=self.definition_dir,
                output=KRunOutput.KORE,
                depth=depth,
                no_expand_macros=False,
                profile=profile,
                check=check,
                cmap={'TEAL_PROGRAMS': tmp_teals_file.name},
                pmap={'TEAL_PROGRAMS': str(self._catcat_parser)},
                pipe_stderr=True,
            )

            parser = KoreParser(proc_result.stdout)
            final_pattern = parser.pattern()
            assert parser.eof

            return final_pattern, proc_result.stderr, proc_result.returncode

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
