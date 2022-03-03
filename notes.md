We need to design a test harness for KAVM. We have the following challenges:

* Integrate the legacy TEAL test harness.
* Develop a new test harness that would make it easy to write end-to-end test vectors and make it as easy as possible to integrate client's tests.

Let's expand on these challenges.

## The legacy TEAL test harness

In the previous interaction, this semantics' main focus was TEAL. TEAL programs are always executed withing a *single transaction*, hence the semantics only modeled the execution of one specific transaction in the group. The current iteration of the semantics models AVM as a whole, and considers the execution of a *transaction group*, which may require evaluation of several TEAL programs associated with distinct transactions in the group. The group may also contain transactions that do not need to execute TEAL. These have their signatures validated and are applied to the network, changing the balances, etc.

The difference between the legacy tests and the new tests is how the initial state is supplied.

The legacy testing harness picks up *single* a TEAL program from a specific `.teal` file and passes it to the semantics, which contains a *hard-coded initial state and transaction group* for testing, defined in `env-init.md`[https://github.com/runtimeverification/avm-semantics/blob/master/lib/include/kframework/avm/env-init.md].

The new testing harness will have a mechanism to define the *initial state and transaction group from outside the semantics* and supply *multiple* `.teal` files to be attached to specific transactions in the group.

To integrate the legacy tests, we will need to export the old hard-coded initial state and transaction group into the new external format and use the new workflow to run the tests.

## The new KAVM test harness

The new test harness needs to be much more versatile than the old ad-hoc one.

Test vectors will define:
* a definition of the initial network state: accounts, ASAs, applications (smart contracts).
* a definition of the input transaction group. LogicSig transactions will need access to stateless TEAL code that was used to sign them.
* TEAL progams, as `.teal` files probably, that will be used in app initialisation.

Note that the surface syntax of test vector definitions must not be KAVM-specific. It would be great to share the test vectors, or at least the framework to define them, with `PyTeal_eval`. We would also like to easily integrate tests that clients brings us for audits.

### The `go-algorand` AVM test-suite

The official Algorand node implementation, `go-algorand` has an extensive test-suite for AVM-related functionality that we would like to eventually be able to replicate. Naturally, their tests interact with a sandboxed private Algorand network, which is not something we want to do in this tool, at least not yet.

The AVM-related tests located in [`go-algorand/test/scripts/e2e_subs/`](https://github.com/algorand/go-algorand/tree/master/test/scripts/e2e_subs) comprise a collection of bash (old) and Python (new) based scripts that, in fact, follow the structure that we have outlined above. Each test file sets up the initial state and input transaction group by issuing Algorand transactions. The older bash-based tests use the command-line too `goal` to do that, and the newer Python-based tests do the same via thin wrapper over `py-algorand-sdk` called [`goal.py`](https://github.com/algorand/go-algorand/blob/master/test/scripts/e2e_subs/goal/goal.py). From what I've gathered, the Python-based scripts are the current method to add new tests.

#### Motivation for adopting Python-based `go-algorand` test workflow in KAVM

Eventually, we would like to integrate the whole `go-algorand` AVM test-suite into KAVM to ensure that our semantics is faithful with respect to the reference implementation. Moreover, many clients will write their smart contracts in PyTeal and use `py-algorand-sdk` in their own test-suites. We, therefore, consider it prudent to come up with a way to integrate `py-algorand-sdk` in some way into our test harness for KAVM.

#### Mocking `py-algorand-sdk` and the `goal` command line tool.

Both `py-algorand-sdk` and the `goal` command-line tool are front-ends to the underlying ABI of Algorand. We need to come up with an interface that would would abstract both.

A good start, I think, is to mock the operations used in [`goal.py`](https://github.com/algorand/go-algorand/blob/master/test/scripts/e2e_subs/goal/goal.py) and force them to produce the chunks of K definitions that are used in KAVM to specify the network state and transaction groups. That would enable us to pick up the test files from `go-algorand` and use them in KAVM without modification. The challenge here is that the tests actually interact with a live node to receive things like addresses and IDs of created accounts and apps, signing transactions etc. We will need to mock these operations somehow.

## Future work: KAVM + Algorand JSON API and messagepack API handling in K = AlgoFirefly

Ultimately, we would like to eliminate the middlemen, which both `py-algorand-sdk` are `goal`, and parse the underlying messages, JSON or binary msgpack, in the K semantics directly. That would enable us to support whatever SDK our clients use in their project.

## References

* [`go-algorand`](https://github.com/algorand/go-algorand) --- Algorand reference implementation
* [`goal`](https://github.com/algorand/go-algorand/tree/041e1f92d9c190bdc6d6c78b1dd04ef19b8ec03b/cmd/goal) --- a command-line tool to interact with an Algorand network
* [`py-algorand-sdk`](https://py-algorand-sdk.readthedocs.io/en/latest/index.html) --- the docs for the Python SDK to interact with an Algorand network
* [`msgpacktool`](https://github.com/algorand/go-algorand/blob/master/cmd/msgpacktool/main.go) ---  a `go-algorand` tool that converts between msgpack and JSON encoding.

------------------------------------------------------------------------------------

## KAVM and `go-algorand` co-simulation

We would like KAVM to be correct and faithful with respect to the AVM/TEAL semantics implemented by `go-algorand`, the reference implementation of an Algorand node. One way to achieve that is to co-simulate test scenarios in both `go-algorand` and KAVM, with the following flow:

* Inside a Python driver, we execute one of the `go-algorand` [AVM end-to-end tests](https://github.com/algorand/go-algorand/tree/master/test/scripts/e2e_subs)
* As we go, we record the relevant state alterations and collect them into a KAVM-friendly representation;
* Once the test scenario has finished executing, we replay it in KAVM using the accumulated KAVM-friendly scenario;
* We check that the approve/deny outcome for the tested transaction group is the same.

**Pros**:

A relatively cheap way to directly use the whole `go-algorand` AVM test suite to test our semantics

**Contras**:

Slow, since requires running a sandboxed network. One test scenario will take several seconds, and there are dozens of those.

--------------------------------------------------------------------------------------

## Lightweight Python test driver

We need a concise way to describe complex test vectors for KAVM.

In the other project, `PyTeal_eval`, @vasil is in the process of solving very similar challenge, and we would like to join forces and share the same surface test description API.

### Short-term goal

Emit strings that would contain K terms that will be passed as values to the `$PGM` configuration variable to `kavm`.

#### Network state

For example, the following `PyTeal_eval`-like pseudocode:

```python
    acc = Account(address="1")                       # new account
    app = Application(app_id=1, creator_address="1") # new app
    asa = Asset(asset_id="42", creator_address="1") # new asset
```

would produce the following K term (excluding comments):

```k
addAccount <address> b\"1\" </address>";
addApp     <appID> 1 </appID> <address> b\"1\" </address> 0";      // the address is the creator's address
addAsset   <assetID> 42 </assetID> <address> b\"1\" </address> 0"; // the address is the creator's address
```

The relevant K rules are now located in the `avm-initialization.md` file of [`algorand-sc-semantics/kteal-prime`](https://github.com/runtimeverification/algorand-sc-semantics/blob/kteal-prime/modules/avm/avm-initialization.md), pending migration to this repo.

Note that here we are being unnecessarily verbose on the `PyTeal_eval` part: many of the constructor arguments may be omitted and provided with generated values. The K terms, however, will need to be precise and include all the information that was generated by `PyTeal_eval`.

#### Transaction group

Similarly to the network state, the tool will emit K terms for specifying transactions:

```python
txn[0] = Transaction(type="appl", sender="1", app_id=1, on_completion=0, accounts=[1])
```

```k
addAppCallTx <txID>            0        </txID>
             <sender>          b\"1\"   </sender>
             <applicationID>   1        </applicationID>
             <onCompletion>    0        </onCompletion>
             <accounts>        b\"1\"   </accounts>;
```

The KAVM semantics will handle bundling of the transactions into a group internally.

Same remark regarding the verbosity in `PyTeal_eval` constructors applies: many of the constructor arguments may be omitted and provided with generated values. The K terms, however, will need to be precise and include all the information that was generated by `PyTeal_eval`.

### Long-term goal

The `PyTeal_eval` will eventually support integrate `py-algorand-sdk` to work with real blockchain data, while retaining the same lightweight format for test scenarios. If made compatible, KAVM will benefit from this too, with the ad-hoc passing of K terms upgraded to a more robust communication protocol.

## Modules needed by AlgoClairy

```
clarity-vm-state.md
4:requires "../common/txn.md"
5:requires "../common/buffered-io.md"
6:requires "../common/json-ext.md"
9:requires "../common/additional-fields.md"

clarity-vm-tealgen.md
7:requires "../common/teal-syntax.md"

clarity-vm-cost.md
2:requires "../common/teal-types.md"
```

`algod.md` seems to not be required by any module, including the AlgoClarity ones. Remove?
`additional-fields.md`
