import base64
import json
import os
import sys
from datetime import timedelta
from typing import Any, Optional

from algosdk import abi, account, error, future
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from kavm.algod import KAVMAtomicTransactionComposer, KAVMClient


# def create_app(
#     client,
#     sender,
#     private_key,
#     approval_program,
#     clear_program,
#     global_schema,
#     local_schema,
# ):

#     # declare on_complete as NoOp
#     on_complete = future.transaction.OnComplete.NoOpOC.real

#     # get node suggested parameters
#     params = client.suggested_params()
#     params.flat_fee = True
#     params.fee = 1000

#     # create unsigned transaction
#     txn = future.transaction.ApplicationCreateTxn(
#         sender,
#         params,
#         on_complete,
#         approval_program,
#         clear_program,
#         global_schema,
#         local_schema,
#     )

#     # sign transaction
#     signed_txn = txn.sign(private_key)
#     tx_id = signed_txn.transaction.get_txid()

#     # send transaction
#     client.send_transactions([signed_txn])

#     # await confirmation
#     confirmed_txn = future.transaction.wait_for_confirmation(client, tx_id, 4)
#     print("TXID: ", tx_id)
#     print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))

#     # display results
#     transaction_response = client.pending_transaction_info(tx_id)
#     app_id = transaction_response["application-index"]
#     print("Created new app-id: ", app_id)

#     return app_id


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def setup() -> Any:
    creator_private_key, creator_address = account.generate_account()

    # Manually setup Algod Client
    client = KAVMClient(str(creator_address))
    client.algodLogger.disabled = True

    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval and clear TEAL programs
    with open(os.path.join(path, "./approval.teal")) as f:
        approval_source = f.read()
    with open(os.path.join(path, "clear.teal")) as f:
        clear_source = f.read()

    # Compile approval and clear TEAL programs
    approval_program = compile_program(client, approval_source)
    clear_program = compile_program(client, clear_source)

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

    # read json and create ABI Contract description
    with open(os.path.join(path, "contract.json")) as f:
        js = f.read()
    c = abi.Contract.from_json(js)
    return client, c, app_id, creator_address, creator_private_key


client, contact, app_id, caller_addr, caller_private_key = setup()
sp = client.suggested_params()
signer = AccountTransactionSigner(caller_private_key)

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


if __name__ == '__main__':
    _, method_name, x, y = sys.argv
    client.algodLogger.setLevel('ERROR')
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
        print(f'Contract has regected the call to method {method_name} with arguments {x} and {y}')
