# Settings
# --------

UNAME_S := $(shell uname -s)

SHELL = /bin/bash -o pipefail

DEPS_DIR    := deps
BUILD_DIR   := .build
BUILD_LOCAL := $(abspath $(BUILD_DIR)/local)
LOCAL_LIB   := $(BUILD_LOCAL)/lib

INSTALL_PREFIX  := /usr
INSTALL_BIN     ?= $(INSTALL_PREFIX)/bin
INSTALL_LIB     ?= $(INSTALL_PREFIX)/lib/kavm
INSTALL_INCLUDE ?= $(INSTALL_LIB)/include

KAVM_RELEASE_TAG ?= $(shell git describe --tags --dirty --long)
KAVM_BIN         := $(BUILD_DIR)$(INSTALL_BIN)
KAVM_LIB         := $(BUILD_DIR)$(INSTALL_LIB)
KAVM_INCLUDE     := $(KAVM_LIB)/include
KAVM_SCRIPTS     := $(KAVM_LIB)/scripts
KAVM_K_BIN       := $(KAVM_LIB)/kframework/bin
KAVM             := kavm
KAVM_DEFINITION_DIR=$(abspath $(KAVM_LIB)/avm-llvm/avm-testing-kompiled/)
KAVM_VERIFICATION_DEFINITION_DIR=$(abspath $(KAVM_LIB)/avm-haskell/verification-kompiled/)
export KAVM_LIB
export KAVM_DEFINITION_DIR
export KAVM_VERIFICATION_DEFINITION_DIR

K_SUBMODULE := $(DEPS_DIR)/k
K_BIN       := $(INSTALL_LIB)/kframework/bin

LIBRARY_PATH         := $(LOCAL_LIB)
LOCAL_K_INCLUDE_PATH := $(BUILD_LOCAL)/include/kframework/
C_INCLUDE_PATH       += :$(BUILD_LOCAL)/include
CPLUS_INCLUDE_PATH   += :$(BUILD_LOCAL)/include
PATH                 := $(CURDIR)/$(KAVM_BIN):$(CURDIR)/$(BUILD_DIR)$(K_BIN):$(PATH)

export LIBRARY_PATH
export C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH
export LOCAL_LIB
export PATH

PLUGIN_SUBMODULE := $(abspath $(DEPS_DIR)/plugin)
PLUGIN_SOURCE    := $(KEVM_INCLUDE)/kframework/blockchain-k-plugin/krypto.md

export PLUGIN_SUBMODULE


# if K_OPTS is undefined, up the default heap size for kompile
ifeq "$(origin K_OPTS)" "undefined"
K_OPTS := -Xmx8G
endif
export K_OPTS

KORE_RPC_PORT := $(if $(KORE_RPC_PORT),$(KORE_RPC_PORT),7777)

.PHONY: all clean distclean install uninstall                                         \
        deps k-deps libsecp256k1 libff plugin-deps hook-deps                          \
        build build-avm build-kavm                                                    \
        test test-avm-semantics test-avm-semantics-prove                              \
        test-kavm test-kavm-bison-parsers                                             \
        test-kavm-hooks build-kavm-hooks-tests                                        \
        clean-avm clean-kavm                                                          \
        module-imports-graph module-imports-graph-dot

.SECONDARY:

all: deps build test

deps: plugin-deps k-deps

# Non-K Dependencies
# ------------------

libsecp256k1_out := $(LOCAL_LIB)/pkgconfig/libsecp256k1.pc
libff_out        := $(KAVM_LIB)/libff/lib/libff.a
libcryptopp_out  := $(KAVM_LIB)/cryptopp/lib/libcryptopp.a

libsecp256k1: $(libsecp256k1_out)
libff:        $(libff_out)
libcryptopp : $(libcryptopp_out)

$(libsecp256k1_out): $(PLUGIN_SUBMODULE)/deps/secp256k1/autogen.sh
	cd $(PLUGIN_SUBMODULE)/deps/secp256k1                                 \
	    && ./autogen.sh                                                   \
	    && ./configure --enable-module-recovery --prefix="$(BUILD_LOCAL)" \
	    && $(MAKE)                                                        \
	    && $(MAKE) install

LIBFF_CMAKE_FLAGS := -DCMAKE_CXX_FLAGS=-fPIC

