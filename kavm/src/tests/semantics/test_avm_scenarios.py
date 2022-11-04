import glob
import os
from os.path import abspath
from pathlib import Path

import pytest

from kavm.kavm import KAVM

project_path = abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def scenario_files() -> list:
    files = glob.glob(os.path.join(project_path, "tests/json-scenarios/*.json"))
    return files


@pytest.mark.parametrize("filename", scenario_files())
def test_run_simulation(filename: str) -> None:
    if not os.environ.get('KAVM_DEFINITION_DIR'):
        raise RuntimeError('Cannot access KAVM_DEFINITION_DIR environment variable. Is it set?')

    kavm_definition_dir = Path(str(os.environ.get('KAVM_DEFINITION_DIR')))

    kavm = KAVM(definition_dir=Path(os.path.join(project_path, str(kavm_definition_dir))), init_pyk=False)

    avm_json_parser = project_path / kavm_definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
    teal_parser = project_path / kavm_definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
    teal_programs_parser = project_path / kavm_definition_dir / 'parser_TealProgramsStore_TEAL-PARSER-SYNTAX'
    proc_result = kavm.run_avm_json(
        input_file=Path(filename),
        output='none',
        profile=True,
        teal_sources_dir=Path(os.path.join(project_path, 'tests/teal-sources/')),
        teal_programs_parser=teal_programs_parser,
        teal_parser=teal_parser,
        avm_json_parser=avm_json_parser,
        depth=0,
        check=False,
    )
    assert proc_result.returncode == 0
