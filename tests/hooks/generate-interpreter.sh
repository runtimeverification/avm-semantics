#!/usr/bin/env bash

set -euo pipefail

HOOK_CPPFILES="$@"
KLLVM_INCLUDES=$(dirname $(which kompile))/../include/kllvm
CURDIR=$(pwd)
kompile $CURDIR/kavm-hooks-tests.k --syntax-module KAVM-HOOKS-TESTS --backend llvm --hook-namespaces KAVM -ccopt -c -ccopt -o -ccopt partial.o
llvm-kompile $CURDIR/kavm-hooks-tests-kompiled/partial.o main $HOOK_CPPFILES -o $CURDIR/kavm-hooks-tests-kompiled/interpreter -I"$KLLVM_INCLUDES" -lcrypto
