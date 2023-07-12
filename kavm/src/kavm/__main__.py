"""Command-line interface for KAVM"""

import json
import logging
import os
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Callable, Dict, Final, Iterable, List, Optional, TypeVar

from pyk.cli.utils import dir_path, file_path, node_id_like
from pyk.kast.inner import KApply
from pyk.kast.manip import minimize_term
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.kcfg import KCFG, NodeIdLike
from pyk.kcfg.tui import KCFGViewer
from pyk.kore import syntax as kore
from pyk.ktool.kompile import LLVMKompileType
from pyk.ktool.kprove import KoreExecLogFormat
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofShow
from pyk.utils import BugReport

from kavm.kavm import KAVM
from kavm.kompile import kompile
from kavm.scenario import KAVMScenario

T = TypeVar('T')

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def exec_kompile(
    definition_dir: Path,
    main_file: Path,
    main_module: Optional[str],
    syntax_module: Optional[str],
    backend: Optional[str],
    verbose: bool,
    includes: List[Path],
    hook_namespaces: List[str],
    hook_cpp_files: List[Path],
    hook_clang_flags: List[str],
    coverage: bool,
    gen_bison_parser: bool = False,
    llvm_library: bool = False,
    **kwargs: Any,
) -> None:
    kompile(
        definition_dir=definition_dir,
        main_file=main_file,
        main_module_name=main_module,
        syntax_module_name=syntax_module,
        includes=includes,
        backend=backend,
        verbose=True,
        hook_namespaces=hook_namespaces,
        hook_cpp_files=hook_cpp_files,
        hook_clang_flags=hook_clang_flags,
        coverage=coverage,
        gen_bison_parser=gen_bison_parser,
        llvm_kompile_type=LLVMKompileType.C if llvm_library else LLVMKompileType.MAIN,
    )


def exec_prove(
    definition_dir: Path,
    spec_file: Path,
    bug_report: bool = False,
    depth: Optional[int] = None,
    debug_equations: Iterable[str] = (),
    claims: Iterable[str] = (),
    exclude_claims: Iterable[str] = (),
    minimize: bool = True,
    smt_timeout: int = 40,
    haskell_log_format: str = KoreExecLogFormat.ONELINE.value,
    haskell_log_debug_transition: bool = True,
    haskell_log_entries: Iterable[str] = (),
    **kwargs: Any,
) -> None:
    kavm = KAVM(definition_dir=definition_dir)
    prove_args = []
    haskell_args = []
    for de in debug_equations:
        haskell_args += ['--debug-equation', de]
    if smt_timeout:
        haskell_args += ['--smt-timeout', str(smt_timeout)]
    if bug_report:
        haskell_args += ['--bug-report', str(spec_file.with_suffix(''))]
    if depth is not None:
        prove_args += ['--depth', str(depth)]
    if claims:
        prove_args += ['--claims', ','.join(claims)]
    if exclude_claims:
        prove_args += ['--exclude', ','.join(exclude_claims)]
    try:
        final_state = kavm.prove(
            spec_file=spec_file,
            args=prove_args,
            haskell_args=haskell_args,
            haskell_log_entries=haskell_log_entries if haskell_log_entries else [],
            haskell_log_format=KoreExecLogFormat(haskell_log_format),
            haskell_log_debug_transition=haskell_log_debug_transition,
        )
        if minimize:
            final_state = minimize_term(final_state)
        print(kavm.pretty_print(final_state) + '\n')
        if not (type(final_state) is KApply and final_state.label.name == '#Top'):
            _LOGGER.error(f'Proof failed! See log file: {spec_file.resolve().name}.debug-log')
            sys.exit(1)
    except RuntimeError as e:
        error_msg = f'Proof failed! See log file: {spec_file.resolve().name}.debug-log'
        _LOGGER.error(error_msg)
        raise RuntimeError(error_msg) from e


def exec_kore_repl(
    definition: Path,
    spec_file: Path,
    debugger: bool,
    debug_script: Path,
    **kwargs: Any,
) -> None:
    command = [
        'kprove',
        '--definition',
        str(definition),
        str(spec_file),
    ]

    command += ['--debugger'] if debugger else []
    command += ['--debug-script', str(debug_script)] if debug_script else []

    _LOGGER.info(f"Executing command: {' '.join(command)}")

    try:
        proc_result = subprocess.run(command, check=True, text=True)
        print(proc_result.stdout)
    except CalledProcessError as err:
        raise RuntimeError(
            f'Command kprove exited with code {err.returncode} for: {spec_file}', err.stdout, err.stderr
        ) from err


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


def top_down_kore(f: Callable[[kore.Pattern], kore.Pattern], pattern: kore.Pattern) -> kore.Pattern:
    return f(pattern).map_pattern(lambda _kpattern: top_down_kore(f, _kpattern))  # type: ignore


