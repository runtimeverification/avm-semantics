from datetime import timedelta
import os
import sys

from algosdk import error

from hypothesis import find, settings, Verbosity, assume, Phase
from hypothesis import example, given, settings, strategies as st

from algosdk.v2client.algod import *
from algosdk.atomic_transaction_composer import *
from algosdk.future import *
from algosdk.abi import *
from algosdk.mnemonic import *
from algosdk.account import *

from kavm.algod import KAVMClient, KAVMAtomicTransactionComposer

# Need to define helper methods
def create_app(
    client,
    sender,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
):

    # declare on_complete as NoOp
    on_complete = future.transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = future.transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    confirmed_txn = future.transaction.wait_for_confirmation(client, tx_id, 4)
    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id: ", app_id)

    return app_id


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def setup() -> Any:
    faucet_private_key, faucet_address = generate_account()
    kavm_faucet = {'address': faucet_address, 'private_key': faucet_private_key}

    # Manually setup Algod Client
    client = KAVMClient("a" * 64, "http://localhost:4001", kavm_faucet['address'])
    client.algodLogger.disabled = True

    addr, sk = (kavm_faucet['address'], kavm_faucet['private_key'])

    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval and clear TEAL programs
    with open(os.path.join(path, "./approval.teal")) as f:
        approval_source = f.read()

    with open(os.path.join(path, "clear.teal")) as f:
        clear_source = f.read()

    # Compile approval and clear TEAL programs
    approval_program = compile_program(client, approval_source)
    clear_program = compile_program(client, clear_source)

    # define empty application state storage shema
    # global_schema = future.transaction.StateSchema(global_ints, global_bytes)
    # local_schema = future.transaction.StateSchema(local_ints, local_bytes)

    # create new application
    app_id = create_app(
        client,
        addr,
        sk,
        approval_program,
        clear_program,
        global_schema=None,
        local_schema=None,
    )

    # read json and create ABI Contract description
    with open(os.path.join(path, "contract.json")) as f:
        js = f.read()
    c = Contract.from_json(js)
    return client, c, app_id, addr, sk


def call_methods(client, contact, app_id, caller_addr, caller_private_key):
    sp = client.suggested_params()
    signer = AccountTransactionSigner(caller_private_key)
    comp = KAVMAtomicTransactionComposer()

    comp.add_method_call(app_id, contact.get_method_by_name("sub"), caller_addr, sp, signer, method_args=[2, 1])

    comp.add_method_call(app_id, contact.get_method_by_name("div"), caller_addr, sp, signer, method_args=[8, 4])

    comp.add_method_call(app_id, contact.get_method_by_name("add"), caller_addr, sp, signer, method_args=[1, 2])

    comp.add_method_call(app_id, contact.get_method_by_name("mul"), caller_addr, sp, signer, method_args=[2, 2])

    resp = comp.execute(client, 2, override_tx_ids=list(map(str, [0, 1, 2, 3])))
    for result in resp.abi_results:
        print(f"{result.method.name} => {result.return_value}")


client, contact, app_id, caller_addr, caller_private_key = setup()
sp = client.suggested_params()
signer = AccountTransactionSigner(caller_private_key)

MAX_ARG_VALUE = 2**64 - 1
MIN_ARG_VALUE = MAX_ARG_VALUE / 4


@settings(deadline=(timedelta(seconds=2)), max_examples=25, phases=[Phase.generate])
@given(
    method_name=st.just('add'),
    x=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
    y=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
)
def test_call_method(method_name: str, x: int, y: int) -> Optional[int]:
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(app_id, contact.get_method_by_name(method_name), caller_addr, sp, signer, method_args=[x, y])
    resp = comp.execute(client, 2)
    assert resp.abi_results[0].return_value == x + y


if __name__ == '__main__':
    _, method_name, x, y = sys.argv
    client.algodLogger.setLevel('ERROR')
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(
        app_id, contact.get_method_by_name(method_name), caller_addr, sp, signer, method_args=[int(x), int(y)]
    )
    try:
        resp = comp.execute(client, 2)
        print(resp.abi_results[0].return_value)
    except error.AlgodHTTPError as e:
        print(json.dumps(client._last_scenario.dictify(), indent=2))
        print(f'^^^^^^^^^^^^^^^^^^ Last attempted scenario ^^^^^^^^^^^^^^^^^^')
        print(f'KAVM has failed to execute contract\'s method {method_name} with arguments {x} and {y}')
