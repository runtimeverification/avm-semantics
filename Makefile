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
KAVM_DEFINITION_DIR=$(KAVM_LIB)/avm-llvm/avm-execution-kompiled/
export KAVM_LIB
export KAVM_DEFINITION_DIR

K_SUBMODULE := $(DEPS_DIR)/k
K_BIN       := $(INSTALL_LIB)/kframework/bin

LIBRARY_PATH         := $(LOCAL_LIB)
LOCAL_K_INCLUDE_PATH := $(BUILD_LOCAL)/include/kframework/
C_INCLUDE_PATH       += :$(BUILD_LOCAL)/include
CPLUS_INCLUDE_PATH   += :$(BUILD_LOCAL)/include
PATH                 := $(CURDIR)/$(KAVM_BIN):$(CURDIR)/$(BUILD_DIR)$(K_BIN):$(PATH)
PLUGIN_SUBMODULE     := $(abspath $(DEPS_DIR)/plugin)

export LIBRARY_PATH
export C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH
export PATH
export PLUGIN_SUBMODULE
export LOCAL_LIB

# if K_OPTS is undefined, up the default heap size for kompile
ifeq "$(origin K_OPTS)" "undefined"
K_OPTS := -Xmx8G
endif
export K_OPTS

.PHONY: all clean distclean install uninstall                                         \
        deps k-deps libsecp256k1 libff plugin-deps hook-deps                          \
        build build-avm build-kavm py-kavm                                            \
        test test-avm-semantics test-avm-semantics-prove                              \
        test-kavm test-kavm-kast test-kavm-kast-avm-scenario test-kavm-kast-teal      \
        clean-avm clean-kavm                                                          \
        module-imports-graph module-imports-graph-dot                                 \
        venv venv-clean

.SECONDARY:

all: deps build test

# Non-K Dependencies
# ------------------

libsecp256k1_out := $(LOCAL_LIB)/pkgconfig/libsecp256k1.pc
libff_out        := $(KAVM_LIB)/libff/lib/libff.a

libsecp256k1: $(libsecp256k1_out)
libff:        $(libff_out)

$(libsecp256k1_out): $(PLUGIN_SUBMODULE)/deps/secp256k1/autogen.sh
	cd $(PLUGIN_SUBMODULE) && CXXFLAGS="$(CXXFLAGS) -std=c++14" make PREFIX="$(BUILD_LOCAL)" INSTALL_PREFIX="$(BUILD_LOCAL)" libsecp256k1

ifeq ($(UNAME_S),Linux)
  LIBFF_CMAKE_FLAGS=
else
  LIBFF_CMAKE_FLAGS=-DWITH_PROCPS=OFF
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

# K Dependencies
# --------------

deps: k-deps

ifneq ($(RELEASE),)
    K_BUILD_TYPE := FastBuild
    SEMANTICS_BUILD_TYPE := Release
else
    K_BUILD_TYPE := Debug
    SEMANTICS_BUILD_TYPE := Debug
endif

ifneq ($(SKIP_HASKELL),)
    SKIP_HASKELL := -Dhaskell.backend.skip=true
else
    SKIP_HASKELL :=
endif


k-deps: $(K_JAR)
	cd $(K_SUBMODULE) \
        && mvn --batch-mode package -DskipTests $(SKIP_HASKELL) -Dllvm.backend.prefix=$(INSTALL_LIB)/kframework -Dllvm.backend.destdir=$(CURDIR)/$(BUILD_DIR) -Dproject.build.type=$(K_BUILD_TYPE) $(K_MVN_ARGS) \
        && DESTDIR=$(CURDIR)/$(BUILD_DIR) PREFIX=$(INSTALL_LIB)/kframework package/package

# Building
# --------

build: build-kavm build-avm

$(KAVM_INCLUDE)/kframework/%: lib/include/kframework/%
	@mkdir -p $(dir $@)
	install $< $@

HOOK_NAMESPACES   := KRYPTO CLARITY

plugin_include    := $(abspath $(KAVM_LIB)/blockchain-k-plugin/include)
plugin_k          := krypto.md
plugin_c          := plugin_util.cpp crypto.cpp blake2.cpp plugin_util.h blake2.h
plugin_includes   := $(patsubst %, $(plugin_include)/kframework/%, $(plugin_k))
plugin_c_includes := $(patsubst %, $(plugin_include)/c/%,          $(plugin_c))

