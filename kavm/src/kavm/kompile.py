import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from typing import Any, Callable, Dict, Final, Iterable, List, Optional, Set, Tuple, Union, cast

from pyk.cli_utils import run_process
from pyk.kast import KApply, KAst, KInner, KLabel, KSort, KToken, Subst
from pyk.kastManip import free_vars, inline_cell_maps, split_config_from
from pyk.ktool import KRun
from pyk.ktool.kprint import paren
from pyk.prelude import Sorts, build_assoc, build_cons, intToken, stringToken


from kavm.kavm import KAVM


def kompile(
    definition_dir: Path,
    main_file: Path,
    includes: Optional[List[Path]] = None,
    main_module_name: Optional[str] = None,
    syntax_module_name: Optional[str] = None,
    backend: Optional[str] = 'llvm',
    md_selector: Optional[str] = None,
    hook_namespaces: Optional[List[str]] = None,
    hook_cpp_files: Optional[List[Path]] = None,
    hook_clang_flags: Optional[List[str]] = None,
) -> KAVM:
    if backend == 'llvm':
        generate_interpreter(
            definition_dir,
            main_file,
            includes,
            main_module_name,
            syntax_module_name,
            md_selector,
            hook_namespaces,
            hook_cpp_files,
            hook_clang_flags,
        )
    return KAVM(definition_dir)


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
) -> None:
    '''Kompile KAVM to produce an LLVM-based interpterer'''

    def _kompile_partial() -> None:
        command = [
            'kompile',
            '--output-definition',
            str(definition_dir),
            str(main_file),
        ]

        command += ['--verbose']
        command += ['--emit-json']
        command += ['--main-module', main_module_name] if main_module_name else []
        command += ['--syntax-module', syntax_module_name] if syntax_module_name else []
        command += [arg for include in includes for arg in ['-I', include]] if includes else []
        command += ['--md-selector', md_selector] if md_selector else []
        command += ['--hook-namespaces', ' '.join(hook_namespaces)] if hook_namespaces else []
        command += ['-ccopt', '-c', '-ccopt', '-o', '-ccopt', 'partial.o']
        try:
            subprocess.run(command, check=True, text=True)
        except CalledProcessError:
            print(' '.join(map(str, command)))
            raise

    def _llvm_kompile(
        interpreter_object_file: Path,
        interpteter_executable_file: Path,
        hook_cpp_files: Optional[List[Path]] = None,
        hook_clang_flags: Optional[List[str]] = None,
    ) -> None:
        command = ['llvm-kompile', str(interpreter_object_file), 'main']

        command += [str(path) for path in hook_cpp_files] if hook_cpp_files else []
        command += ['-o', str(interpteter_executable_file)]
        command += [flag.strip() for flag in hook_clang_flags] if hook_clang_flags else []

        try:
            print(' '.join(map(str, command)))
            subprocess.run(command, check=True, text=True)
        except CalledProcessError:
            print(' '.join(map(str, command)))
            raise

    _kompile_partial()
    _llvm_kompile(
        interpreter_object_file=definition_dir / 'partial.o',
        interpteter_executable_file=definition_dir / 'interpreter',
        hook_cpp_files=hook_cpp_files,
        # includes=includes,
        hook_clang_flags=hook_clang_flags,
    )
