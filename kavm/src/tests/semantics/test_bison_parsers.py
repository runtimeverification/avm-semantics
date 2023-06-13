import glob
import os
from os.path import abspath
from pathlib import Path

import pytest
from pyk.utils import run_process

project_path = abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def teal_files() -> list:
    files = glob.glob(os.path.join(project_path, "tests/teal-sources/*.teal"))
    return files


@pytest.mark.parametrize("filename", teal_files())
def test_teal_parser(filename: str) -> None:
    if not os.environ.get('KAVM_DEFINITION_DIR'):
        raise RuntimeError('Cannot access KAVM_DEFINITION_DIR environment variable. Is it set?')

    kavm_definition_dir = Path(str(os.environ.get('KAVM_DEFINITION_DIR')))

    teal_parser = project_path / kavm_definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
    command = [str(teal_parser), filename]
    proc_result = run_process(command)
    assert proc_result.returncode == 0


def avm_json_files() -> list:
    files = glob.glob(os.path.join(project_path, "tests/json-scenarios/*.json"))
    return files


@pytest.mark.parametrize("filename", avm_json_files())
def test_avm_json_parser(filename: str) -> None:
    if not os.environ.get('KAVM_DEFINITION_DIR'):
        raise RuntimeError('Cannot access KAVM_DEFINITION_DIR environment variable. Is it set?')

    kavm_definition_dir = Path(str(os.environ.get('KAVM_DEFINITION_DIR')))

    avm_json_parser = project_path / kavm_definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
    command = [str(avm_json_parser), filename]
    proc_result = run_process(command)
    assert proc_result.returncode == 0