HOOK_PLUGIN_FILES := $(plugin_include)/c/plugin_util.cpp \
                     $(plugin_include)/c/crypto.cpp      \
                     $(plugin_include)/c/blake2.cpp

$(plugin_include)/c/%: $(PLUGIN_SUBMODULE)/plugin-c/%
	@mkdir -p $(dir $@)
	install $< $@

$(plugin_include)/kframework/%: $(PLUGIN_SUBMODULE)/plugin/%
	@mkdir -p $(dir $@)
	install $< $@

plugin-deps: $(plugin_includes) $(plugin_c_includes)

hook_include  := $(abspath $(KAVM_LIB)/include/c)
hook_c        := algorand.cpp base.cpp hooks.cpp mnemonic.cpp algorand.h base.h mnemonic.h
hook_includes := $(patsubst %, $(hook_include)/%, $(hook_c))

HOOK_ALGO_FILES := $(hook_include)/algorand.cpp \
                   $(hook_include)/base.cpp     \
                   $(hook_include)/mnemonic.cpp \
                   $(hook_include)/hooks.cpp

$(hook_include)/%: $(CURDIR)/hooks/%
	@mkdir -p $(dir $@)
	install $< $@

hook-deps: $(hook_includes)

HOOK_CC_OPTS      := -g -std=c++14                                     \
                     -L$(CURDIR)/$(KAVM_LIB)/libff/lib                 \
                     -I$(CURDIR)/$(KAVM_LIB)/libff/include             \
                     -I$(plugin_include)/c                             \
                     -lcryptopp -lsecp256k1 -lff -lcurl -lssl -lcrypto

ifeq ($(UNAME_S),Darwin)
export BITCOIN_LIBEXEC := $(shell brew --prefix libbitcoin)/libexec
export SSL_ROOT        := $(shell brew --prefix openssl)
HOOK_CC_OPTS += -I/usr/local/include         \
                -I$(SSL_ROOT)/include        \
                -L$(SSL_ROOT)/lib            \
                -I$(BITCOIN_LIBEXEC)/include \
                -L$(BITCOIN_LIBEXEC)/lib
else ifeq ($(UNAME_S),Linux)
HOOK_CC_OPTS      += -lprocps
endif


HOOK_KOMPILE_OPTS := --hook-namespaces "$(HOOK_NAMESPACES)"                     \
                     $(addprefix -ccopt , $(HOOK_PLUGIN_FILES) $(HOOK_CC_OPTS))

AVM_HOOK_KOMPILE_OPTS  := $(addprefix -ccopt , $(HOOK_ALGO_FILES))

ifneq ($(COVERAGE),)
    COVERAGE_OPTS := --coverage
else
    COVERAGE_OPTS :=
endif

## * kavm --- Python library and CLI app

PY_KAVM_DIR := ./kavm
VENV_DIR       := $(BUILD_DIR)/venv
VENV_ACTIVATE  := . $(VENV_DIR)/bin/activate

$(VENV_DIR)/pyvenv.cfg:
	   virtualenv $(VENV_DIR)              \
        && $(VENV_ACTIVATE)                    \
        && pip install --editable ./deps/k/pyk \
        && pip install --editable $(PY_KAVM_DIR)

venv: $(VENV_DIR)/pyvenv.cfg
	@echo $(VENV_ACTIVATE)

venv-clean:
	rm -rf $(VENV_DIR)

py-kavm:
	$(MAKE) -C $(PY_KAVM_DIR)

includes := $(avm_includes) $(plugin_includes) $(plugin_c_includes) $(hook_includes)

kavm_scripts := $(patsubst %, $(KAVM_SCRIPTS)/%, parse-avm-simulation.sh  parse-teal-programs.sh)

kavm_lib_files := version
kavm_libs      := $(patsubst %, $(KAVM_LIB)/%, $(kavm_lib_files))

build-kavm: $(KAVM_LIB)/version $(KAVM_DEFINITION_DIR)

# this target packages the Python-based kavm CLI
$(KAVM_LIB)/version: $(includes) $(kavm_scripts) py-kavm $(VENV_DIR)/pyvenv.cfg
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

clean-kavm: venv-clean
	rm -f $(KAVM_LIB)/version

# * avm-semantics --- the K semantics of AVM

avm_files    :=                            \
                avm/additional-fields.md   \
                avm/args.md                \
                avm/blockchain.md          \
                avm/constants.md           \
                avm/txn.md                 \
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
                avm/teal/teal-types.md

