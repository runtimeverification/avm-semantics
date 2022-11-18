import os

from algosdk.abi import *
from algosdk.account import *
from algosdk.atomic_transaction_composer import *
from algosdk.future import *
from algosdk.mnemonic import *
from algosdk.v2client.algod import *
from sandbox import get_accounts


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
    # comment out the next two (2) lines to use suggested fees
    # params.flat_fee = True
    # params.fee = 1000

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


# Manually setup Algod Client
client = AlgodClient("a" * 64, "http://localhost:4001")

addr, sk = get_accounts()[0]

path = os.path.dirname(os.path.abspath(__file__))

# Read in approval and clear TEAL programs
with open(os.path.join(path, "./approval.teal")) as f:
    approval_source = f.read()

with open(os.path.join(path, "clear.teal")) as f:
    clear_source = f.read()

# Compile approval and clear TEAL programs
approval_program = compile_program(client, approval_source)
clear_program = compile_program(client, clear_source)

# declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 1
global_bytes = 0

# define schema
global_schema = future.transaction.StateSchema(global_ints, global_bytes)
local_schema = future.transaction.StateSchema(local_ints, local_bytes)

# create new application
app_id = create_app(
    client,
    addr,
    sk,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
)

# read json and create ABI Contract description
with open(os.path.join(path, "contract.json")) as f:
    js = f.read()
c = Contract.from_json(js)

signer = AccountTransactionSigner(sk)

comp = AtomicTransactionComposer()

sp = client.suggested_params()

comp.add_method_call(app_id, c.get_method_by_name("sub"), addr, sp, signer, method_args=[2, 1])

comp.add_method_call(app_id, c.get_method_by_name("div"), addr, sp, signer, method_args=[8, 4])

comp.add_method_call(app_id, c.get_method_by_name("add"), addr, sp, signer, method_args=[1, 2])

comp.add_method_call(app_id, c.get_method_by_name("mul"), addr, sp, signer, method_args=[2, 2])

resp = comp.execute(client, 2)
for result in resp.abi_results:
    print(f"{result.method.name} => {result.return_value}")
