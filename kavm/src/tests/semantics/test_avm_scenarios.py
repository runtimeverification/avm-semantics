import glob
import os
from os.path import abspath
from pathlib import Path

import pytest

from kavm.kavm import KAVM
from kavm.scenario import KAVMScenario

project_path = abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def scenario_files() -> list:
    files = glob.glob(os.path.join(project_path, "tests/json-scenarios/*.json"))
    return files


@pytest.mark.parametrize("filename", scenario_files())
def test_run_simulation(filename: str) -> None:
    if not os.environ.get('KAVM_DEFINITION_DIR'):
        raise RuntimeError('Cannot access KAVM_DEFINITION_DIR environment variable. Is it set?')

    kavm_definition_dir = Path(str(os.environ.get('KAVM_DEFINITION_DIR')))

    kavm = KAVM(definition_dir=Path(os.path.join(project_path, str(kavm_definition_dir))))

    scenario = KAVMScenario.from_json(Path(filename).read_text())

    teals = kavm.parse_teals(
        teal_paths=scenario._teal_files, teal_sources_dir=Path(os.path.join(project_path, 'tests/teal-sources/'))
    )
    proc_result = kavm.run_avm_json(
        scenario=scenario.to_json(),
        output='none',
        profile=True,
        teals=teals,
        depth=0,
    )

    assert proc_result.returncode == 0
