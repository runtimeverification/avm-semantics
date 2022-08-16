from base64 import b64decode
<<<<<<< HEAD
import pytest
=======
from typing import Dict
>>>>>>> origin

from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import (
<<<<<<< HEAD
    PaymentTxn,
    ApplicationCallTxn,
    ApplicationCreateTxn,
    OnComplete,
)

approval_program_src = """
=======
    ApplicationCallTxn,
    ApplicationCreateTxn,
    OnComplete,
    PaymentTxn,
)
from algosdk.v2client import AlgodClient

approval_program_src = '''
>>>>>>> origin
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
<<<<<<< HEAD
"""

clear_program_src = """
#pragma version 4
int 1
return
"""


def generate_and_fund_account(algod, faucet):
=======
'''

clear_program_src = '''
#pragma version 4
int 1
return
'''


def generate_and_fund_account(
    algod: AlgodClient, faucet: Dict[str, str]
) -> Dict[str, str]:
>>>>>>> origin
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = algod.suggested_params()
    algod.send_transaction(
<<<<<<< HEAD
        PaymentTxn(faucet["address"], sp, address, 10_000_000).sign(
            faucet["private_key"]
        )
    )

    return {"address": address, "private_key": private_key}


def create_calculator_app(algod, faucet):
=======
        PaymentTxn(faucet['address'], sp, address, 10_000_000).sign(
            faucet['private_key']
        )
    )

    return {'address': address, 'private_key': private_key}


def create_calculator_app(algod: AlgodClient, faucet: Dict[str, str]) -> int:
>>>>>>> origin

    sp = algod.suggested_params()

    calculator_creator = generate_and_fund_account(algod, faucet)

    # prepare the transaction to create the smart contract
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
<<<<<<< HEAD
    approval_program = b64decode(algod.compile(approval_program_src)["result"])
    clear_program = b64decode(algod.compile(clear_program_src)["result"])
    create_app_txn = ApplicationCreateTxn(
        calculator_creator["address"],
=======
    approval_program = b64decode(algod.compile(approval_program_src)['result'])
    clear_program = b64decode(algod.compile(clear_program_src)['result'])
    create_app_txn = ApplicationCreateTxn(
        calculator_creator['address'],
>>>>>>> origin
        sp,
        OnComplete.NoOpOC,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign the transaction
<<<<<<< HEAD
    signed_create_app_txn = create_app_txn.sign(calculator_creator["private_key"])
=======
    signed_create_app_txn = create_app_txn.sign(calculator_creator['private_key'])
>>>>>>> origin

    # send the transaction to the network and save its id
    create_app_txn_id = algod.send_transactions([signed_create_app_txn])
    created_app_id = algod.pending_transaction_info(create_app_txn_id)[
<<<<<<< HEAD
        "application-index"
=======
        'application-index'
>>>>>>> origin
    ]

    return created_app_id


<<<<<<< HEAD
def test_call_calculator(algod, faucet):
=======
def test_call_calculator(algod: AlgodClient, faucet: Dict[str, str]) -> None:
>>>>>>> origin
    # create app
    app_id = create_calculator_app(algod, faucet)

    # create user
    user = generate_and_fund_account(algod, faucet)

    # user calls the application
    sp = algod.suggested_params()
<<<<<<< HEAD
    app_call_txn = ApplicationCallTxn(user["address"], sp, app_id, OnComplete.NoOpOC)
    signed_app_call_txn = app_call_txn.sign(user["private_key"])
=======
    app_call_txn = ApplicationCallTxn(user['address'], sp, app_id, OnComplete.NoOpOC)
    signed_app_call_txn = app_call_txn.sign(user['private_key'])
>>>>>>> origin
    app_call_txn_id = algod.send_transactions([signed_app_call_txn])
    app_call_txn_status = algod.pending_transaction_info(app_call_txn_id)

    # check that the transaction was confirmed --- call succeded
<<<<<<< HEAD
    assert app_call_txn_status["confirmed-round"]
=======
    assert app_call_txn_status['confirmed-round']
>>>>>>> origin
