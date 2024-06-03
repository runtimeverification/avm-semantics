import logging
import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from typing import Final, Iterable, List, Optional, Tuple, Union, cast

from pyk.kast.inner import KSort, KToken
from pyk.kast.manip import get_cell
from pyk.kast.pretty import SymbolTable, paren
from pyk.kore import syntax as kore
from pyk.kore.parser import KoreParser
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun, KRunOutput, _krun
from pyk.prelude.k import K
from pyk.utils import BugReport, run_process

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
        # verification_definition_dir: Optional[Path] = None,
        main_file: Optional[Path] = None,
        bug_report: Optional[BugReport] = None,
    ) -> None:
        self.backend = (definition_dir / 'backend.txt').read_text()

        if self.backend == 'haskell':
            KProve.__init__(
                self,
                definition_dir=definition_dir,
                use_directory=use_directory,
                main_file=main_file,
                patch_symbol_table=KAVM._kavm_patch_symbol_table,
            )
            self._verification_definition = definition_dir
        KRun.__init__(
            self,
            definition_dir,
            use_directory=use_directory,
            bug_report=bug_report,
            patch_symbol_table=KAVM._kavm_patch_symbol_table,
        )

        self._catcat_parser = definition_dir / 'catcat'
        self._teal_parser = teal_parser if teal_parser else definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
        self._scenario_parser = (
            scenario_parser if scenario_parser else definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
        )

    def parse_teal(self, file: Optional[Path]) -> kore.Pattern:
        '''Parse a TEAL program with the fast Bison parser'''
        if not (file):
            # return an error program
            return KoreParser(
                "inj{SortPseudoOpCode{}, SortTealInputPgm{}}(Lblint'UndsUnds'TEAL-OPCODES'Unds'PseudoOpCode'Unds'PseudoTUInt64{}(inj{SortInt{}, SortPseudoTUInt64{}}(\\dv{SortInt{}}(\"1\"))))"
            ).pattern()

        command = [str(self._teal_parser)] + [str(file)]
        result = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
        return KoreParser(result.stdout).pattern()

    def parse_teals(self, teal_paths: Iterable[str], teal_sources_dir: Path) -> kore.Pattern:
        """Parse several TEAL progams and combine them into a single Kore pattern"""

        map_union_op = "Lbl'Unds'Map'Unds'{}"
        map_item_op = "Lbl'UndsPipe'-'-GT-Unds'{}"
        empty_map_label = "Lbl'Stop'Map{}()"
        current_teal_pgms_map = empty_map_label
        for teal_path in teal_paths:
            teal_path_parsed = 'inj{SortString{},SortKItem{}}(\\dv{SortString{}}("' + str(teal_path) + '"))'
            teal_parsed = (
                'inj{SortTealInputPgm{},SortKItem{}}(' + self.parse_teal(teal_sources_dir / teal_path).text + ')'
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
        rerun_on_error: bool = False,
        output: str = "kore",
    ) -> Tuple[kore.Pattern, str]:
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

            _LOGGER.info(f'Writing scenario JSON to {tmp_scenario_file.name}')
            tmp_scenario_file.write(scenario.to_json())
            tmp_scenario_file.flush()
            _LOGGER.info('Running KAVM')
            os.environ['KAVM_DEFINITION_DIR'] = str(self.definition_dir)

            try:
                if output == "kore":
                    proc_result = _krun(
                        input_file=Path(tmp_scenario_file.name),
                        definition_dir=self.definition_dir,
                        output=KRunOutput.KORE,
                        depth=depth,
                        no_expand_macros=False,
                        check=check,
                        cmap={'TEAL_PROGRAMS': tmp_teals_file.name},
                        pmap={'TEAL_PROGRAMS': str(self._catcat_parser)},
                        pipe_stderr=True,
                    )
                    if proc_result.returncode != 0:
                        raise RuntimeError('Non-zero exit-code from krun.')

                    parser = KoreParser(proc_result.stdout)
                    final_pattern = parser.pattern()
                    assert parser.eof
                if output == "pretty":
                    proc_result = _krun(
                        input_file=Path(tmp_scenario_file.name),
                        definition_dir=self.definition_dir,
                        output=KRunOutput.PRETTY,
                        depth=depth,
                        no_expand_macros=False,
                        check=check,
                        cmap={'TEAL_PROGRAMS': tmp_teals_file.name},
                        pmap={'TEAL_PROGRAMS': str(self._catcat_parser)},
                        pipe_stderr=True,
                    )
                    if proc_result.returncode != 0:
                        raise RuntimeError('Non-zero exit-code from krun.')

                    final_pattern = proc_result.stdout

                return final_pattern, proc_result.stderr
            except RuntimeError as err:
                # if _krun has thtown a RuntimeError, rerun with --output pretty to see the final state quicker
                if rerun_on_error:
                    rerun_result = _krun(
                        input_file=Path(tmp_scenario_file.name),
                        definition_dir=self.definition_dir,
                        output=KRunOutput.PRETTY,
                        depth=depth,
                        no_expand_macros=False,
                        check=False,
                        cmap={'TEAL_PROGRAMS': tmp_teals_file.name},
                        pmap={'TEAL_PROGRAMS': str(self._catcat_parser)},
                        pipe_stderr=True,
                    )
                    raise RuntimeError(f'Final configuration was: {rerun_result.stdout}') from err
                # otherwise, try to establish the reason from the output Kore
                else:
                    parser = KoreParser(err.args[1])
                    final_pattern = parser.pattern()
                    returnstatus = cast(KToken, get_cell(self.kore_to_kast(final_pattern), 'RETURNSTATUS_CELL')).token
                    raise RuntimeError(returnstatus) from err

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
        return run_process(kast_command, env=command_env, logger=_LOGGER)

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
        return run_process(kast_command, env=command_env, logger=_LOGGER)

    @classmethod
    def _kavm_patch_symbol_table(cls, symbol_table: SymbolTable) -> None:
        symbol_table['_+Int_'] = paren(symbol_table['_+Int_'])
        symbol_table['_+Bytes_'] = paren(lambda a1, a2: a1 + '+Bytes' + a2)
        symbol_table['_Map_'] = paren(lambda m1, m2: m1 + '\n' + m2)

    @staticmethod
    def concrete_rules() -> List[str]:
        return []
