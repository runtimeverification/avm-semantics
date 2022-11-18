## Try KAVM

### How to install KAVM

#### Install kup tool

The easiest way to install KAVM is provided by the kup tool. To install kup, run the following in your terminal:

```bash
bash <(curl https://kframework.org/install)
```

The installation script will guide you through a simple process that will also install Nix on your system. Once the previous command finishes, which may take some time, `kup` should be available in your shell. To verify the installation, execute:

```
kup list
```

The result should look similar to the following screenshot:

![1](https://user-images.githubusercontent.com/8296326/202644795-897cf3d7-0a7c-4654-8998-4fc838ec632e.png)

Once `kup` is installed, we can proceed to installing `kavm` itself.

#### Install KAVM

In the screenshot above, we see kup reporting that the `kavm` package is available for installation. Proceed by typing `kup install kavm` to install it:

![2](https://user-images.githubusercontent.com/8296326/202645178-324a8bd2-cd8e-4eee-920d-6b4c65dd1241.png)

The installation process may take some time, since `kavm` will be built from source, together with its dependencies (can we provide a cached build?).

### Test a PyTeal smart contract with KAVM

In this tutorial, we'll look at how KAVM can be used to test a simple Algorand smart contract implemented in PyTeal. KAVM is compatible with `py-algorand-sdk`, which makes it possible to not only use the full power of Python's testing libraries such as `pyetst` and `hypothesis`, but to fully **reuse** Python scripts that deploy PyTeal smart contracts for testing with KAVM.

#### The Calculator contract

We will use the [Calculator](https://github.com/runtimeverification/avm-semantics/blob/pyteal-calculator/kavm/src/tests/algod_integration/contracts/calculator/contract.py) contract as the example of this tutorial. This very simple contract example is provided by Algorand [devrel](https://github.com/algorand-devrel/beaker-calculator/tree/main/calculator-pyteal) and suites perfectly for tutorials like this one, since it is concise, but still has a lot in common with real Algorand smart contracts.

The contract uses the PyTeal `Router` abstraction to define the [ABI](https://pyteal.readthedocs.io/en/stable/abi.html) of the contract, and plug the methods implementations into it. The router abstraction makes the implementation in PyTeal very concise:

```python
router = Router(
    # Name of the contract
    name="calculator",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction.never(),
        delete_application=OnCompleteAction.never(),
        clear_state=OnCompleteAction.never(),
    ),
)

@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """sum a and b, return the result"""
    return output.set(a.get() + b.get())

@router.method
def sub(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """subtract b from a, return the result"""
    return output.set(a.get() - b.get())

@router.method
def mul(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """multiply a and b, return the result"""
    return output.set(a.get() * b.get())

@router.method
def div(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """divide a by b, return the result"""
    return output.set(a.get() / b.get())
```

The contract has four ABI methods (Python functions marked with `@router.method` decorator) for four binary arithmetic operations: addition, subtraction, multiplication and division. Besides the ABI methods, the contract accepts only one [*bare call*](https://pyteal.readthedocs.io/en/stable/abi.html#creating-an-arc-4-program), which facilitate application deployment (creation of the application in the Algorand blockchain). All other bare calls, such as application code update, deletion and clear state are rejected.

#### Testing the contract with KAVM

To test PyTeal contracts, the developers have to *deploy* them, since the source code above cannot be executed directly. The usual deployment workflow is to compile the contract's source code to TEAL, the executable language of the Algorand blockchain, and submit an application call transaction to an Algorand node that will create the contract. Interaction with the created contract is then done by submitting more application call transactions.

KAVM works a little differently. KAVM is not an implementation of the Algorand node, but rather a simulation and formal verification tool for Algorand smart contracts. Therefore, KAVM runs locally on the developers machine, almost like the Algorand [Sandbox](https://github.com/algorand/sandbox). However, in contracts to the Sandbox, there is no HTTP communication involved when interacting with KAVM, therefore the gap between the Python testing/deployment script and the execution engine is much narrower.

With all that being said, we do not want the developers to think too much about the implementation details! Thus, we have designed KAVM to integrate well with `py-algorand-sdk`, making it possible to interact with KAVM almost as if it were, in fact, and Algorand node.

Enough talking! Let's get our hand dirt and simulate the calculator contract deployment with KAVM!

#### Deploying a smart contact with KAVM and `py-algorand-sdk`

Smart contracts must be deployed by *somebody* --- an existing Algorand account that will submit he application call to create the contract. We generate a fresh account that we will initialize the KAVM with. By default, KAVM will treat the account as a faucet and give it a big supply of Algos:

```python
    creator_private_key, creator_address = account.generate_account()
    client = KAVMClient(str(creator_address))
```

Then, we need to compile the PyTeal source code of the contract into the binary representation we could submit as part of a transaction. Assuming that the source code is located in the `contract.py` file (see the end of this tutorial to links for complete examples), we can execute the command:

```
$ python contract.py
```

which should create the approval and clear state TEAL programs. We can verify that these programs are created:

```
$ ls | grep teal
approval.teal
clear.teal
```

Getting back to our Python deployment script, let's compile the TEAL sources into the binary code:

```python
    # Read in approval and clear TEAL programs
    with open("approval.teal") as f:
        approval_source = f.read()
    with open("clear.teal") as f:
        clear_source = f.read()
    # Compile approval and clear TEAL programs
    approval_program = compile_program(client, approval_source)
    clear_program = compile_program(client, clear_source)
```

Now we need to bundle the compiled programs into a transaction that will deploy the contract, sign the transaction and get its unique identifier:

```python
    # create unsigned transaction
    txn = future.transaction.ApplicationCreateTxn(
        sender=creator_address,
        sp=client.suggested_params(),
        on_complete=future.transaction.OnComplete.NoOpOC.real,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=None,
        local_schema=None,
    )
    # sign transaction
    signed_txn = txn.sign(creator_private_key)
    tx_id = signed_txn.transaction.get_txid()
```

The important arguments of the `ApplicationCreateTxn` initializer are `sender`, which we set to the creator's address, and the `approval_program` and `clear_state_program`, which are the binary code of the contract.

Finally, we need to submit the transaction and make sure that KAVM has verified and confirmed it: 

```
    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    confirmed_txn = future.transaction.wait_for_confirmation(client, tx_id, 4)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app with app-id ", app_id)
```

That's it! Now we can jump to the interesting part: we will simulate the calls to smart contract and use [Hypothesis](https://hypothesis.readthedocs.io/en/latest/index.html), the Python property testing framework to find out which calls will cause the contract to reject our calls.

#### Interacting with the contract

First off, we will turn our calculator smart contract into a command-line executable, so we can easily call any of it's methods from our shell:

```
if __name__ == '__main__':
    _, method_name, x, y = sys.argv
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(
        app_id, contact.get_method_by_name(method_name), caller_addr, sp, signer, method_args=[int(x), int(y)]
    )
    try:
        resp = comp.execute(client, 2)
        for result in resp.abi_results:
            print(f"{result.method.name} => {result.return_value}")
    except error.AlgodHTTPError as e:
        print(json.dumps(client._last_scenario.dictify(), indent=2))
        print(f'^^^^^^^^^^^^^^^^^^ Last attempted scenario ^^^^^^^^^^^^^^^^^^')
        print(f'KAVM has failed to execute contract\'s method {method_name} with arguments {x} and {y}')
```

We use the slightly modified version of `py-algorand-sdk`'s [`AtomicTransactionComposer`](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/atomic_transaction_composer.html?highlight=Atomic#algosdk.atomic_transaction_composer.AtomicTransactionComposer) class to make a call to the contract's methods.

We can now use the KAVM and the contract as a very weird, well, calculator:

```bash
$ python interact_kavm.py add 1 2
TXID:  P5VCGT7OUAZYFY4A6CLMA4WOPIR2J55NPZCY7Q5NA2UTTE6DHQ5A
Result confirmed in round: 1
Created new app with app-id  1
add => 3
```

Hooray! The contract was "deployed" onto KAVM and the method `'add'` was executed with the arguments `1` and `2`, giving `3` as the result. Let's execute a couple of more calls:

```bash
$ python interact_kavm.py mul 100 3
TXID:  ZZFAX54Q342B56KFH3NQKS3EILDMM5YBJUVFR5A7HDUX6L7LXJQA
Result confirmed in round: 1
Created new app with app-id  1
mul => 300

$ python interact_kavm.py sub 100 99
TXID:  GRFTR7FQ3XEONRU7ROCSOZIMKLOWAFUW2K6JTKART6SLNFWFMXAA
Result confirmed in round: 1
Created new app with app-id  1
sub => 1
```

Let's now do something naughty:

```bash
$ python interact_kavm.py div 42 0
TXID:  RW6VVGFPNN4X4XJWKFRVQEUOAZGTW33XWZNVM3FARQILUKJEZF6A
Result confirmed in round: 1
Created new app with app-id  1
Contract has regected the call to method div with arguments 42 and 0
```

It's not surprise that the contract's approval program refused the transaction that tried to divide by zero. However, we only now which arguments are undesirable because the contact is very simple: it's just a calculator! If it was something more complicated, we'd need some more advanced methods to find the bad inputs. Let's try out one such method on this simple example.

#### Testing the contract with Hypothesis

[Hypothesis](https://hypothesis.readthedocs.io/en/latest/index.html) is a property testing framework that integrates well with `pytest` and provides an easy way to run any Python function with randomized inputs. The idea it is run the methods of the calculator contracts with integer arguments generated according to a certain *strategy* and find out which arguments cause the contract to reject the transaction.

Let's declare a test function to execute the described scenario:

```python
MAX_ARG_VALUE = 2**64 - 1
MIN_ARG_VALUE = MAX_ARG_VALUE / 4

@settings(deadline=(timedelta(seconds=2)), max_examples=25, phases=[Phase.generate])
@given(
    x=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
    y=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
)
def test_method_add(x: int, y: int) -> Optional[int]:
    method_name = 'add'
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(app_id, contact.get_method_by_name(method_name), caller_addr, sp, signer, method_args=[x, y])
    resp = comp.execute(client, 2)
    assert resp.abi_results[0].return_value == x + y
```

You can easily see that this is just a modified variant of the `__main__` function that we wrote to try the contact out, specialized to the `'add'` method. We ask Hypothesis to generate 25 pairs of integer numbers in certain range and run the code on every input. At the end, we assert that the result returned by the contract is in fact the sum. Let's run the tests with `pytest` and see what happens:

```bash
$ python -m pytest --tb=short --hypothesis-show-statistics interact_kavm.py
...
E   algosdk.error.AlgodHTTPError: KAVM has failed, rerun witn --log-level=ERROR to see the executed JSON scenario
E   Falsifying example: test_method_add(
E       x=4611686018427423219, y=17205414141096452043,
E   )
--------------------------------- Captured stdout setup ---------------------------------
TXID:  2HLZPUBA5AC4O3ZEM5GGNRAE6TLBXT47OKGT3Q2JSCB3ZJE3FPHA
Result confirmed in round: 1
Created new app with app-id  1
================================= Hypothesis Statistics =================================
interact_kavm.py::test_method_add:

  - during generate phase (2.27 seconds):
    - Typical runtimes: 277-470 ms, ~ 0% in data generation
    - 6 passing examples, 1 failing examples, 0 invalid examples
    - Found 1 distinct error in this phase

  - Stopped because nothing left to do
```

Hypothesis found a pair of inputs that causes the contract to reject the transaction! Why? Remember that TEAL operates with integer of type `uint64`, i.e. we try to add to values that generate a result greater than `2**64 - 1`, the TEAL's `+` opcode will trigger an integer overflow error, halting the program and rejecting the calling transaction.
