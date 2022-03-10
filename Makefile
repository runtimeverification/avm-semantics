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
KAVM_K_BIN       := $(KAVM_LIB)/kframework/bin
KAVM             := kavm
KAVM_LIB_ABS     := $(abspath $(KAVM_LIB))
export KAVM_LIB_ABS

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
        build build-avm build-kavm                                                    \
        test test-avm
.SECONDARY:

all: build

# Non-K Dependencies
# ------------------

libsecp256k1_out := $(LOCAL_LIB)/pkgconfig/libsecp256k1.pc
libff_out        := $(LOCAL_LIB)/libff.a

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
	cd $(PLUGIN_SUBMODULE)/deps/libff/build                                                               \
	    && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$(BUILD_LOCAL) $(LIBFF_CMAKE_FLAGS) \
	    && make -s -j4                                                                                    \
	    && make install

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

k-deps: $(K_JAR)
	cd $(K_SUBMODULE)                                                                                                                                                                            \
	    && mvn --batch-mode package -DskipTests -Dllvm.backend.prefix=$(INSTALL_LIB)/kframework -Dllvm.backend.destdir=$(CURDIR)/$(BUILD_DIR) -Dproject.build.type=$(K_BUILD_TYPE) $(K_MVN_ARGS) \
	    && DESTDIR=$(CURDIR)/$(BUILD_DIR) PREFIX=$(INSTALL_LIB)/kframework package/package

# Building
# --------

build: build-avm build-kavm

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
                     -L$(LOCAL_LIB)                                    \
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

K_INCLUDES   :=                                         \
                -I $(CURDIR)/$(KAVM_INCLUDE)/kframework \
                -I $(INSTALL_INCLUDE)/kframework        \
                -I $(plugin_include)/kframework
KOMPILE_OPTS += --verbose --gen-glr-bison-parser $(COVERAGE_OPTS) $(K_INCLUDES)

ifneq (,$(RELEASE))
    KOMPILE_OPTS += -O2 --read-only-kompiled-directory
endif

# AVM

avm_files    :=                            \
                avm/additional-fields.md   \
                avm/args.md                \
                avm/blockchain.md          \
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

AVM_KOMPILE_OPTS += --emit-json --verbose $(COVERAGE_OPTS) $(K_INCLUDES)
tangle_avm            := k & ((! type) | exec)

ifeq ($(K_BACKEND),)
  K_BACKEND := llvm
endif

KOMPILE_AVM       := kompile --backend $(K_BACKEND) --md-selector "$(tangle_avm)"          \
                          $(AVM_KOMPILE_OPTS) $(HOOK_KOMPILE_OPTS) $(AVM_HOOK_KOMPILE_OPTS)

avm_dir           := avm-llvm
avm_main_module   := AVM-EXECUTION
avm_syntax_module := TEAL-PARSER-SYNTAX
avm_main_file     := avm/avm-execution.md
avm_main_filename := $(basename $(notdir $(avm_main_file)))
avm_kompiled      := $(avm_dir)/$(avm_main_filename)-kompiled

build-avm: $(KAVM_LIB)/$(avm_kompiled)

$(KAVM_LIB)/$(avm_kompiled): $(avm_includes) $(hook_includes) $(libff_out) $(plugin_includes) $(plugin_c_includes)
	$(KOMPILE_AVM) $(KAVM_INCLUDE)/kframework/$(avm_main_file)                     \
	                --directory $(KAVM_LIB)/$(avm_dir)  \
	                --main-module $(avm_main_module)     \
	                --syntax-module $(avm_syntax_module)

clean-avm:
	rm -r $(KAVM_LIB)/$(avm_kompiled)
	rm -r $(KAVM_INCLUDE)

# Runners/Helpers

kavm_includes := $(teal_includes)
includes      := $(kavm_includes) $(plugin_includes)

kavm_bin_files := kavm
kavm_bins      := $(patsubst %, $(KAVM_BIN)/%, $(kavm_bin_files))