avm_includes := $(patsubst %, $(KAVM_INCLUDE)/kframework/%, $(avm_files))

AVM_KOMPILE_OPTS += --verbose $(COVERAGE_OPTS)
tangle_avm            := k & ((! type) | exec)

ifeq ($(K_BACKEND),)
  K_BACKEND := llvm
endif

avm_dir           := avm-llvm
avm_main_module   := AVM-EXECUTION
avm_syntax_module := TEAL-PARSER-SYNTAX
avm_main_file     := avm/avm-execution.md
avm_main_filename := $(basename $(notdir $(avm_main_file)))
avm_kompiled      := $(avm_dir)/$(avm_main_filename)-kompiled

build-avm: $(avm_includes) $(KAVM_LIB)/$(avm_kompiled)

$(KAVM_LIB)/$(avm_kompiled): $(KAVM_LIB)/version $(libff_out)
	$(VENV_ACTIVATE) && $(KAVM) kompile $(KAVM_INCLUDE)/kframework/$(avm_main_file) \
                            -I "${KAVM_INCLUDE}/kframework"                          \
                            -I "${plugin_include}/kframework"                           \
                            --definition-dir $(KAVM_LIB)/$(avm_kompiled)                \
                            --main-module $(avm_main_module)                            \
                            --syntax-module $(avm_syntax_module)                        \
                            $(AVM_KOMPILE_OPTS)

clean-avm:
	rm -rf $(KAVM_LIB)/$(avm_kompiled)
	rm -rf $(KAVM_INCLUDE)

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

# Tests
# -----

KAVM_OPTIONS :=

test: test-avm-semantics test-kavm

#################
## AVM Unit Tests
#################
avm_simulation_sources := $(wildcard tests/scenarios/*.avm-simulation)
avm_tests_failing := $(shell cat tests/failing-avm-simulation.list)
avm_tests_passing := $(filter-out $(avm_tests_failing), $(avm_simulation_sources))
teal_sources := $(wildcard tests/teal-sources/*.teal)
all_sources := $(join $(avm_simulation_sources), $(teal_sources))

test-avm-semantics: $(avm_tests_passing:=.unit)

tests/scenarios/%.fail.avm-simulation.unit: tests/scenarios/%.fail.avm-simulation
	$(VENV_ACTIVATE) && ! $(KAVM) run --teal-sources-dir=./tests/teal-sources/ --output none $<

tests/scenarios/%.avm-simulation.unit: tests/scenarios/%.avm-simulation
	$(VENV_ACTIVATE) && $(KAVM) run --teal-sources-dir=./tests/teal-sources/ --output none $<

###########################
## AVM Symbolic Proof Tests
###########################

avm_prove_tests := $(wildcard tests/specs/*-spec.k)

test-avm-semantics-prove: $(avm_prove_tests:=.prove)

tests/specs/%-spec.k.prove: tests/specs/verification-kompiled/timestamp $(KAVM_LIB)/version
	$(KAVM) prove --directory tests/specs tests/specs/$*-spec.k

tests/specs/verification-kompiled/timestamp: tests/specs/verification.k
	$(KAVM) kompile $< --backend haskell --directory tests/specs

#######
## kavm
#######
test-kavm: test-kavm-kast module-imports-graph

## * kavm kast
test-kavm-kast: test-kavm-kast-avm-scenario test-kavm-kast-teal

test-kavm-kast-avm-scenario: $(avm_simulation_sources:=.kavm-kast.unit)

tests/scenarios/%.avm-simulation.kavm-kast.unit: tests/scenarios/%.avm-simulation
	$(VENV_ACTIVATE) && $(KAVM) kast $< --output none

test-kavm-kast-teal: $(teal_sources:=.kavm-kast.unit)

tests/teal-sources/%.teal.kavm-kast.unit: tests/teal-sources/%.teal
	$(VENV_ACTIVATE) && $(KAVM) kast $< --output none

# Utils
# -----

# Generate a graph of module imports
module-imports-graph: module-imports-graph-dot
	dot -Tsvg $(KAVM_LIB)/$(avm_kompiled)/import-graph -o module-imports-graph.svg

module-imports-graph-dot: venv
	$(VENV_ACTIVATE) && pyk graph-imports $(KAVM_LIB)/$(avm_kompiled)

clean: clean-avm clean-kavm venv-clean

distclean: clean
	rm -rf $(BUILD_DIR)
	git clean -dffx -- tests/