ifeq ($(UNAME_S),Linux)
    LIBFF_CMAKE_FLAGS +=
else ifeq ($(UNAME_S),Darwin)
    LIBFF_CMAKE_FLAGS += -DWITH_PROCPS=OFF -DOPENSSL_ROOT_DIR=$(shell brew --prefix openssl)
else
    LIBFF_CMAKE_FLAGS += -DWITH_PROCPS=OFF
endif

ifneq ($(APPLE_SILICON),)
    LIBFF_CMAKE_FLAGS += -DCURVE=ALT_BN128 -DUSE_ASM=Off
endif

$(libff_out): $(PLUGIN_SUBMODULE)/deps/libff/CMakeLists.txt
	@mkdir -p $(PLUGIN_SUBMODULE)/deps/libff/build
	cd $(PLUGIN_SUBMODULE)/deps/libff/build                                                                     \
	    && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$(INSTALL_LIB)/libff $(LIBFF_CMAKE_FLAGS) \
	    && make -s -j4                                                                                          \
	    && make install DESTDIR=$(CURDIR)/$(BUILD_DIR)

$(libcryptopp_out): $(PLUGIN_SUBMODULE)/deps/cryptopp/GNUmakefile
	cd $(PLUGIN_SUBMODULE)/deps/cryptopp                            \
            && $(MAKE) install DESTDIR=$(CURDIR)/$(BUILD_DIR) PREFIX=$(INSTALL_LIB)/cryptopp

# K Dependencies
# --------------


deps: k-deps plugin-deps

K_MVN_ARGS :=
ifneq ($(SKIP_LLVM),)
    K_MVN_ARGS += -Dllvm.backend.skip
endif
ifneq ($(SKIP_HASKELL),)
    K_MVN_ARGS += -Dhaskell.backend.skip
endif

ifneq ($(APPLE_SILICON),)
    K_MVN_ARGS += -Dstack.extra-opts='--compiler ghc-8.10.7 --system-ghc'
endif

ifneq ($(RELEASE),)
    K_BUILD_TYPE := FastBuild
else
    K_BUILD_TYPE := Debug
endif

k-deps:
	cd $(K_SUBMODULE)                                                                                                                                                                            \
	    && mvn --batch-mode package -DskipTests -Dllvm.backend.prefix=$(INSTALL_LIB)/kframework -Dllvm.backend.destdir=$(CURDIR)/$(BUILD_DIR) -Dproject.build.type=$(K_BUILD_TYPE) $(K_MVN_ARGS) \
	    && DESTDIR=$(CURDIR)/$(BUILD_DIR) PREFIX=$(INSTALL_LIB)/kframework package/package

plugin_include    := $(abspath $(KAVM_LIB)/blockchain-k-plugin/include)
plugin_k          := krypto.md
plugin_c          := plugin_util.cpp crypto.cpp blake2.cpp plugin_util.h blake2.h
plugin_includes   := $(patsubst %, $(plugin_include)/kframework/%, $(plugin_k))
plugin_c_includes := $(patsubst %, $(plugin_include)/c/%,          $(plugin_c))
PLUGIN_CPP_FILES := $(plugin_include)/c/plugin_util.cpp \
                    $(plugin_include)/c/crypto.cpp      \
                    $(plugin_include)/c/blake2.cpp

$(plugin_include)/c/%: $(PLUGIN_SUBMODULE)/plugin-c/%
	@mkdir -p $(dir $@)
	install $< $@

$(plugin_include)/kframework/%: $(PLUGIN_SUBMODULE)/plugin/%
	@mkdir -p $(dir $@)
	install $< $@

plugin-deps: libsecp256k1 libff libcryptopp $(plugin_includes) $(plugin_c_includes)
# --------

build: build-kavm build-avm-llvm-so build-avm build-avm-verification

$(KAVM_INCLUDE)/kframework/%: lib/include/kframework/%
	@mkdir -p $(dir $@)
	install $< $@

hook_include  := $(abspath $(KAVM_LIB)/include/c)
hook_c        := algorand.cpp base.cpp hooks.cpp mnemonic.cpp algorand.h base.h mnemonic.h
hook_includes := $(patsubst %, $(hook_include)/%, $(hook_c))

HOOK_KAVM_FILES := $(hook_include)/algorand.cpp \
                   $(hook_include)/base.cpp     \
                   $(hook_include)/mnemonic.cpp \
                   $(hook_include)/hooks.cpp

