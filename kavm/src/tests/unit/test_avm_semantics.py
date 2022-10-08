from typing import Any

import pytest
import glob
from pyk.kast import KApply, KInner, KSort, KToken
from pyk.prelude import intToken, stringToken
import os
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess

from kavm.pyk_utils import maybe_tvalue, split_direct_subcells_from
from kavm.kavm import KAVM

def file_loop_index() -> list:
    filenames = []
    failing_file = open('../tests/failing-avm-simulation.list')
    failing_tests = ['../' + filename for filename in failing_file.read().split('\n')]
    print(failing_tests)
    files = glob.glob("../tests/scenarios/*.avm-simulation")
    files_passing = list(filter(None, [file if (file not in failing_tests) else None for file in files]))
    for file in files_passing:
        return_code = 0
        if file.__contains__('.fail.'): return_code = 3
        filenames.append(tuple((file, return_code)))
    return filenames

@pytest.mark.parametrize("filename, expected", file_loop_index())
def test_run_simulation(filename: str, expected: int) -> None:
    if not os.environ.get('KAVM_LIB'):
        raise RuntimeError('Cannot access KAVM_LIB environment variable. Is it set?')

    kavm = KAVM(definition_dir='.build/usr/lib/kavm/avm-llvm/avm-execution-kompiled/')

    kavm_lib_dir = Path(str(os.environ.get('KAVM_LIB')))

    teal_programs_parser = kavm_lib_dir / 'scripts/parse-teal-programs.sh'
    avm_simulation_parser = kavm_lib_dir / 'scripts/parse-avm-simulation.sh'
    proc_result = kavm.run_avm_simulation(
        input_file=Path(filename),
        output='pretty',
        profile=True,
        teal_sources_dir=Path('../tests/teal-sources/'),
        teal_programs_parser=teal_programs_parser,
        avm_simulation_parser=avm_simulation_parser,
        depth=0,
        check=False,
    )
    print(proc_result.stdout)

    assert proc_result.returncode == expected
