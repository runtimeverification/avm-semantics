# Settings
# --------

UNAME_S := $(shell uname -s)

SHELL = /bin/bash -o pipefail

DEPS_DIR    := deps
BUILD_DIR   := .build
PY_KAVM_DIR := kavm/

KAVM_DEFINITION_DIR=$(shell $(POETRY_RUN) kbuild which llvm)
KAVM_VERIFICATION_DEFINITION_DIR=$(shell $(POETRY_RUN) kbuild which haskell)
export KAVM_DEFINITION_DIR
export KAVM_VERIFICATION_DEFINITION_DIR

# if K_OPTS is undefined, up the default heap size for kompile
ifeq "$(origin K_OPTS)" "undefined"
K_OPTS := -Xmx8G
endif
export K_OPTS

KORE_RPC_PORT := $(if $(KORE_RPC_PORT),$(KORE_RPC_PORT),7777)

all: deps build test
.PHONY: all

deps: plugin-deps k-deps
.PHONY: deps

# Non-K Dependencies
# ------------------

plugin-deps:
	$(MAKE) -C $(DEPS_DIR)/plugin libcryptopp libff libsecp256k1
.PHONY: plugin-deps

# K Dependencies
# --------------

# Semantics
# ---------

build: plugin-deps build-avm generate-parsers build-avm-verification
.PHONY: build

# * avm-semantics --- the K semantics of AVM

POETRY_RUN := poetry run -C kavm

build-avm:
	$(POETRY_RUN) kbuild kompile llvm
.PHONY: build-avm

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
.PHONY: generate-parsers

build-avm-verification:
	$(POETRY_RUN) kbuild kompile haskell
.PHONY: build-avm-verification

## * kavm --- Python library and CLI app

check-kavm-codestyle:
	$(MAKE) check -C $(PY_KAVM_DIR)

# Tests
# -----

KAVM_OPTIONS :=

test: test-kavm-hooks test-kavm test-kavm-avm-simulation test-kavm-algod test-avm-semantics-prove
.PHONY: test


###########################
## Generated Bison parsers tests
###########################

test-kavm-bison-parsers:
	echo $(KAVM_DEFINITION_DIR)
	$(MAKE) test-bison-parsers -C $(PY_KAVM_DIR)
.PHONY: test-kavm-bison-parsers

###########################
## AVM Simulation Scenarios
###########################
test-kavm-avm-simulation:
	$(MAKE) test-scenarios -C ./kavm
.PHONY: test-kavm-avm-simulation

#######
## kavm.algod Python library tests
#######
test-kavm-algod:
	$(MAKE) test-unit -C $(PY_KAVM_DIR)
	$(MAKE) test-integration-kalgod -C $(PY_KAVM_DIR)

############################################
## AVM PyTeal-generated Symbolic Proof Tests
############################################
test-pyteal-prove:
	$(MAKE) test-generated-claims -C $(PY_KAVM_DIR)
.PHONY: test-pyteal-prove

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
.PHONY: test-avm-semantics-prove

test-avm-semantics-kcfg-prove: test-avm-semantics-calls-kcfg-prove
.PHONY: test-avm-semantics-kcfg-prove

test-avm-semantics-internal-prove: $(avm_prove_internal_specs:=.prove)
.PHONY: test-avm-semantics-internal-prove

test-avm-semantics-opcode-prove: $(avm_prove_opcode_specs:=.prove)
.PHONY: test-avm-semantics-opcode-prove

test-avm-semantics-simple-prove: $(avm_prove_simple_specs:=.prove)
.PHONY: test-avm-semantics-simple-prove

test-avm-semantics-calls-prove: $(avm_prove_call_specs:=.prove)
.PHONY: test-avm-semantics-calls-prove

test-avm-semantics-transactions-prove: $(avm_prove_transactions_specs:=.prove)
.PHONY: test-avm-semantics-transactions-prove

test-avm-semantics-pact-prove: $(avm_prove_pact_specs:=.prove)
.PHONY: test-avm-semantics-pact-prove

test-avm-semantics-calls-kcfg-prove: $(avm_prove_call_specs:=.kcfg.prove)
.PHONY: test-avm-semantics-calls-kcfg-prove

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
.PHONY: clean-verification


# Utils
# -----

# Generate a graph of module imports
module-imports-graph: module-imports-graph-dot
	dot -Tsvg $(KAVM_LIB)/$(avm_kompiled)/import-graph -o module-imports-graph.svg
.PHONY: module-imports-graph

module-imports-graph-dot:
	$(POETRY_RUN) && pyk graph-imports $(KAVM_LIB)/$(avm_kompiled)
.PHONY: module-imports-graph-dot

clean: clean-avm clean-kavm clean-verification
.PHONY: clean

distclean: clean
	rm -rf $(BUILD_DIR)
	git clean -dffx -- tests/
.PHONY: distclean
