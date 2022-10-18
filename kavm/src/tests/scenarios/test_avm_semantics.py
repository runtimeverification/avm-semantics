import glob
import json
import os
from os.path import abspath
from pathlib import Path
from typing import cast

import pytest
from pyk.kast import KAst, KInner
from pyk.kastManip import split_config_from

from kavm.kavm import KAVM

project_path = abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def file_loop_index() -> list:

    filenames = []

    files = glob.glob(os.path.join(project_path, "tests/scenarios/*.avm-simulation"))
    files_passing = [os.path.basename(f) for f in files]
    for file in files_passing:
        return_code = int(file.split('.')[-2])
        filenames.append((file, return_code))
    return filenames


@pytest.mark.parametrize("filename, expected", file_loop_index())
def test_run_simulation(filename: str, expected: int) -> None:

    failing_file = open(os.path.join(project_path, 'tests/failing-avm-simulation.list'))
    failing_tests = [os.path.basename(f) for f in failing_file.read().split('\n')]
    if filename in failing_tests:
        pytest.skip()

    if not os.environ.get('KAVM_LIB'):
        raise RuntimeError('Cannot access KAVM_LIB environment variable. Is it set?')

    kavm = KAVM(definition_dir=Path(os.path.join(project_path, '.build/usr/lib/kavm/avm-llvm/avm-execution-kompiled/')))

    kavm_lib_dir = Path(str(os.environ.get('KAVM_LIB')))

    teal_programs_parser = project_path / kavm_lib_dir / 'scripts/parse-teal-programs.sh'
    avm_simulation_parser = project_path / kavm_lib_dir / 'scripts/parse-avm-simulation.sh'
    proc_result = kavm.run_avm_simulation(
        input_file=Path(os.path.join(project_path, 'tests/scenarios', filename)),
        output='json',
        profile=True,
        teal_sources_dir=Path(os.path.join(project_path, 'tests/teal-sources/')),
        teal_programs_parser=teal_programs_parser,
        avm_simulation_parser=avm_simulation_parser,
        depth=0,
        check=False,
    )

    expected_exit_code = 0 if expected == 0 else 3

    output_kast_term = KAst.from_dict(json.loads(proc_result.stdout)['term'])

    (_, subst) = split_config_from(cast(KInner, output_kast_term))

    panic_code = int(subst['PANICCODE_CELL'].token)

    assert panic_code == expected
    assert proc_result.returncode == expected_exit_code
