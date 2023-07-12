import itertools
import logging
import subprocess
import sys
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Final, List, Optional

from pyk.ktool.kompile import HaskellKompile, Kompile, KompileArgs, LLVMKompile, LLVMKompileType

from kavm.kavm import KAVM

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def kompile(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    backend: Optional[str] = 'llvm',
    llvm_kompile_type: LLVMKompileType | None = None,
    md_selector: Optional[str] = None,
    verbose: bool = True,
    hook_namespaces: Optional[List[str]] = None,
    hook_cpp_files: Optional[List[Path]] = None,
    hook_clang_flags: Optional[List[str]] = None,
    coverage: bool = False,
    gen_bison_parser: bool = False,
    emit_json: bool = True,
) -> KAVM:
    if includes:
        include_dirs = [Path(include) for include in includes]
    else:
        include_dirs = []

    base_args = KompileArgs(
        main_file=main_file,
        main_module=main_module_name,
        syntax_module=syntax_module_name,
        include_dirs=include_dirs,
        md_selector=md_selector,
        hook_namespaces=hook_namespaces if hook_namespaces else [],
        emit_json=emit_json,
    )
    kompile: Kompile
    match backend:
        case 'llvm':
            cpp_files = hook_cpp_files if hook_cpp_files else []
            clang_flags = hook_clang_flags if hook_clang_flags else []
            kompile = LLVMKompile(
                base_args=base_args,
                ccopts=[f.lstrip() for f in clang_flags] + [str(p) for p in cpp_files],
                llvm_kompile_type=llvm_kompile_type,
            )
        case 'haskell':
            kompile = HaskellKompile(
                base_args=base_args,
            )
        case _:
            raise ValueError(f'Unsupported backend: {backend}')

    try:
        kompile(output_dir=definition_dir)
        return KAVM(definition_dir)
    except RuntimeError as err:
        sys.stderr.write(f'\nkompile stdout:\n{err.args[1]}\n')
        sys.stderr.write(f'\nkompile stderr:\n{err.args[2]}\n')
        sys.stderr.write(f'\nkompile returncode:\n{err.args[3]}\n')
        sys.stderr.flush()
        raise


def kompile_haskell(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    md_selector: Optional[str] = None,
    hook_namespaces: Optional[List[str]] = None,
    backend: Optional[str] = 'llvm',
    verbose: bool = True,
    emit_json: bool = True,
) -> CompletedProcess:
    command = [
        'kompile',
        '--output-definition',
        str(definition_dir),
        str(main_file),
    ]

    command += ['--verbose'] if verbose else []
    command += ['--emit-json'] if emit_json else []
    command += ['--backend', backend] if backend else []
    command += ['--main-module', main_module_name] if main_module_name else []
    command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
    command += ['--md-selector', md_selector] if md_selector else []
    command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
    command += ['--concrete-rules', ','.join(KAVM.concrete_rules())] if KAVM.concrete_rules() else []
    command += [str(arg) for include in includes for arg in ['-I', include]] if includes else []

    _LOGGER.info(' '.join(command))

    return subprocess.run(command, check=True, text=True)


def generate_interpreter(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    md_selector: Optional[str] = None,
    hook_namespaces: Optional[List[str]] = None,
    hook_cpp_files: Optional[List[Path]] = None,
    hook_clang_flags: Optional[List[str]] = None,
    coverage: bool = False,
    gen_bison_parser: bool = False,
) -> None:
    '''Kompile KAVM to produce an LLVM-based interpreter'''

    interpreter_executable_file = definition_dir / 'interpreter'

    def _clang_flags() -> List[str]:
        flags = [str(path) for path in hook_cpp_files] if hook_cpp_files else []
        flags += ['-o', str(interpreter_executable_file)]
        flags += [flag.strip() for flag in hook_clang_flags] if hook_clang_flags else []

        ccopt_flags = [('-ccopt', flag) for flag in flags]
        return list(itertools.chain(*ccopt_flags))

    def _kompile(
        interpreter_executable_file: Path,
        hook_cpp_files: Optional[List[Path]] = None,
        hook_clang_flags: Optional[List[str]] = None,
    ) -> None:
        command = [
            'kompile',
            '--output-definition',
            str(definition_dir),
            str(main_file),
        ]

        command += ['--verbose']
        command += ['--emit-json']
        command += ['--gen-glr-bison-parser'] if gen_bison_parser else []
        command += ['--main-module', main_module_name] if main_module_name else []
        command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
        command += [str(arg) for include in includes for arg in ['-I', include]] if includes else []
        command += ['--md-selector', md_selector] if md_selector else []
        command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
        command += ['--coverage'] if coverage else []
        command += _clang_flags()
        try:
            subprocess.run(command, check=True, text=True)
        except CalledProcessError:
            print(' '.join(map(str, command)))
            raise

    _kompile(
        interpreter_executable_file=interpreter_executable_file.resolve(),
        hook_cpp_files=hook_cpp_files,
        hook_clang_flags=hook_clang_flags,
    )
