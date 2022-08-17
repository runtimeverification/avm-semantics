import json
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from pyk.cli_utils import dir_path, file_path
from pyk.kast import KAst
from pyk.kastManip import inlineCellMaps

from .kavm import KAVM


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()
    if not hasattr(args, 'definition_dir'):
        args.definition_dir = os.environ.get('KAVM_DEFINITION_DIR')

    if args.command == 'kompile':
        INSTALL_INCLUDE = '.build/usr/lib/kavm/include/'
        plugin_include = '.build/usr/lib/kavm/blockchain-k-plugin/include/'

        kavm = KAVM.kompile(
            definition_dir=args.directory,
            main_file=args.main_file,
            main_module_name=args.main_module,
            syntax_module_name=args.syntax_module,
            includes=[f'{INSTALL_INCLUDE}/kframework', f'{plugin_include}/kframework'],
            verbose=args.verbose,
        )
        return

    if args.command == 'run':
        kavm = KAVM(definition_dir=args.definition_dir)

        (krun_return_code, output) = kavm.run(args.input_file)
        if args.output != 'none':
            if isinstance(output, KAst):
                print(kavm.pretty_print(output))
            else:
                print(output)
        exit(krun_return_code)

    if args.command == 'llvm-krun':
        kavm = KAVM(definition_dir=args.definition_dir)

        parse_command = f'kavm kast {args.input_file} kore'
        output = subprocess.run(parse_command, shell=True, capture_output=True)

        avm_simulation_kore_term = output.stdout.decode('utf-8')

        (krun_return_code, output) = kavm.krun_kore(avm_simulation_kore_term)
        if args.output != 'none':
            if isinstance(output, KAst):
                print(kavm.pretty_print(output))
            else:
                print(output)
        exit(krun_return_code)

    else:
        assert False


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kavm-pyk')
    command_parser = parser.add_subparsers(dest='command', required=True)

    # kompile
    kompile_subparser = command_parser.add_parser('kompile', help='Kompile KAVM')
    kompile_subparser.add_argument(
        '--directory', type=dir_path, help='Path to definition to use.'
    )
    kompile_subparser.add_argument(
        'main_file', type=file_path, help='Path to the main file.'
    )
    kompile_subparser.add_argument('--main-module', type=str)
    kompile_subparser.add_argument('--syntax-module', type=str)
    kompile_subparser.add_argument('--verbose', action='store_true')

    # run
    run_subparser = command_parser.add_parser('run', help='Run KAVM simulation')
    run_subparser.add_argument(
        '--definition',
        dest="definition_dir",
        type=dir_path,
        help='Path to definition to use.',
    )
    run_subparser.add_argument(
        'input_file', type=file_path, help='Path to AVM simulation scenario file'
    )
    run_subparser.add_argument('--output', type=str, help='Output mode')

    # llvm-krun
    run_subparser = command_parser.add_parser('llvm-krun', help='Run KAVM simulation')
    run_subparser.add_argument(
        '--definition',
        dest="definition_dir",
        type=dir_path,
        help='Path to definition to use.',
    )
    run_subparser.add_argument(
        'input_file', type=file_path, help='Path to AVM simulation scenario file'
    )
    run_subparser.add_argument('--output', type=str, help='Output mode')

    return parser


if __name__ == "__main__":
    main()
