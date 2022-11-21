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

    failing_file = open(os.path.join(project_path, 'tests/failing-avm-simulation.list'))
    failing_tests = [os.path.basename(f) for f in failing_file.read().split('\n')]
    print(failing_tests)
    print(filename)
    if os.path.basename(filename) in failing_tests:
        pytest.skip()

    kavm_definition_dir = Path(str(os.environ.get('KAVM_DEFINITION_DIR')))

    kavm = KAVM(definition_dir=Path(os.path.join(project_path, str(kavm_definition_dir))))

    scenario = KAVMScenario.from_json(
        scenario_json_str=Path(filename).read_text(),
        teal_sources_dir=Path(os.path.join(project_path, 'tests/teal-sources/')),
    )

    kavm.run_avm_json(
        scenario=scenario,
        profile=True,
        depth=0,
    )
