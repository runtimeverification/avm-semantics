import glob
import os
import json
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

    kavm = KAVM(definition_dir=Path(os.path.join(project_path, str(kavm_definition_dir))))

    scenario = Path(filename).read_text()

    teals = kavm.extract_teals(
        scenario=scenario, teal_sources_dir=Path(os.path.join(project_path, 'tests/teal-sources/'))
    )
    proc_result = kavm.run_avm_json(
        scenario=scenario,
        output='none',
        profile=True,
        teals=teals,
        depth=0,
    )

    assert proc_result.returncode == 0
