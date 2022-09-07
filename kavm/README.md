# kavm

KAVM integration with `py-algorand-sdk` and Algorand Sandbox

UNDER CONSTRUCTION


## Installation

Prerequsites: `python 3.8.*`, `pip >= 20.0.2`, `poetry >= 1.1.14`.

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
