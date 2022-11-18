## AVM Smart Contract Testing

With the introduction of KAVM, Runtime Verification aims to provide developers with the go-to solution for testing Algorand smart contract pre-deployment. For all intents and purposes, KAVM gives you a drop-in replacement of Algorand Sandbox, and additional features on top. And you don’t even need to know anything about K to use KAVM. KAVM is tightly integrated with py-algorand-sdk, enabling you to run your existing test-suites for PyTeal contracts on top of KAVM. With KAVM and py-algorand-sdk, you can leverage Python’s abundance of testing packages such as pytest and Hypothesis to test your PyTeal contracts. Just like with Algorand Sandbox, but faster!

Property-based testing (like with Hypothesis) probes your code with random inputs. However, the actual input space is too large to try all possible combinations. That’s where KAVM gives you an easy transition to formal verification of your properties. Imagine you could formally prove that your properties hold instead of just testing them. This feature will leverage K’s symbolic execution backend.

## Try KAVM

### Install kup tool

The easiest way to install KAVM is provided by the kup tool. To install kup, run the following in your terminal:

```bash
bash <(curl https://kframework.org/install)
```

The installation script will guide you through a simple process that will also install Nix on your system. Once the previous command finishes, which may take some time, `kup` should be available in your shell. To verify the installation, execute:

```
kup list
```

The result should look similar to the following screenshot:

 Upon installation, execute `kup list` to see the K packages available for installation:
