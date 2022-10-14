#!/usr/bin/env bash

set -euo pipefail

# The interpreter needs to be linked with KLLVM C++ library
KLLVM_INCLUDES=$(dirname $(which kompile))/../include/kllvm

# The blockchain-k-plugin declares hooked cryptographic functions, and we need both the K and C++ sources
PLUGIN_INCLUDES=$(realpath "../../.build/usr/lib/kavm/blockchain-k-plugin/include/")
PLUGIN_K_INCLUDES=$PLUGIN_INCLUDES/kframework
PLUGIN_CPP_FILES="${PLUGIN_INCLUDES}/c/plugin_util.cpp ${PLUGIN_INCLUDES}/c/crypto.cpp ${PLUGIN_INCLUDES}/c/blake2.cpp"

# The blockchain-k-plugin hooks need libff: both includes and the compiled shared object
LIBFF_LIB=$(realpath "../../.build/usr/lib/kavm/libff/lib/")
LIBFF_INCLUDE=$(realpath "../../.build/usr/lib/kavm/libff/include/")

# The custom hooks for KAVM: we need the C++ sources
KAVM_HOOKS_INCLUDES=$(realpath "../../.build/usr/lib/kavm/include/c/")
KAVM_HOOKS_CPP_FILES="${KAVM_HOOKS_INCLUDES}/algorand.cpp ${KAVM_HOOKS_INCLUDES}/base.cpp ${KAVM_HOOKS_INCLUDES}/mnemonic.cpp ${KAVM_HOOKS_INCLUDES}/hooks.cpp"

# Clang needs to link these libraries into the interpreter
CLANG_FLAGS="-lcryptopp -lsecp256k1 -lff -lcurl -lssl -lcrypto -lprocps"

CURDIR=$(pwd)

# Build the interpreter object file by kompiling the K modules: the semantics and blockchain-k-plugin
kompile $CURDIR/kavm-hooks-tests.k --backend llvm \
        --syntax-module KAVM-HOOKS-TESTS          \
        --hook-namespaces "KAVM KRYPTO"           \
        -I $PLUGIN_K_INCLUDES                     \
        -ccopt -c -ccopt -o -ccopt partial.o

# Compile the C++ code of the blockchain-k-plugin's hooks and the custom hooks and link them into the interpreter
llvm-kompile $CURDIR/kavm-hooks-tests-kompiled/partial.o main -- \
             $PLUGIN_CPP_FILES $KAVM_HOOKS_CPP_FILES             \
             -I"$KLLVM_INCLUDES"                                 \
             -I"$LIBFF_INCLUDE" -L"$LIBFF_LIB"                   \
             $CLANG_FLAGS                                        \
             -o $CURDIR/kavm-hooks-tests-kompiled/interpreter
