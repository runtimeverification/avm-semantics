# KAVM integration with `py-algorand-sdk` and Algorand Sandbox

UNDER CONSTRUCTION

## Working with vanilla Algorand Sandbox (without KAVM)

The `kavm_algod/tests/contracts` directory has a number of integration tests that deploy example smart contracts into an Algorand Sandbox and test them.
We use the modified Algorand Sandbox Docker image created by [MakerX](https://github.com/MakerXStudio/algorand-sandbox-dev). To work on the tests, you need `docker` and `docker-compose` installed and configured.

Use `docker-compose up -d` to start the sandbox and `docker-compose down` to stop it.

To run the integration tests, execute `make test-integration` with the **sandbox active**.
