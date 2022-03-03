Algorand Virtual Machine Semantics in K
=======================================

AVM Files
---------

The AVM semantics source files are located in [`lib/include/kframework/avm/`](lib/include/kframework/avm/):

* [`avm-configuration.md`](lib/include/kframework/avm/avm-configuration.md) defines the top-level K configuration of the AVM:
  - AVM execution state
  - TEAL interpreter state
* [`blockchain.md`](lib/include/kframework/avm/blockchain.md) defines the Algorand network state: accounts, apps and assets.
* [`txn.md`](lib/include/kframework/avm/txn.md) defines the representation of Algorand transactions.
* [`avm-execution.md`](lib/include/kframework/avm/avm-execution.md) defines the execution flow of AVM:
  - transaction evaluation and execution process, depending on its type;
  - starting/stopping TEAL execution;
  - AVM-level panic behaviors;
  - basic syntax of simulation scenarios.
* [`avm-initialization.md`](lib/include/kframework/avm/avm-initialization.md) defines rules that initialize AVM with a specific initial network state and the supplied transaction group;
* [`avm-limits.md`](lib/include/kframework/avm/avm-limits.md) defines the constants that govern AVM execution: max transaction group size, max TEAL stack depth, etc.
* [`avm-txn-deque.md`](lib/include/kframework/avm/avm-txn-deque.md) defines an internal data structure that handles transaction execution schedule.
* [`args.md`](lib/include/kframework/avm/args.md) defines the representation of Logic Signature transaction arguments.

TEAL Interpreter Files
----------------------

Transaction Execution Approval Language (TEAL) is the language that governs approval of Algorand transactions and serves as the execution layer for Algorand Smart Contracts.

The K modules describing syntax and semantics of TEAL are located in [`lib/include/kframework/avm/teal/`](lib/include/kframework/avm/teal/):

* [`teal-types.md`](lib/include/kframework/avm/teal/teal-types.md) defines basic types representing values in TEAL and various operations involving them.
* [`teal-constants.md`](lib/include/kframework/avm/teal/teal-constants.md) defines a set of integer constants TEAL uses, including transaction types and on-completion types.
* [`teal-fields.md`](lib/include/kframework/avm/teal/lib/include/kframework/common/teal-fields.md) defines sets of fields that may be used as arguments to some specific opcodes in TEAL, such as `txn/txna` fields and `global` fields.
* [`teal-syntax.md`](lib/include/kframework/avm/teal/lib/include/kframework/common/teal-syntax.md) defines the syntax of (textual) TEAL and the structure of its programs.
* [`teal-stack.md`](lib/include/kframework/avm/teal/teal-stack.md) defines the K representation of TEAL stack and the associated operations.
* [`teal-execution.md`](lib/include/kframework/avm/teal/teal-execution.md) defines the execution flow of the interpreter:
  - [Interpreter Initialization](lib/include/kframework/avm/teal/teal-execution.md#teal-interpreter-initialization)
  - [Execution](lib/include/kframework/avm/teal/teal-execution.md#teal-execution)
  - [Interpreter Finalization](lib/include/kframework/avm/teal/teal-execution.md#teal-interpreter-finalization)
  - [TEAL Panic Behaviors](lib/include/kframework/avm/teal/teal-execution.md#panic-behaviors)
* [`teal-driver.md`](lib/include/kframework/avm/teal/teal-driver.md) defines the semantics of the various TEAL opcodes and specifies how a TEAL program is interpreted.

`kavm` runner script
--------------------

`kavm` is a shell script that provides a command-line interface for the semantics:
* concrete simulations and tests are run via `krun` and the K LLVM Backend
* symbolic execution proofs are run with `kprovex` and the K Haskell Backend

See `kavm --help` for more information.

`kavm` uses two auxiliary scripts located in [`scripts/`](scripts/):
* [`parse-avm-simulation.sh`](scripts/parse-avm-simulation.sh) calls `kparse` to parse a simulation scenario from a `.avm-simulation` file;
* [`parse-teal-programs.sh`](scripts/parse-teal-programs.sh) calls `kparse` to parse a `;`-separated list of TEAL source codes.

Testing harness
---------------

The tests are located in [`tests/`](tests/). Each test has two components:
* a TEAL program `.teal`, or several programs, in [`tests/teal-sources/`](tests/teal-sources/);
* a test scenario, `.avm-simulation` in [`tests/scenarios/`](tests/scenarios/) that defines the initial network state, the input transaction group and declares which TEAL programs should it uses.

Note that negative test scenarios are mist have the `.fail.avm-simulation` file extension.

Working on KAVM
---------------

### Build system

* `make deps`: build K and other dependencies.
* `make build`: compile KAVM K modules and the `kavm` tool.
* `make test -j8`: run tests. Adjust the `-jX` option as needed to run `X` tests in parallel.

### Adding new tests

TBD

### Managing `PATH` with `direnv`

We use [`direnv`](https://direnv.net/) to manage the environment variables such as `PATH`, see [`.envrc`](.envrc).

After installing `direnv`, run `direnv allow` to activate the settings for the project's directory.

Feel free to ignore `direnv` if you prefer your global installation of K.
