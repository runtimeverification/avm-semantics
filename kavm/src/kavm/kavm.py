import logging
import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from typing import Callable, Dict, Final, Iterable, List, Optional, Tuple, Union

from pyk.cli_utils import BugReport, run_process
from pyk.kast.inner import KInner, KSort
from pyk.kast.manip import minimize_term
from pyk.kore import syntax as kore
from pyk.kore.parser import KoreParser
from pyk.ktool.kprint import paren
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun, KRunOutput, _krun
from pyk.prelude.k import K

from kavm.pyk_utils import empty_cells_to_dots
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
        verification_definition_dir: Optional[Path] = None,
        main_file: Optional[Path] = None,
        bug_report: Optional[BugReport] = None,
    ) -> None:
        KRun.__init__(self, definition_dir, use_directory=use_directory, profile=profile, bug_report=bug_report)
        KProve.__init__(
            self,
            verification_definition_dir,
            use_directory=use_directory,
            main_file=main_file,
            profile=profile,
            bug_report=bug_report,
        ) if verification_definition_dir else None

        self._bool_parser = definition_dir / 'parser_Bool_AVM-TESTING-SYNTAX'
        self._catcat_parser = definition_dir / 'catcat'
        self._teal_parser = teal_parser if teal_parser else definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
        self._scenario_parser = (
            scenario_parser if scenario_parser else definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
        )
        self._verification_definition = verification_definition_dir

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
        check_return_code: bool = True,
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
                proc_result = _krun(
                    input_file=Path(tmp_scenario_file.name),
                    definition_dir=self.definition_dir,
                    output=KRunOutput.KORE,
                    depth=depth,
                    no_expand_macros=False,
                    profile=profile,
                    check=check,
                    cmap={'TEAL_PROGRAMS': tmp_teals_file.name, 'CHECK': str(check_return_code).lower()},
                    pmap={'TEAL_PROGRAMS': str(self._catcat_parser), 'CHECK': str(self._bool_parser)},
                    pipe_stderr=True,
                )
                if proc_result.returncode != 0:
                    raise RuntimeError('Non-zero exit-code from krun.')

                parser = KoreParser(proc_result.stdout)
                final_pattern = parser.pattern()
                assert parser.eof

                return final_pattern, proc_result.stderr
            except RuntimeError:
                raise

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
        symbol_table['_Map_'] = lambda m1, m2: m1 + '\n' + m2
        paren_symbols = [
            '#And',
            '_andBool_',
            '#Implies',
            '_impliesBool_',
            '_&Int_',
            '_*Int_',
            '_+Int_',
            '_-Int_',
            '_/Int_',
            '_|Int_',
            '_modInt_',
            'notBool_',
            '#Or',
            '_orBool_',
            '_Set_',
        ]
        for symb in paren_symbols:
            if symb in symbol_table:
                symbol_table[symb] = paren(symbol_table[symb])

    @staticmethod
    def concrete_rules() -> List[str]:
        return [
            'TEAL-TYPES.getAppAddressBytes',
        ]

    @staticmethod
    def reduce_config_for_pretty_printing(term: KInner) -> KInner:
        '''
        Omit various parts of the configuration that are irrelevant

        - Input: <generatedTop> cell term with full information
        - Output: <generatedTop> cell with the 'empty' or irrelevant cells collappsed

        This function is intended for pretty-printing only and is very opinionated
        '''
        labels_to_remove = [
            '<effects>',
            '<program>',
            '<firstValid>',
            '<lastValid>',
            '<genesisHash>',
            '<genesisID>',
            '<typeEnum>',
            '<lease>',
            '<note>',
            '<blocks>',
            '<blockheight>',
            '<globalRound>',
            '<latestTimestamp>',
            '<approvalProgramSrc>',
            '<approvalPgmSrc>',
            '<clearStateProgramSrc>',
            '<clearStatePgmSrc>',
            '<mode>',
            '<version>',
            '<stacksize>',
            '<dequeIndexSet>',
            '<round>',
            '<preRewards>',
            '<rewards>',
            '<status>',
            '<state-dumps>',
            '<tealPrograms>',
        ]
        empty_labels = [
            '.Map',
            '.AppCellMap',
            '.OptInAppCellMap',
            '.AssetCellMap',
            '.OptInAssetCellMap',
            '.BoxCellMap',
            '.TValueList',
            '.TValuePairList',
        ]
        reduced_term = minimize_term(empty_cells_to_dots(term, empty_labels), abstract_labels=labels_to_remove)
        return reduced_term
