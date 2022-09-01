"""Command-line interface for KAVM"""

import os
from argparse import ArgumentParser
from pathlib import Path
from subprocess import CalledProcessError

from pyk.cli_utils import dir_path

from .kavm import KAVM


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    if not args.definition_dir:
        env_definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
        if env_definition_dir:
            args.definition_dir = Path(env_definition_dir)
        else:
            raise RuntimeError('Cannot find KAVM definition, plese specify either --definition or KAVM_DEFINITION_DIR')

    if args.command == 'kompile':
        install_prefix = Path('.build').resolve() / 'usr'
        install_lib = install_prefix / 'lib/kavm'
        install_include = install_lib / 'include'
        plugin_include = install_lib / 'blockchain-k-plugin/include/'

        # try:
        proc_result = KAVM.kompile(
            definition_dir=args.definition_dir,
            main_file=args.main_file,
            main_module_name=args.main_module,
            syntax_module_name=args.syntax_module,
            includes=[f'{install_include}/kframework', f'{plugin_include}/kframework'],
            verbose=True,
        )
        exit(proc_result.returncode)
    if args.command == 'kast':
        kavm = KAVM(definition_dir=args.definition_dir)

        # decide which sort to parse based on the file extension
        if args.input_file.suffix == '.avm-simulation':
            sort = 'AVMSimulation'
            module = 'AVM-EXECUTION'
        elif args.input_file.suffix == '.teal':
            sort = 'TealInputPgm'
            module = 'TEAL-PARSER-SYNTAX'
        elif args.input_file.suffix == '.teals':
            sort = 'TealPrograms'
            module = 'TEAL-PARSER-SYNTAX'
        else:
            raise RuntimeError(f'The input file {args.input_file} has an unrecognized extension')
        try:
            proc_result = kavm.kast(
                input_file=args.input_file, input='program', output=args.output, sort=sort, module=module
            )
            if args.output != 'none':
                print(proc_result.stdout)
            exit(proc_result.returncode)

        except CalledProcessError as err:
            exit(err.returncode)

    if args.command == 'run':
        kavm = KAVM(definition_dir=args.definition_dir)

        if not os.environ.get('KAVM_LIB_ABS'):
            raise RuntimeError('Cannot access KAVM_LIB_ABS environment variable. Is it set?')
        kavm_lib_dir = Path(str(os.environ.get('KAVM_LIB_ABS')))

        if not args.teal_programs_parser:
            args.teal_programs_parser = kavm_lib_dir / 'scripts/parse-teal-programs.sh'
        if not args.avm_simulation_parser:
            args.avm_simulation_parser = kavm_lib_dir / 'scripts/parse-avm-simulation.sh'
        try:
            proc_result = kavm.run_avm_simulation(
                input_file=args.input_file,
                output=args.output,
                teal_sources_dir=args.teal_sources_dir,
                teal_programs_parser=args.teal_programs_parser,
                avm_simulation_parser=args.avm_simulation_parser,
            )
            if args.output != 'none':
                print(proc_result.stdout)
            exit(proc_result.returncode)
        except CalledProcessError as err:
            exit(err.returncode)
    else:
        raise NotImplementedError()


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kavm')
    command_parser = parser.add_subparsers(
        dest='command',
        required=True,
        help='Command to execute',
    )

    # kompile
    kompile_subparser = command_parser.add_parser('kompile', help='Kompile KAVM')
    kompile_subparser.add_argument(
        '--definition-dir', dest='definition_dir', type=Path, help='Path to store the kompiled definition'
    )
    kompile_subparser.add_argument('main_file', type=Path, help='Path to the main file')
    kompile_subparser.add_argument('--main-module', type=str)
    kompile_subparser.add_argument('--syntax-module', type=str)
    kompile_subparser.add_argument('--verbose', action='store_true')

    # kast
    kast_subparser = command_parser.add_parser('kast', help='Kast a term')
    kast_subparser.add_argument(
        '--definition',
        dest='definition_dir',
        type=Path,
        help='Path to definition to use.',
    )
    kast_subparser.add_argument(
        'input_file',
        type=Path,
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
    run_subparser = command_parser.add_parser('run', help='Run KAVM simulation')
    run_subparser.add_argument(
        '--definition',
        dest='definition_dir',
        type=dir_path,
        help='Path to definition to use',
    )
    run_subparser.add_argument(
        'input_file',
        type=Path,
        help='Path to AVM simulation scenario file',
    )
    run_subparser.add_argument(
        '--teal-sources-dir',
        dest='teal_sources_dir',
        type=Path,
        help='Path to directory containing .teal files used by the scenario',
        required=True,
    )
    run_subparser.add_argument(
        '--teal-programs-parser',
        dest='teal_programs_parser',
        type=Path,
        help='Path to the executable to parse .teals files containing TealPrograms terms',
    )
    run_subparser.add_argument(
        '--avm-simulation-parser',
        dest='avm_simulation_parser',
        type=Path,
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

    return parser


if __name__ == "__main__":
    main()
