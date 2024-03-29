from base64 import b64decode
from typing import Dict

from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import ApplicationCallTxn, ApplicationCreateTxn, OnComplete, PaymentTxn
from algosdk.v2client.algod import AlgodClient

approval_program_src = '''
#pragma version 2
int 1
return
'''

clear_program_src = '''
#pragma version 2
int 0
return
'''


def generate_and_fund_account(client: AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = client.suggested_params()
    client.send_transaction(PaymentTxn(faucet['address'], sp, address, 10_000_000).sign(faucet['private_key']))

    return {'address': address, 'private_key': private_key}


def create_app(client: AlgodClient, faucet: Dict[str, str]) -> int:
    sp = client.suggested_params()

    app_creator = generate_and_fund_account(client, faucet)

    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    approval_program = b64decode(client.compile(approval_program_src)['result'])
    clear_program = b64decode(client.compile(clear_program_src)['result'])

    create_app_txn = ApplicationCreateTxn(
        app_creator['address'],
        sp,
        OnComplete.NoOpOC,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign the transaction
    signed_create_app_txn = create_app_txn.sign(app_creator['private_key'])

    # send the transaction to the network and save its id
    create_app_txn_id = client.send_transactions([signed_create_app_txn])
    created_app_id = client.pending_transaction_info(create_app_txn_id)['application-index']

    return created_app_id


def test_create(client: AlgodClient, faucet: Dict[str, str]) -> None:
    # create app
    app_id = create_app(client, faucet)
    assert app_id

    # create user
    user = generate_and_fund_account(client, faucet)

    # user calls the application
    sp = client.suggested_params()
    app_call_txn = ApplicationCallTxn(user['address'], sp, app_id, OnComplete.NoOpOC)
    signed_app_call_txn = app_call_txn.sign(user['private_key'])
    app_call_txn_id = client.send_transactions([signed_app_call_txn])
    app_call_txn_status = client.pending_transaction_info(app_call_txn_id)

    # check that the transaction was confirmed --- call succeded
    assert app_call_txn_status['confirmed-round']
    # # check that a valid (non-zero) app id was returned
    # assert app_call_txn_status['application-index']