def get_state_dumps_kore(input: kore.Pattern) -> Optional[kore.Pattern]:
    state_dumps_cell_symbol = "Lbl'-LT-'state-dumps'-GT-'"

    result = None

    def get_it(input: kore.Pattern) -> kore.Pattern:
        nonlocal result
        if isinstance(input, kore.App) and input.symbol == state_dumps_cell_symbol:
            result = input
        return input

    top_down_kore(get_it, input)
    if isinstance(result, kore.App):
        return result.patterns[0].app.patterns[0].patterns[0]  # type: ignore
    else:
        return None


def kore_json_to_dict(input: kore.Pattern) -> Dict[str, Any]:
    return {}


def exec_run(
    definition_dir: Path,
    input_file: Path,
    teal_sources_dir: Path,
    teal_parser: Path,
    avm_simulation_parser: Path,
    avm_json_parser: Path,
    output: str,
    depth: Optional[int],
    **kwargs: Any,
) -> None:
    kavm = KAVM(definition_dir=definition_dir)

    if not teal_parser:
        teal_parser = definition_dir / 'parser_TealInputPgm_TEAL-PARSER-SYNTAX'
    if not avm_json_parser:
        avm_json_parser = definition_dir / 'parser_JSON_AVM-TESTING-SYNTAX'
    try:
        if input_file.suffix == '.json':
            scenario = KAVMScenario.from_json(input_file.read_text(), teal_sources_dir)
            final_state, kavm_stderr = kavm.run_avm_json(
                scenario=scenario, depth=depth, rerun_on_error=True, check=False
            )
            if output == 'kore':
                print(final_state)
                exit(0)
            if output == 'pretty':
                final_state_kast = kavm.kore_to_kast(final_state)
                print(kavm.pretty_print(final_state_kast))
            if output == 'final-state-json':
                _LOGGER.info('Extracting <state_dumps> cell from KORE output')
                state_dumps_kore = get_state_dumps_kore(final_state)
                assert state_dumps_kore
                _LOGGER.info('Converting KORE => Kast')
                state_dumps = kavm.kore_to_kast(state_dumps_kore)
                _LOGGER.info('Pretty-printing <state_dumps> JSON')
                state_dump_str = kavm.pretty_print(state_dumps).replace(', .JSONs', '').replace('.JSONs', '')
                print(json.dumps(json.loads(state_dump_str), indent=4))
            if output == 'stderr-json':
                print(json.dumps(json.loads(kavm_stderr), indent=4))
            exit(0)
        else:
            print(f'Unrecognized input file extension: {input_file.suffix}')
            exit(1)
    except RuntimeError as err:
        msg, stdout, stderr = err.args
        _LOGGER.critical(stdout)
        _LOGGER.critical(msg)
        _LOGGER.critical(stderr)


def exec_env(
    **kwargs: Any,
) -> None:
    """
    Report KAVM's environment variables or attempt to establish their vaules
    """
    print(f"KAVM_DEFINITION_DIR={os.environ.get('KAVM_DEFINITION_DIR')}")
    print(f"KAVM_VERIFICATION_DEFINITION_DIR={os.environ.get('KAVM_VERIFICATION_DEFINITION_DIR')}")


