from base64 import b64decode
from typing import Dict

import pytest
from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import (
    ApplicationCallTxn,
    ApplicationCreateTxn,
    OnComplete,
    PaymentTxn,
)
from algosdk.v2client.algod import AlgodClient

approval_program_src = '''
#pragma version 4

txn OnCompletion
int NoOp
==
bnz handle_noop

// OnCompletetion actions other than NoOp are denied
err

// Test arithemtic
handle_noop:
int 1
int 2
+
store 0
load 0
int 3
*
store 1
load 1
int 3
/
store 2
load 2
int 2
-
store 3
load 3
int 1
==
assert

accept:
int 1
return
'''

clear_program_src = '''
#pragma version 4
int 1
return
'''


def generate_and_fund_account(
    algod: AlgodClient, faucet: Dict[str, str]
) -> Dict[str, str]:
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = algod.suggested_params()
    algod.send_transaction(
        PaymentTxn(faucet['address'], sp, address, 10_000_000).sign(
            faucet['private_key']
        )
    )

    return {'address': address, 'private_key': private_key}


def create_calculator_app(algod: AlgodClient, faucet: Dict[str, str]) -> int:

    sp = algod.suggested_params()

    calculator_creator = generate_and_fund_account(algod, faucet)

    # prepare the transaction to create the smart contract
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    approval_program = b64decode(algod.compile(approval_program_src)['result'])
    clear_program = b64decode(algod.compile(clear_program_src)['result'])
    create_app_txn = ApplicationCreateTxn(
        calculator_creator['address'],
        sp,
        OnComplete.NoOpOC,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign the transaction
    signed_create_app_txn = create_app_txn.sign(calculator_creator['private_key'])

    # send the transaction to the network and save its id
    create_app_txn_id = algod.send_transactions([signed_create_app_txn])
    created_app_id = algod.pending_transaction_info(create_app_txn_id)[
        'application-index'
    ]

    return created_app_id


@pytest.mark.skipif(
    "config.getoption('--backend') == 'kalgod'",
    reason='kalgod does not yet support ApplicationCallTxn',
)
def test_call_calculator(algod: AlgodClient, faucet: Dict[str, str]) -> None:
    # create app
    app_id = create_calculator_app(algod, faucet)

    # create user
    user = generate_and_fund_account(algod, faucet)

    # user calls the application
    sp = algod.suggested_params()
    app_call_txn = ApplicationCallTxn(user['address'], sp, app_id, OnComplete.NoOpOC)
    signed_app_call_txn = app_call_txn.sign(user['private_key'])
    app_call_txn_id = algod.send_transactions([signed_app_call_txn])
    app_call_txn_status = algod.pending_transaction_info(app_call_txn_id)

    # check that the transaction was confirmed --- call succeded
    assert app_call_txn_status['confirmed-round']
