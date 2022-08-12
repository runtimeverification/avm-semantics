import subprocess
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Callable

from pyk.cli_utils import run_process
from pyk.kast import KApply, KInner
from pyk.kastManip import flatten_label, getCell
from pyk.ktool import KRun, paren
from pyk.prelude import intToken, stringToken

class KAVM(KRun):

    def __init__(self, definition_dir, use_directory=None):
        super().__init__(definition_dir, use_directory=use_directory)
        KAVM._patch_symbol_table(self.symbol_table)

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