kavm_lib_files := version
kavm_libs      := $(patsubst %, $(KAVM_LIB)/%, $(kavm_lib_files))

build-kavm: $(KAVM_LIB)/version

$(KAVM_LIB)/version: $(includes) $(kavm_bins)

$(KAVM_BIN)/%: %
	@mkdir -p $(dir $@)
	install $< $@

$(KAVM_LIB)/%: lib/%
	@mkdir -p $(dir $@)
	install $< $@

$(KAVM_INCLUDE)/kframework/modules/%:
	echo $@
	@mkdir -p $(dir $@)
	install $< $@

$(KAVM_LIB)/version:
	@mkdir -p $(dir $@)
	echo '== KAVM Version'    > $@
	echo $(KAVM_RELEASE_TAG) >> $@
	echo '== Build Date'     >> $@
	date                     >> $@

clean-kavm:
	rm $(KAVM_BIN)/kavm

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

test: test-avm test-kavm

#################
## AVM Unit Tests
#################
avm_simulation_sources := $(wildcard tests/scenarios/*.avm-simulation)
avm_tests_failing := $(shell cat tests/failing-avm-simulation.list)
avm_tests_passing := $(filter-out $(avm_tests_failing), $(avm_simulation_sources))
teal_sources := $(wildcard tests/teal-sources/*.teal)
all_sources := $(join $(avm_simulation_sources), $(teal_sources))

test-avm: $(avm_simulation_sources:=.unit)

tests/scenarios/%.fail.avm-simulation.unit: tests/scenarios/%.fail.avm-simulation
	! $(KAVM) run $< --output none

tests/scenarios/%.avm-simulation.unit: tests/scenarios/%.avm-simulation
	$(KAVM) run $< --output none

###########################
## AVM Symbolic Proof Tests
###########################

avm_prove_tests := $(wildcard tests/specs/*-spec.k)

test-avm-prove: $(avm_prove_tests:=.prove)

tests/specs/%-spec.k.prove: tests/specs/verification-kompiled/timestamp $(KAVM_BIN)/$(KAVM)
	$(KAVM) prove --backend-dir tests/specs tests/specs/$*-spec.k

tests/specs/verification-kompiled/timestamp: tests/specs/verification.k $(kavm_includes)
	kompile $< --backend haskell --directory tests/specs $(K_INCLUDES)

#######
## kavm
#######
test-kavm: test-kavm-parse test-kavm-kast

## * kavm parse
test-kavm-parse: test-kavm-parse-avm-scenario test-kavm-parse-teal

test-kavm-parse-avm-scenario: $(avm_simulation_sources:=.kavm-parse.unit)

tests/scenarios/%.avm-simulation.kavm-parse.unit: tests/scenarios/%.avm-simulation
	$(KAVM) parse $< > /dev/null 2>&1

test-kavm-parse-teal: $(teal_sources:=.kavm-parse.unit)

tests/teal-sources/%.teal.kavm-parse.unit: tests/teal-sources/%.teal
	$(KAVM) parse $< > /dev/null 2>&1

## * kavm kast
test-kavm-kast: test-kavm-kast-avm-scenario test-kavm-kast-teal

test-kavm-kast-avm-scenario: $(avm_simulation_sources:=.kavm-kast.unit)

tests/scenarios/%.avm-simulation.kavm-kast.unit: tests/scenarios/%.avm-simulation
	$(KAVM) kast $< none

test-kavm-kast-teal: $(teal_sources:=.kavm-kast.unit)

tests/teal-sources/%.teal.kavm-kast.unit: tests/teal-sources/%.teal
	$(KAVM) kast $< none

# Utils
# -----

# Generate a graph of module imports
module-imports-graph: module-imports-graph-dot
	dot -Tsvg $(KAVM_LIB)/$(avm_kompiled)/import-graph -o module-imports-graph.svg

module-imports-graph-dot:
	kpyk $(KAVM_LIB)/$(avm_kompiled) graph-imports

clean: clean-avm clean-kavm

distclean: clean
	rm -rf $(BUILD_DIR)
	git clean -dffx -- tests/
