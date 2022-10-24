import glob
import json
import sys
import os
from os.path import abspath
from pathlib import Path
from typing import cast

import pytest
from pyk.kast import KAst, KInner, KToken
from pyk.kastManip import split_config_from

from kavm.kavm import KAVM

project_path = abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


def file_loop_index() -> list:

    filenames = []

    files = glob.glob(os.path.join(project_path, "tests/scenarios/*.avm-simulation"))
    files_passing = [os.path.basename(f) for f in files]
    for file in files_passing:
        desc = file.split('.')[-2]
        if 'exit' in desc:
            panic_code = 0
            exit_code = int(desc[4:])
        else:
            panic_code = int(file.split('.')[-2])
            exit_code = 0 if panic_code == 0 else 3

        filenames.append((file, panic_code, exit_code))
    return filenames


@pytest.mark.parametrize(("filename", "expected_panic_code", "expected_exit_code"), file_loop_index())
def test_run_simulation(filename: str, expected_panic_code: int, expected_exit_code: int) -> None:

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

    # This is needed because long programs create deeply nested json objects
    sys.setrecursionlimit(12500)

    output_kast_term = KAst.from_dict(json.loads(proc_result.stdout)['term'])

    (_, subst) = split_config_from(cast(KInner, output_kast_term))

    panic_code = int(cast(KToken, subst['PANICCODE_CELL']).token)

    assert panic_code == expected_panic_code
    assert proc_result.returncode == expected_exit_code
