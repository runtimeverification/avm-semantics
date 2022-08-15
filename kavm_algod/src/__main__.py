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
        # TEAL source code is fetched from .teal files in ./tests/teal/
        # by scanning the test scenario "${run_file}" for "declareTealSource <path>" commands
        raw_avm_simulation = args.input_file.read_text()
        teal_paths = re.findall(r'declareTealSource "(.+?)";', raw_avm_simulation)

        teal_programs: str = ''
        for teal_path in teal_paths:
            teal_programs += f'{Path(teal_path).read_text()};'
        teal_programs += '.TealPrograms'

        krun_command = f'krun --definition {kavm.definition_dir} --output json \'-cTEAL_PROGRAMS={teal_programs}\' -pTEAL_PROGRAMS=lib/scripts/parse-teal-programs.sh --parser lib/scripts/parse-avm-simulation.sh {args.input_file}'

        env = os.environ.copy()
        env['KAVM_DEFITION_DIR'] = str(kavm.definition_dir)
        output = subprocess.run(krun_command, shell=True, capture_output=True, env=env)

        try:
            output_kast_term = KAst.from_dict(json.loads(output.stdout)['term'])
        except json.JSONDecodeError:
            print(output.stderr.decode(sys.getfilesystemencoding()))
            exit(output.returncode)
        if args.output != 'none':
            print(kavm.pretty_print(inlineCellMaps(output_kast_term)))

        exit(output.returncode)

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

    return parser


if __name__ == "__main__":
    main()