$(hook_include)/%: $(CURDIR)/hooks/%
	@mkdir -p $(dir $@)
	install $< $@

HOOK_CC_OPTS      := " -g" " -std=c++17"                      \
                     " -L$(CURDIR)/$(KAVM_LIB)/libff/lib"     \
                     " -I$(CURDIR)/$(KAVM_LIB)/libff/include" \
                     " -I$(plugin_include)/c"                 \
                     " -I/usr/include"                        \
                     " -lcryptopp" " -lsecp256k1" " -lff" " -lcurl" " -lssl" " -lcrypto"

ifeq ($(UNAME_S),Darwin)
export BITCOIN_LIBEXEC := $(shell brew --prefix libbitcoin)/libexec
export SSL_ROOT        := $(shell brew --prefix openssl)
HOOK_CC_OPTS += -I/usr/local/include         \
                -I$(SSL_ROOT)/include        \
                -L$(SSL_ROOT)/lib            \
                -I$(BITCOIN_LIBEXEC)/include \
                -L$(BITCOIN_LIBEXEC)/lib
else ifeq ($(UNAME_S),Linux)
HOOK_CC_OPTS      += " -lprocps"
endif


HOOK_KOMPILE_OPTS := --hook-namespaces "$(HOOK_NAMESPACES)"  \
                     $(addprefix -ccopt=, $(HOOK_CC_OPTS))   \
                     $(addprefix -ccopt=, $(HOOK_KAVM_FILES))

## * kavm --- Python library and CLI app

PY_KAVM_DIR := ./kavm

ifeq ($(SKIP_POETRY_RUN),)
  POETRY_RUN  := poetry run -C $(PY_KAVM_DIR)
else
  POETRY_RUN  :=
endif


check-kavm-codestyle:
	$(MAKE) check -C $(PY_KAVM_DIR)

includes := $(avm_includes) $(plugin_includes) $(plugin_c_includes) $(hook_includes)

kavm_scripts := $(patsubst %, $(KAVM_SCRIPTS)/%, parse-avm-simulation.sh  parse-teal-programs.sh)

kavm_lib_files := version
kavm_libs      := $(patsubst %, $(KAVM_LIB)/%, $(kavm_lib_files))

build-kavm: $(KAVM_LIB)/version $(KAVM_DEFINITION_DIR)

# this target packages the Python-based kavm CLI
$(KAVM_LIB)/version: $(includes) $(kavm_scripts)
	@mkdir -p $(dir $@)
	echo '== KAVM Version'    > $@
	echo $(KAVM_RELEASE_TAG) >> $@
	echo '== Build Date'     >> $@
	date

$(KAVM_DEFINITION_DIR):
	@mkdir -p $(dir $@)

$(KAVM_LIB)/%: lib/%
	@mkdir -p $(dir $@)
	install $< $@

$(KAVM_INCLUDE)/kframework/modules/%:
	echo $@
	@mkdir -p $(dir $@)
	install $< $@

clean-kavm:
	rm -f $(KAVM_LIB)/version

# * avm-semantics --- the K semantics of AVM

avm_files    :=                            \
                avm/additional-fields.md   \
                avm/args.md                \
                avm/blockchain.md          \
                avm/constants.md           \
                avm/txn.md                 \
                avm/itxn.md                \
                avm/avm-configuration.md   \
                avm/avm-execution.md       \
                avm/avm-initialization.md  \
                avm/avm-limits.md          \
                avm/avm-txn-deque.md       \
                avm/teal/teal-constants.md \
                avm/teal/teal-driver.md    \
                avm/teal/teal-execution.md \
                avm/teal/teal-fields.md    \
                avm/teal/teal-stack.md     \
                avm/teal/teal-syntax.md    \
                avm/teal/teal-types.md     \
                avm/algod/algod-models.md  \
                avm/avm-testing.md         \
                avm/panics.md              \
                avm/macros.md

avm_includes := $(patsubst %, $(KAVM_INCLUDE)/kframework/%, $(avm_files))

AVM_KOMPILE_OPTS += --verbose $(COVERAGE_OPTS)
tangle_avm            := k & ((! type) | exec)

ifeq ($(K_BACKEND),)
  K_BACKEND := llvm
endif

ifneq ($(BUILD_WITH_COVERAGE),)
  BUILD_WITH_COVERAGE := --coverage
