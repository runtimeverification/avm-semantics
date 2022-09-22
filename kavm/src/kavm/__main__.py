"""Command-line interface for KAVM"""

import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Final, List, Optional

from pyk.cli_utils import dir_path, file_path

from .kavm import KAVM

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def exec_kompile(
    definition_dir: Path,
    main_file: Path,
    main_module: Optional[str],
    syntax_module: Optional[str],
    includes: List[str],
    backend: Optional[str],
    verbose: bool,
    **kwargs: Any,
) -> None:
    proc_result = KAVM.kompile(
        definition_dir=definition_dir,
        main_file=main_file,
        main_module_name=main_module,
        syntax_module_name=syntax_module,
        includes=includes,
        backend=backend,
        verbose=True,
    )
    exit(proc_result.returncode)

def exec_prove(
    definition: Path,
    main_file: Path,
    **kwargs: Any,
) -> None:
    proc_result = KAVM.prove(
        definition,
        main_file,
    )
    exit(proc_result.returncode)

def exec_kast(
    definition_dir: Path,
    input_file: Path,
    output: str,
    **kwargs: Any,
) -> None:
    kavm = KAVM(definition_dir=definition_dir)

    # decide which sort to parse based on the file extension
    if input_file.suffix == '.avm-simulation':
        sort = 'AVMSimulation'
        module = 'AVM-EXECUTION'
    elif input_file.suffix == '.teal':
        sort = 'TealInputPgm'
        module = 'TEAL-PARSER-SYNTAX'
    elif input_file.suffix == '.teals':
        sort = 'TealPrograms'
        module = 'TEAL-PARSER-SYNTAX'
    else:
        raise RuntimeError(f'The input file {input_file} has an unrecognized extension')
    try:
        proc_result = kavm.kast(input_file=input_file, input='program', output=output, sort=sort, module=module)
        if output != 'none':
            print(proc_result.stdout)
        exit(proc_result.returncode)

    except CalledProcessError as err:
        print(err.stdout)
        exit(err.returncode)


def exec_run(
    definition_dir: Path,
    input_file: Path,
    teal_sources_dir: Path,
    teal_programs_parser: Path,
    avm_simulation_parser: Path,
    output: str,
    profile: bool,
    depth: Optional[int],
    **kwargs: Any,
) -> None:
    kavm = KAVM(definition_dir=definition_dir)

    if not os.environ.get('KAVM_LIB'):
        raise RuntimeError('Cannot access KAVM_LIB environment variable. Is it set?')
    kavm_lib_dir = Path(str(os.environ.get('KAVM_LIB')))

    if not teal_programs_parser:
        teal_programs_parser = kavm_lib_dir / 'scripts/parse-teal-programs.sh'
    if not avm_simulation_parser:
        avm_simulation_parser = kavm_lib_dir / 'scripts/parse-avm-simulation.sh'
    try:
        proc_result = kavm.run_avm_simulation(
            input_file=input_file,
            output=output,
            profile=profile,
            teal_sources_dir=teal_sources_dir,
            teal_programs_parser=teal_programs_parser,
            avm_simulation_parser=avm_simulation_parser,
            depth=depth,
        )
        print(proc_result.stdout)
        exit(proc_result.returncode)
    except CalledProcessError as err:
        print(err.stdout)
        exit(err.returncode)


def main() -> None:
    sys.setrecursionlimit(15000000)
    parser = create_argument_parser()
    args = parser.parse_args()
    logging.basicConfig(level=_loglevel(args), format=_LOG_FORMAT)

    if (not 'definition_dir' in vars(args)) or (not args.definition_dir):
        env_definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
        if env_definition_dir:
            args.definition_dir = Path(env_definition_dir)
        else:
            raise RuntimeError('Cannot find KAVM definition, plese specify either --definition or KAVM_DEFINITION_DIR')

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(**vars(args))


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kavm')

    shared_args = ArgumentParser(add_help=False)
    shared_args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
    shared_args.add_argument('--debug', default=False, action='store_true', help='Debug output.')
    shared_args.add_argument('--profile', default=False, action='store_true', help='Coarse process-level profiling.')

    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # kompile
    kompile_subparser = command_parser.add_parser('kompile', help='Kompile KAVM', parents=[shared_args])
    kompile_subparser.add_argument(
        '--definition-dir', dest='definition_dir', type=dir_path, help='Path to store the kompiled definition'
    )
    kompile_subparser.add_argument(
        '-I', type=str, dest='includes', default=[], action='append', help='Directories to lookup K definitions in.'
    )
    kompile_subparser.add_argument('main_file', type=file_path, help='Path to the main file')
    kompile_subparser.add_argument('--main-module', type=str)
    kompile_subparser.add_argument('--syntax-module', type=str)
    kompile_subparser.add_argument('--backend', type=str)

    # prove
    prove_subparser = command_parser.add_parser('prove', help='Prove claims', parents=[shared_args])
    prove_subparser.add_argument('main_file', type=file_path, help='Path to the main file')
    prove_subparser.add_argument('--definition', type=dir_path)

    # kast
    kast_subparser = command_parser.add_parser('kast', help='Kast a term', parents=[shared_args])
    kast_subparser.add_argument(
        '--definition',
        dest='definition_dir',
        type=dir_path,
        help='Path to definition to use.',
    )
    kast_subparser.add_argument(
        'input_file',
        type=file_path,
        help='Path to .avm-simulation, .teal or .teals file',
    )
    kast_subparser.add_argument(
        '--output',
        dest='output',
        type=str,
        help='Output mode',
        choices=['pretty', 'json', 'kore', 'kast', 'none'],
        required=True,
    )

    # run
    run_subparser = command_parser.add_parser('run', help='Run KAVM simulation', parents=[shared_args])
    run_subparser.add_argument(
        '--definition',
        dest='definition_dir',
        type=dir_path,
        help='Path to definition to use',
    )
    run_subparser.add_argument(
        'input_file',
        type=file_path,
        help='Path to AVM simulation scenario file',
    )
    run_subparser.add_argument(
        '--teal-sources-dir',
        dest='teal_sources_dir',
        type=dir_path,
        help='Path to directory containing .teal files used by the scenario',
        required=True,
    )
    run_subparser.add_argument(
        '--teal-programs-parser',
        dest='teal_programs_parser',
        type=file_path,
        help='Path to the executable to parse .teals files containing TealPrograms terms',
    )
    run_subparser.add_argument(
        '--avm-simulation-parser',
        dest='avm_simulation_parser',
        type=file_path,
        help='Path to the executable to parse .avm-simulation files containing AVMSimulation terms',
    )
    run_subparser.add_argument(
        '--output',
        dest='output',
        type=str,
        help='Output mode',
        choices=['pretty', 'json', 'kore', 'kast', 'none'],
        required=True,
    )
    run_subparser.add_argument(
        '--depth',
        dest='depth',
        type=int,
        help='Execute at most N rewrite steps',
    )

    return parser


def _loglevel(args: Namespace) -> int:
    if args.verbose or args.profile:
        return logging.INFO

    if args.debug:
        return logging.DEBUG

    return logging.WARNING


if __name__ == "__main__":
    main()
