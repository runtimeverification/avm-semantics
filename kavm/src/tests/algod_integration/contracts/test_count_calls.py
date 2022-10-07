from typing import Dict

import base64
from base64 import b64decode

import pytest
from algosdk import account
from algosdk.v2client.algod import AlgodClient

from src.tests.algod_integration.contracts.count_calls_pyteal import *

from algosdk.future.transaction import PaymentTxn, ApplicationCallTxn, OnComplete, StateSchema

from src.tests.algod_integration.algosdk_utils import get_balance, get_local_int, get_global_int, get_global_bytes, get_created_app_id

from algosdk.encoding import encode_address

def generate_and_fund_account(client: AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = client.suggested_params()
    client.send_transaction(PaymentTxn(faucet['address'], sp, address, 1_000_000).sign(faucet['private_key']))

    return {'address': address, 'private_key': private_key}

def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])

def test_count_calls(client: AlgodClient, faucet: Dict[str, str]):
    # Setup a user account
    user = generate_and_fund_account(client, faucet)
    sp = client.suggested_params()

    program_src = compileTeal(call_counter_approval_program(), mode=Mode.Application, version=6)
    program = compile_program(client, program_src)

    clear_src = compileTeal(call_counter_clear_program(), mode=Mode.Application, version=6)
    clear = compile_program(client, clear_src)

    # set up TXN --- user creates a call counter app
    txn = ApplicationCallTxn(
        sender = user['address'],
        sp = sp,
        index = None,
        local_schema = StateSchema(num_uints=1, num_byte_slices=0),
        global_schema = StateSchema(num_uints=2, num_byte_slices=2),
        on_complete = OnComplete.NoOpOC,
        approval_program=program,
        clear_program=clear,
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])

    app_id = get_created_app_id(client, txn_id)

    x = get_global_bytes(client, app_id, "Creator")

    print("abc")
    print(x)
    print(len(x))
    assert False
    assert encode_address(get_global_bytes(client, app_id, "Creator")) == user['address']
    assert get_global_int(client, app_id, "Number") == 123

    # opt in to app
    txn = ApplicationCallTxn(
        sender = user['address'],
        sp = sp,
        index = app_id,
        on_complete = OnComplete.OptInOC,
    )
    signed_txn = txn.sign(user['private_key'])

    txn_id = client.send_transactions([signed_txn])

    txn_status = client.pending_transaction_info(txn_id)

    print(client.account_info(user['address']))

    assert encode_address(get_global_bytes(client, app_id, "Creator")) == user['address']
    assert get_local_int(client, app_id, user['address'], "timesPinged") == 0

    # call ping" function on app, increasing local and global counter by 1
    txn = ApplicationCallTxn(
        sender = user['address'],
        sp = sp,
        index = app_id,
        on_complete = OnComplete.NoOpOC,
        app_args = [ bytearray("ping", "ascii"), 0x0 ]
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])
    txn_status = client.pending_transaction_info(txn_id)

    assert get_local_int(client, app_id, user['address'], "timesPinged") == 1
    assert get_global_int(client, app_id, "timesPonged") == 1

    # call ping" function on app, increasing local and global counter by 1
    txn = ApplicationCallTxn(
        sender = user['address'],
        sp = sp,
        index = app_id,
        on_complete = OnComplete.NoOpOC,
        app_args = [ bytearray("ping", "ascii"), 0x1 ]
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])
    txn_status = client.pending_transaction_info(txn_id)

    assert get_local_int(client, app_id, user['address'], "timesPinged") == 2
    assert get_global_int(client, app_id, "timesPonged") == 2

    assert False