endif

avm_dir           := avm-llvm
avm_main_module   := AVM-TESTING
avm_syntax_module := AVM-TESTING-SYNTAX
avm_main_file     := avm/avm-testing.md
avm_main_filename := $(basename $(notdir $(avm_main_file)))
avm_kompiled      := $(avm_dir)/$(avm_main_filename)-kompiled/


build-avm-llvm-so: plugin-deps $(hook_includes) $(avm_includes) $(KAVM_LIB)/version
	@mkdir -p $(KAVM_DEFINITION_DIR)
	@rm -f $(KAVM_DEFINITION_DIR)/interpreter.o # make sure the llvm interpreter gets rebuilt
	@rm -f $(KAVM_DEFINITION_DIR)/interpreter.so
	$(POETRY_RUN) $(KAVM) kompile $(KAVM_INCLUDE)/kframework/$(avm_main_file)       \
                            --backend llvm                                              \
                            --llvm-library                                              \
                            -I "${KAVM_INCLUDE}/kframework"                             \
                            -I "${plugin_include}/kframework"                           \
                            --definition-dir "${KAVM_LIB}/${avm_kompiled}"              \
                            --main-module $(avm_main_module)                            \
                            --syntax-module $(avm_syntax_module)                        \
                            --hook-namespaces KRYPTO KAVM                               \
                            --hook-cpp-files $(HOOK_KAVM_FILES) $(PLUGIN_CPP_FILES)     \
                            --hook-clang-flags $(HOOK_CC_OPTS)                          \
                            $(BUILD_WITH_COVERAGE)
	@make generate-parsers

build-avm: plugin-deps $(hook_includes) $(avm_includes) $(KAVM_LIB)/version
	@mkdir -p $(KAVM_DEFINITION_DIR)
	@rm -f $(KAVM_DEFINITION_DIR)/interpreter.o # make sure the llvm interpreter gets rebuilt
	@rm -f $(KAVM_DEFINITION_DIR)/interpreter
	$(POETRY_RUN) $(KAVM) kompile $(KAVM_INCLUDE)/kframework/$(avm_main_file)       \
                            --backend llvm                                              \
                            -I "${KAVM_INCLUDE}/kframework"                             \
                            -I "${plugin_include}/kframework"                           \
                            --definition-dir "${KAVM_LIB}/${avm_kompiled}"              \
                            --main-module $(avm_main_module)                            \
                            --syntax-module $(avm_syntax_module)                        \
                            --hook-namespaces KRYPTO KAVM                               \
                            --hook-cpp-files $(HOOK_KAVM_FILES) $(PLUGIN_CPP_FILES)     \
                            --hook-clang-flags $(HOOK_CC_OPTS)                          \
                            $(BUILD_WITH_COVERAGE)
	@make generate-parsers


clean-avm:
	rm -rf $(KAVM_LIB)/$(avm_kompiled)
	rm -rf $(KAVM_INCLUDE)

generate-parsers:
	kast --definition $(KAVM_DEFINITION_DIR) --gen-parser \
             --module AVM-TESTING-SYNTAX                      \
             --sort JSON                                      \
             $(KAVM_DEFINITION_DIR)/parser_JSON_AVM-TESTING-SYNTAX
	kast --definition $(KAVM_DEFINITION_DIR) --gen-parser \
             --module TEAL-PARSER-SYNTAX                      \
             --sort TealInputPgm                              \
             $(KAVM_DEFINITION_DIR)/parser_TealInputPgm_TEAL-PARSER-SYNTAX
	echo 'cat $$(cat $$1)' > $(KAVM_DEFINITION_DIR)/catcat
	@chmod +x $(KAVM_DEFINITION_DIR)/catcat

build-avm-verification: $(KAVM_LIB)/$(avm_verification_kompiled)/timestamp

$(KAVM_LIB)/$(avm_verification_kompiled)/timestamp: tests/specs/verification.k $(avm_includes)
	mkdir -p $(KAVM_VERIFICATION_DEFINITION_DIR)
	$(POETRY_RUN)                                                                             \
        $(KAVM) kompile $< --backend haskell --definition-dir $(KAVM_VERIFICATION_DEFINITION_DIR) \
                           --emit-json --hook-namespaces KRYPTO KAVM                              \
                           -I "${KAVM_INCLUDE}/kframework" -I "${plugin_include}/kframework"

