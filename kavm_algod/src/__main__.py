import json
import re
from argparse import ArgumentParser
import subprocess
from typing import List
from pathlib import Path
import os

from pyk.cli_utils import dir_path, file_path
from pyk.kast import KInner, KAst, KToken, KLabel, KApply, top_down

from pyk.kastManip import splitConfigFrom
from .kavm import KAVM


def collect_specific_cells(kast_term: KInner, labels: List[str]) -> List[Path]:
    """Extract a list of cells from a configuration"""
    result: List[Path] = []

    def label_selector(term):
        if isinstance(term, KApply) and term.label.name in labels:
            result.append(term)
        return term

    top_down(label_selector, kast_term)
    return result


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.command == 'teal-to-kore':
        kavm = KAVM(definition_dir=args.definition_dir)
        kavm.parse_teal_programs(args.program_files)
        return

    if args.command == 'scenario-to-kore':
        kavm = KAVM(definition_dir=args.definition_dir)
        kavm.parse_avm_simulation(args.input_file)
        return

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
        if args.definition_dir is None:
            args.definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
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
        env['KAVM_DEFITION_DIR'] = kavm.definition_dir
        output = subprocess.run(krun_command, shell=True, capture_output=True, env=env)

        output_kast_term = KAst.from_dict(json.loads(output.stdout)['term'])
        if args.output != 'none':
            if args.extract_cells is not None:
                for cell_term in collect_specific_cells(
                    output_kast_term, args.extract_cells
                ):
                    print(kavm.pretty_print(cell_term))
            else:
                print(kavm.pretty_print(output_kast_term))

        return

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
    run_subparser.add_argument(
        '--extract-cells',
        nargs='+',
        type=str,
        help='Extract cells with specified labels from final configuration',
    )

    # teak-to-kore
    teal_to_k_subparser = command_parser.add_parser(
        'teal-to-kore',
        help='Parse TEAL program(s) and output the KORE term.',
    )
    teal_to_k_subparser.add_argument(
        'definition_dir', type=dir_path, help='Path to definition to use.'
    )
    teal_to_k_subparser.add_argument(
        'program_files', nargs='+', help='One of more .teal files'
    )

    # scenario-to-kore
    scenario_subparser = command_parser.add_parser(
        'scenario-to-kore',
        help='Parse an AVM simulation scenario and output the KORE term.',
    )
    scenario_subparser.add_argument(
        'definition_dir', type=dir_path, help='Path to definition to use.'
    )
    scenario_subparser.add_argument(
        'input_file', type=file_path, help='Path to AVM simulation scenario file'
    )

    return parser


if __name__ == "__main__":
    main()
