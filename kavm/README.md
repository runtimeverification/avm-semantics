# kavm

KAVM integration with `py-algorand-sdk` and Algorand Sandbox

UNDER CONSTRUCTION


## Installation

Prerequsites: `python 3.8.*`, `pip >= 20.0.2`, `poetry >= 1.2.0`.

```bash
make build
pip install dist/*.whl
```


## For Developers

Use `make` to run common tasks (see the [Makefile](Makefile) for a complete list of available targets).

* `make build`: Build wheel
* `make check`: Check code style
* `make format`: Format code
* `make test-unit`: Run unit tests
* `make test-integration`: Run integration tests (see below)

For interactive use, spawn a shell with `poetry shell` (after `poetry install`), then run an interpreter.


### Working with vanilla Algorand Sandbox (without KAVM)

The `kavm_algod/tests/contracts` directory has a number of integration tests that deploy example smart contracts into an Algorand Sandbox and test them.
We use the modified Algorand Sandbox Docker image created by [MakerX](https://github.com/MakerXStudio/algorand-sandbox-dev). To work on the tests, you need `docker` and `docker-compose` installed and configured.

Use `docker-compose up -d` to start the sandbox and `docker-compose down` to stop it.

To run the integration tests, execute `make test-integration` with the **sandbox active**.

### Profiling

We use [`pytest-profiling`](https://pypi.org/project/pytest-profiling/) to generate profiling data for `kavm`.

#### Suites of tests

The `kavm/Makefile` has targets chat allow running unit/integration test-suites with profiling enabled. For example, run the following to profile the unit tests:

```bash
make clean-profiling # remove previos profiling artefacts
PYTEST_PROFILING=1 THREADS=4 make test-unit
make transient-profiling-report > profiling-report-unit.md
```

#### Individual tests/scripts


The approach is as follows:
1. Run a test file (or several) to collect profiling information into a `.prof` binary file
2. Run a script that will analyze the `.prof` file and present the relevant results as a Markdown table

For example, here are the steps required to profile `kavm/src/tests/algod_integration/test_faucet.py`:

1. Change into the `kavm` directory
2. Run the test with `--profile` and using the KAVM backend (`kalgod`):

```bash
poetry run python -m pytest --profile --backend=kalgod src/tests/algod_integration/test_faucet.py # run the test with KAVM
```
3. The command above will create a `./prof` directory containing the following files:
```bash
$ ls ./prof
combined.prof  test_faucet.prof  test_faucet_separate_groups.prof
```
The `combiled.prof` file contains the profiling information gathered over the whole test file execution, and the other two files are restricted to the two individual test functions.
4. Run the analysis script to obtain a summary table:
```bash
poetry run python src/profiling/__main__.py ./prof/combined.prof > prof/table.md
```
5. The generated table can be shared on GitHub and will be rendered nicely:

| function                                                    |   cumtime |   percall_cumtime | ncalls   |
|-------------------------------------------------------------|-----------|-------------------|----------|
| src/kavm/algod.py:145[_handle_post_requests]                |    30.507 |            10.169 | 3        |
| src/kavm/kavm.py:225[eval_transactions]                     |    23.749 |             7.916 | 3        |
| src/kavm/kavm.py:415[_run_with_current_config]              |    16.804 |             5.601 | 3        |
| src/kavm/kavm.py:449[run_term]                              |     9.212 |             3.071 | 3        |
| src/kavm/kavm.py:134[kast]                                  |     7.408 |             2.469 | 3        |
| src/kavm/algod.py:72[algod_request]                         |    30.564 |             1.91  | 16       |
| src/kavm/adaptors/transaction.py:217[transaction_from_k]    |     6.818 |             1.705 | 4        |
| src/kavm/adaptors/transaction.py:102[transaction_to_k]      |    13.517 |             1.69  | 8        |
| src/kavm/kavm.py:288[_initial_config]                       |     2.06  |             1.03  | 2        |
| src/kavm/kavm.py:194[_empty_config]                         |     2.045 |             1.023 | 2        |
| src/kavm/kavm.py:358[simulation_config]                     |     0.06  |             0.02  | 3        |
| src/kavm/pyk_utils.py:119[extractor]                        |     6.836 |             0.008 | 871/860  |
| src/kavm/pyk_utils.py:69[carefully_split_config_from]       |     0.036 |             0.006 | 6        |
| src/kavm/algod.py:94[_handle_get_requests]                  |     0.056 |             0.004 | 13       |
| src/kavm/pyk_utils.py:152[k_cell]                           |     0.011 |             0.002 | 20/5     |
| src/kavm/adaptors/account.py:70[account_cell]               |     0.01  |             0.001 | 15       |
| src/kavm/adaptors/account.py:94[to_account_cell]            |     0.01  |             0.001 | 15       |
| src/kavm/adaptors/account.py:98[from_account_cell]          |     0.015 |             0.001 | 11       |
| src/kavm/pyk_utils.py:47[split_direct_subcells_from]        |     0.012 |             0.001 | 11       |
| src/kavm/algod.py:19[msgpack_decode_txn_list]               |     0.004 |             0.001 | 6        |
| src/kavm/pyk_utils.py:12[maybe_tvalue]                      |     0.01  |             0     | 640      |
| src/kavm/pyk_utils.py:82[_replace_with_var]                 |     0.022 |             0     | 540      |
| src/kavm/pyk_utils.py:79[_mk_cell_var]                      |     0.004 |             0     | 246      |
| src/kavm/pyk_utils.py:40[tvalue_list]                       |     0.001 |             0     | 48       |
| src/kavm/kavm.py:62[accounts]                               |     0     |             0     | 44       |
| src/kavm/pyk_utils.py:27[tvalue]                            |     0     |             0     | 32       |
| src/kavm/adaptors/transaction.py:82[txid]                   |     0     |             0     | 18       |
| src/kavm/adaptors/transaction.py:295[txn_type_to_type_enum] |     0     |             0     | 8        |
| src/kavm/kavm.py:204[current_config]                        |     0     |             0     | 6        |
| src/kavm/kavm.py:208[transactions_cell]                     |     0     |             0     | 5        |
| src/kavm/adaptors/transaction.py:86[sdk_txn]                |     0     |             0     | 4        |
| src/kavm/adaptors/transaction.py:91[transaction_cell]       |     0     |             0     | 4        |
| src/kavm/kavm.py:74[next_valid_txid]                        |     0     |             0     | 4        |
| src/kavm/kavm.py:279[_commit_transaction]                   |     0     |             0     | 4        |
| src/kavm/kavm.py:58[logger]                                 |     0     |             0     | 3        |
| src/kavm/kavm.py:190[_patch_symbol_table]                   |     0     |             0     | 2        |
| src/kavm/algod.py:66[set_log_level]                         |     0     |             0     | 2        |
| src/kavm/adaptors/application.py:1[<module>]                |     0     |             0     | 1        |
| src/kavm/adaptors/application.py:14[KAVMApplication]        |     0     |             0     | 1        |

The generated table includes the functions from the `kavm` package and is sorted by the average cumulative time per call (`percall_cumtime`). Customisation and extension of the analysis script (`kavm/src/profiling/__main__.py`) is encouraged!