# Installation
# ------------

all_bin_sources := $(shell find $(KAVM_BIN) -type f | sed 's|^$(KAVM_BIN)/||')
all_lib_sources := $(shell find $(KAVM_LIB) -type f                                            \
                            -not -path "$(KAVM_LIB)/*/*-kompiled/dt/*"                         \
                            -not -path "$(KAVM_LIB)/kframework/share/kframework/pl-tutorial/*" \
                            -not -path "$(KAVM_LIB)/kframework/share/kframework/k-tutorial/*"  \
                        | sed 's|^$(KAVM_LIB)/||')

install: $(patsubst %, $(DESTDIR)$(INSTALL_BIN)/%, $(all_bin_sources)) \
         $(patsubst %, $(DESTDIR)$(INSTALL_LIB)/%, $(all_lib_sources))

$(DESTDIR)$(INSTALL_BIN)/%: $(KAVM_BIN)/%
	@mkdir -p $(dir $@)
	install $< $@

$(DESTDIR)$(INSTALL_LIB)/%: $(KAVM_LIB)/%
	@mkdir -p $(dir $@)
	install $< $@

uninstall:
	rm -rf $(DESTDIR)$(INSTALL_BIN)/kavm
	rm -rf $(DESTDIR)$(INSTALL_LIB)/kavm

# Coverage Processing
# -------------------

KCOVR:=$(KAVM_K_BIN)/kcovr

$(BUILD_DIR)/coverage.xml: test-kavm-avm-simulation
	$(POETRY_RUN) $(KCOVR) $(KAVM_DEFINITION_DIR)       \
        -- $(avm_includes) $(plugin_includes) > $(BUILD_DIR)/coverage.xml
	$(KAVM_SCRIPTS)/post-process-coverage $(BUILD_DIR)/coverage.xml

transient-coverage:
	$(POETRY_RUN) $(KCOVR) $(KAVM_DEFINITION_DIR)       \
        -- $(avm_includes) $(plugin_includes) > $(BUILD_DIR)/coverage.xml
	$(KAVM_SCRIPTS)/post-process-coverage $(BUILD_DIR)/coverage.xml

$(BUILD_DIR)/coverage.html: $(BUILD_DIR)/coverage.xml
	$(POETRY_RUN) pycobertura show --format html $(BUILD_DIR)/coverage.xml > $(BUILD_DIR)/coverage.html

coverage-html: $(BUILD_DIR)/coverage.html