def exec_kcfg_view(
    definition_dir: Path,
    spec_file: Path,
    claim_id: str,
    spec_module: Optional[str] = None,
    use_directory: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    use_directory = use_directory if use_directory else Path('.kavm')
    kavm = KAVM(definition_dir=definition_dir, use_directory=use_directory)

    spec_module = spec_module if spec_module else spec_file.name.removesuffix('.k').removesuffix('.md').upper()

    proof = APRProof.read_proof(f'{spec_module}.{claim_id}', proof_dir=use_directory)
    kcfg_viewer = KCFGViewer(proof.kcfg, kavm)
    kcfg_viewer.run()


def exec_kcfg_show(
    definition_dir: Path,
    spec_file: Path,
    claim_id: str,
    spec_module: Optional[str] = None,
    use_directory: Optional[Path] = None,
    nodes: Iterable[NodeIdLike] = (),
    minimize: bool = True,
    **kwargs: Any,
) -> None:
    use_directory = use_directory if use_directory else Path('.kavm')
    kavm = KAVM(definition_dir=definition_dir, use_directory=use_directory)

    spec_module = spec_module if spec_module else spec_file.name.removesuffix('.k').removesuffix('.md').upper()

    proof = APRProof.read_proof(f'{spec_module}.{claim_id}', proof_dir=use_directory)
    proof_show = APRProofShow(kavm)

    res_lines = proof_show.show(
        proof,
        nodes=nodes,
        minimize=minimize,
        sort_collections=True,
    )
    print('\n'.join(res_lines))

    print('Proof summary:')
    print('\n'.join(proof.summary))


def exec_kcfg_prove(
    definition_dir: Path,
    spec_file: Path,
    claim_id: str,
    kore_rpc_port: int,
    bug_report: bool = False,
    spec_module: Optional[str] = None,
    use_directory: Optional[Path] = None,
    use_booster: bool = False,
    llvm_library: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    default_kavm_dir = Path('.kavm')
    default_kavm_dir.mkdir(parents=True, exist_ok=True)
    use_directory = use_directory if use_directory else default_kavm_dir
    bug_report_path = BugReport(use_directory / 'kavm-bug') if bug_report else None
    kavm = KAVM(definition_dir=definition_dir, use_directory=use_directory, bug_report=bug_report_path)

    spec_module = spec_module if spec_module else spec_file.name.removesuffix('.k').removesuffix('.md').upper()
    claim_label = f'{spec_module}.{claim_id}'
    claims = kavm.get_claims(spec_file, spec_module_name=spec_module, claim_labels=[claim_label])

    cfg, init_node, target_node = KCFG.from_claim(kavm.definition, claims[0])

    proof = APRProof(
        id=claim_label, kcfg=cfg, init=init_node, target=target_node, proof_dir=kavm.use_directory, logs={}
    )

    if use_booster:
        if llvm_library:
            kore_rpc_command = ['kore-rpc-booster', '--llvm-backend-library', str(llvm_library)]
        else:
            kore_rpc_command = ['kore-rpc-booster']
    else:
        kore_rpc_command = ['kore-rpc']
    with KCFGExplore(
        kavm, kore_rpc_command=kore_rpc_command, port=kore_rpc_port, bug_report=bug_report_path
    ) as kcfg_explore:
        prover = APRProver(proof, kcfg_explore=kcfg_explore)
        prover.advance_proof(
            cut_point_rules=['AVM-EXECUTION.starttx', 'AVM-EXECUTION.endtx', 'AVM-PANIC.panic'],
        )


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
            raise RuntimeError(
                'Cannot find KAVM definition, plese specify either --definition-dir or KAVM_DEFINITION_DIR'
            )

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(**vars(args))


def create_argument_parser() -> ArgumentParser:
    def list_of(elem_type: Callable[[str], T], delim: str = ';') -> Callable[[str], List[T]]:
        def parse(s: str) -> List[T]:
            return [elem_type(elem) for elem in s.split(delim)]

        return parse

    parser = ArgumentParser(prog='kavm')

    shared_args = ArgumentParser(add_help=False)
    shared_args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
    shared_args.add_argument('--debug', default=False, action='store_true', help='Debug output.')

    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # env
    command_parser.add_parser(
        'env',
        help='Show KAVM environment variables',
        parents=[shared_args],
        allow_abbrev=False,
    )

    # kompile
    kompile_subparser = command_parser.add_parser(
        'kompile',
        help='Kompile KAVM',
        parents=[shared_args],
        allow_abbrev=False,
    )
    kompile_subparser.add_argument(
        '--definition-dir', dest='definition_dir', type=dir_path, help='Path to store the kompiled definition'
    )
    kompile_subparser.add_argument('main_file', type=file_path, help='Path to the main file')
    kompile_subparser.add_argument('--main-module', type=str)
    kompile_subparser.add_argument('--syntax-module', type=str)
    kompile_subparser.add_argument('--backend', type=str)
    kompile_subparser.add_argument('--coverage', default=False, action='store_true')
    kompile_subparser.add_argument('--gen-bison-parser', default=False, action='store_true')
    kompile_subparser.add_argument('--emit-json', default=False, action='store_true')
    kompile_subparser.add_argument('--llvm-library', default=False, action='store_true')
    kompile_subparser.add_argument(
        '-I',
        type=dir_path,
        dest='includes',
        default=[],
        action='append',
        help='Directories to lookup K definitions in.',
    )
    kompile_subparser.add_argument(
        '--hook-namespaces',
        type=str,
        nargs='*',
        dest='hook_namespaces',
        default=[],
        help='A whitespace-separated list of namespaces to include in the hooks defined in the definition.',
    )
    kompile_subparser.add_argument(
        '--hook-cpp-files',
        type=Path,
        nargs='*',
        dest='hook_cpp_files',
        default=[],
        help='C++ source files of hooked functions to compile and link into the interpreter',
    )
    kompile_subparser.add_argument(
        '--hook-clang-flags',
        type=str,
        nargs='*',
        dest='hook_clang_flags',
        default=[],
        help='A whitespace-separated list of flags to pass to clang when calling llvm-kompile',
    )

    # prove
    prove_subparser = command_parser.add_parser('prove', help='Prove claims', parents=[shared_args])
    prove_subparser.add_argument('spec_file', type=file_path, help='Path to the K spec file')
    prove_subparser.add_argument('--definition-dir', dest='definition_dir', type=dir_path)
    prove_subparser.add_argument('--debugger', default=False, action='store_true')
    prove_subparser.add_argument('--debug-script', type=file_path)
    prove_subparser.add_argument('--smt-timeout', dest='smt_timeout', type=int),
    prove_subparser.add_argument(
        '--haskell-log-format',
        type=str,
        choices=[f.value for f in KoreExecLogFormat],
        default=KoreExecLogFormat.ONELINE.value,
    )
    prove_subparser.add_argument(
        '--debug-equations', type=list_of(str, delim=','), default=[], help='Comma-separate list of equations to debug.'
    )
    prove_subparser.add_argument(
        '--haskell-log-entries',
        type=list_of(str, delim=','),
        default=[],
    )

    # kore-repl
    kore_repl_subparser = command_parser.add_parser(
        'kore-repl', help='Prove claims interactively', parents=[shared_args]
    )
    kore_repl_subparser.add_argument('spec_file', type=file_path, help='Path to the spec file')
    kore_repl_subparser.add_argument('--definition', type=dir_path)
    kore_repl_subparser.add_argument('--debugger', default=False, action='store_true')
    kore_repl_subparser.add_argument('--debug-script', type=file_path)

    # kast
    kast_subparser = command_parser.add_parser('kast', help='Kast a term', parents=[shared_args])
    kast_subparser.add_argument(
        '--definition-dir',
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
        '--definition-dir',
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
        '--teal-parser',
        dest='teal_parser',
        type=file_path,
        help='Path to the executable to parse .teal files containing TealPrograms terms',
    )
    run_subparser.add_argument(
        '--avm-simulation-parser',
        dest='avm_simulation_parser',
        type=file_path,
        help='Path to the executable to parse .avm-simulation files containing AVMSimulation terms',
    )
    run_subparser.add_argument(
        '--avm-json-parser',
        dest='avm_json_parser',
        type=file_path,
        help='Path to the executable to parse .json files containing JSON-encoded AVM state',
    )
    run_subparser.add_argument(
        '--output',
        dest='output',
        type=str,
        help='Output mode',
        choices=['pretty', 'json', 'kore', 'kast', 'none', 'final-state-json', 'stderr-json'],
        required=True,
    )
    run_subparser.add_argument(
        '--depth',
        dest='depth',
        type=int,
        help='Execute at most N rewrite steps',
    )

    # kcfg-view
    kcfg_view_subparser = command_parser.add_parser('kcfg-view', help='Explore KCFG', parents=[shared_args])
    kcfg_view_subparser.add_argument('--definition-dir', dest='definition_dir', type=dir_path)
    kcfg_view_subparser.add_argument('spec_file', type=file_path, help='Path to the K spec file')
    kcfg_view_subparser.add_argument('claim_id', type=str, help='Claim from "spec_file" to prove')

    # kcfg-show
    kcfg_show_subparser = command_parser.add_parser(
        'kcfg-show', help='Show detailed output about KCFG', parents=[shared_args]
    )
    kcfg_show_subparser.add_argument('--definition-dir', dest='definition_dir', type=dir_path)
    kcfg_show_subparser.add_argument('spec_file', type=file_path, help='Path to the K spec file')
    kcfg_show_subparser.add_argument('claim_id', type=str, help='Claim from "spec_file" to prove')
    kcfg_show_subparser.add_argument(
        '--node',
        type=node_id_like,
        dest='nodes',
        default=[],
        action='append',
        help='Node to display more detailed information about.',
    )
    kcfg_show_subparser.add_argument(
        '--minimize', default=True, dest='minimize', action='store_true', help='Minimize node output.'
    )
    kcfg_show_subparser.add_argument(
        '--no-minimize', dest='minimize', action='store_false', help='Do not minimize node output.'
    )

    # kcfg-prove
    kcfg_prove_subparser = command_parser.add_parser(
        'kcfg-prove', help='Prove a claim using RPC-based prover. Generate KCFG for the claim.', parents=[shared_args]
    )
    kcfg_prove_subparser.add_argument('--definition-dir', dest='definition_dir', type=dir_path)
    kcfg_prove_subparser.add_argument('--bug-report', dest='bug_report', default=False, action='store_true')
    kcfg_prove_subparser.add_argument('spec_file', type=file_path, help='Path to the K spec file')
    kcfg_prove_subparser.add_argument('claim_id', type=str, help='Claim from "spec_file" to prove')
    kcfg_prove_subparser.add_argument('--port', dest='kore_rpc_port', required=True, type=int, help='Port for kore-rpc')
    kcfg_prove_subparser.add_argument('--use-booster', default=False, action='store_true')
    kcfg_prove_subparser.add_argument('--llvm-library', type=file_path, help='Path to interpreter.so')

    return parser


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == "__main__":
    main()