# remove coverage execution logs from the kompiled directory
clean-coverage:
	rm -f $(KAVM_DEFINITION_DIR)/*_coverage.txt
	rm -f $(BUILD_DIR)/coverage.xml
	rm -f $(BUILD_DIR)/coverage.html

# Tests
# -----

KAVM_OPTIONS :=

test: test-kavm-hooks test-kavm test-kavm-avm-simulation test-kavm-algod test-avm-semantics-prove

##########################################
## Standalone AVM LLVM Backend hooks tests
##########################################

test-kavm-hooks: build-kavm-hooks-tests
	cd $(CURDIR)/tests/hooks; pytest

build-kavm-hooks-tests: $(hook_includes) plugin-deps
	cd $(CURDIR)/tests/hooks; ./generate-interpreter.sh

#######
## kavm
#######
check-codestyle-kavm:
	$(MAKE) check -C $(PY_KAVM_DIR)

## * kavm.algod Python library tests
test-kavm-algod:
	$(MAKE) test-unit -C $(PY_KAVM_DIR)
	$(MAKE) test-integration-kalgod -C $(PY_KAVM_DIR)


###########################
## Generated Bison parsers tests
###########################

test-kavm-bison-parsers:
	$(MAKE) test-bison-parsers -C $(PY_KAVM_DIR)

###########################
## AVM Simulation Scenarios
###########################
test-kavm-avm-simulation:
	$(MAKE) test-scenarios -C $(PY_KAVM_DIR)

############################################
## AVM PyTeal-generated Symbolic Proof Tests
############################################
test-pyteal-prove:
	$(MAKE) test-generated-claims -C $(PY_KAVM_DIR)

###########################
## AVM Symbolic Proof Tests
###########################
avm_prove_specs_failing := $(shell cat tests/failing-symbolic.list)
avm_prove_internal_specs := $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/internal/*-spec.k))
avm_prove_simple_specs := $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/simple/*-spec.k))
avm_prove_opcode_specs :=  $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/opcodes/*-spec.md))
avm_prove_call_specs :=  $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/calls/*-spec.md))
avm_prove_transactions_specs := $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/transactions/*-spec.k))
avm_prove_pact_specs := $(filter-out $(avm_prove_specs_failing), $(wildcard tests/specs/pact/*-spec.k))

test-avm-semantics-prove: test-avm-semantics-internal-prove test-avm-semantics-opcode-prove test-avm-semantics-simple-prove test-avm-semantics-calls-prove test-avm-semantics-transactions-prove test-avm-semantics-pact-prove

test-avm-semantics-kcfg-prove: test-avm-semantics-calls-kcfg-prove

test-avm-semantics-internal-prove: $(avm_prove_internal_specs:=.prove)
test-avm-semantics-opcode-prove: $(avm_prove_opcode_specs:=.prove)
test-avm-semantics-simple-prove: $(avm_prove_simple_specs:=.prove)
test-avm-semantics-calls-prove: $(avm_prove_call_specs:=.prove)
test-avm-semantics-transactions-prove: $(avm_prove_transactions_specs:=.prove)
test-avm-semantics-pact-prove: $(avm_prove_pact_specs:=.prove)
test-avm-semantics-calls-kcfg-prove: $(avm_prove_call_specs:=.kcfg.prove)

.SECONDEXPANSION:
tests/specs/%/verification/timestamp: tests/specs/$$(firstword $$(subst /, ,$$*))/verification.k $$(avm_includes)
	mkdir -p tests/specs/$*/verification
	$(POETRY_RUN)                                                                             \
	$(KAVM) kompile tests/specs/$*/verification.k --backend haskell --definition-dir tests/specs/$*/verification         \
													 --emit-json --hook-namespaces KRYPTO KAVM                              \
													 -I "${KAVM_INCLUDE}/kframework" -I "${plugin_include}/kframework"

.SECONDEXPANSION:
tests/specs/%-spec.k.prove: tests/specs/$$(firstword $$(subst /, ,$$*))/verification/timestamp $$(KAVM_LIB)/version
	$(POETRY_RUN) \
	$(KAVM) prove tests/specs/$*-spec.k --definition $(CURDIR)/tests/specs/$(firstword $(subst /, ,$*))/verification --smt-timeout 1000000

.SECONDEXPANSION:
tests/specs/%-spec.md.prove: tests/specs/$$(firstword $$(subst /, ,$$*))/verification/timestamp $$(KAVM_LIB)/version
	$(POETRY_RUN) \
	$(KAVM) prove tests/specs/$*-spec.md --definition $(CURDIR)/tests/specs/$(firstword $(subst /, ,$*))/verification --smt-timeout 1000000

.SECONDEXPANSION:
tests/specs/%-spec.k.kcfg.prove: tests/specs/$$(firstword $$(subst /, ,$$*))/verification/timestamp $$(KAVM_LIB)/version
	$(POETRY_RUN) \
	$(KAVM) kcfg-prove --port $(KORE_RPC_PORT) --definition-dir $(CURDIR)/tests/specs/$(firstword $(subst /, ,$*))/verification tests/specs/$*-spec.k main

.SECONDEXPANSION:
tests/specs/%-spec.md.kcfg.prove: tests/specs/$$(firstword $$(subst /, ,$$*))/verification/timestamp $$(KAVM_LIB)/version
	$(POETRY_RUN) \
	$(KAVM) kcfg-prove --port $(KORE_RPC_PORT) --definition-dir $(CURDIR)/tests/specs/$(firstword $(subst /, ,$*))/verification tests/specs/$*-spec.md main

clean-verification:
	rm -rf tests/specs/verification-kompiled


# Utils
# -----

# Generate a graph of module imports
module-imports-graph: module-imports-graph-dot
	dot -Tsvg $(KAVM_LIB)/$(avm_kompiled)/import-graph -o module-imports-graph.svg

module-imports-graph-dot:
	$(POETRY_RUN) && pyk graph-imports $(KAVM_LIB)/$(avm_kompiled)

clean: clean-avm clean-kavm clean-verification

distclean: clean
	rm -rf $(BUILD_DIR)
	git clean -dffx -- tests/
