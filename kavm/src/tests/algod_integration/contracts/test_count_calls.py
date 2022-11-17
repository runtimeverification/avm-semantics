from typing import Dict

from algosdk.encoding import encode_address
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import And, App, Bytes, Cond, Expr, Int, Mode, OnComplete, Return, Seq, Txn, compileTeal

from ..algosdk_utils import compile_program, generate_and_fund_account, get_created_app_id, get_global_bytes


# A trivial stateful application that does two things:
# * tacks how many times a specific account called the app
#   by incrementing a counter in the caller's local state
# * tracks haw many times the app was called overall
#   by incrementing a counter in the app's global state
def call_counter_approval_program() -> Expr:

    handle_creation = Seq(
        [
            App.globalPut(Bytes('Creator'), Txn.sender()),
            App.globalPut(Bytes('timesPonged'), Int(0)),
            Return(Int(1)),
        ]
    )

    handle_closeout = Return(Int(1))

    handle_optin = Seq(
        [
            App.localPut(Txn.sender(), Bytes('timesPinged'), Int(0)),
            App.localPut(Txn.sender(), Bytes('senderAddress'), Txn.sender()),
            Return(Int(1)),
        ]
    )

    times_pinged = App.localGet(Txn.sender(), Bytes('timesPinged'))
    times_ponged = App.globalGet(Bytes('timesPonged'))
    handle_ping = Seq(
        [
            # increment the app's 'pong' counter --- how many times the app was pinged overall
            App.globalPut(Bytes('timesPonged'), times_ponged + Int(1)),
            # increment the user's 'ping' counter --- how many times this specific user pinged the app
            App.localPut(Txn.sender(), Bytes('timesPinged'), times_pinged + Int(1)),
            Return(Int(1)),
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [
            And(
                Txn.on_completion() == OnComplete.NoOp,
                Txn.application_args[0] == Bytes('ping'),
            ),
            handle_ping,
        ],
    )

    return program


def call_counter_clear_program() -> Expr:
    return Int(1)


def test_count_calls(client: algod.AlgodClient, faucet: Dict[str, str]) -> None:
    # Setup a user account
    user = generate_and_fund_account(client, faucet)
    sp = client.suggested_params()

    program_src = compileTeal(call_counter_approval_program(), mode=Mode.Application, version=6)

    program = compile_program(client, program_src)

    clear_src = compileTeal(call_counter_clear_program(), mode=Mode.Application, version=6)
    clear = compile_program(client, clear_src)

    # set up TXN --- user creates a call counter app
    txn = transaction.ApplicationCallTxn(
        sender=user['address'],
        sp=sp,
        index=None,
        local_schema=transaction.StateSchema(num_uints=1, num_byte_slices=1),
        global_schema=transaction.StateSchema(num_uints=1, num_byte_slices=1),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=program,
        clear_program=clear,
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])

    app_id = get_created_app_id(client, txn_id)
    assert app_id

    creator_addr_bytes = get_global_bytes(client, app_id, 'Creator')
    assert encode_address(creator_addr_bytes) == user['address']

    # opt in to app
    txn = transaction.ApplicationCallTxn(
        sender=user['address'],
        sp=sp,
        index=app_id,
        on_complete=transaction.OnComplete.OptInOC,
    )
    signed_txn = txn.sign(user['private_key'])

    txn_id = client.send_transactions([signed_txn])

    txn_status = client.pending_transaction_info(txn_id)
    assert txn_status['confirmed-round']

    creator_addr_bytes = get_global_bytes(client, app_id, 'Creator')
    # sender_addr_bytes = get_local_bytes(client, app_id, user['address'], 'senderAddress')
    assert encode_address(creator_addr_bytes) == user['address']
    # assert encode_address(sender_addr_bytes) == user['address']
    # assert get_local_int(client, app_id, user['address'], 'timesPinged') == 0

    # call ping' function on app, increasing local and global counter by 1
    txn = transaction.ApplicationCallTxn(
        sender=user['address'],
        sp=sp,
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=['ping'.encode(), 0x0],
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])
    txn_status = client.pending_transaction_info(txn_id)
    assert txn_status['confirmed-round']

    # assert get_local_int(client, app_id, user['address'], 'timesPinged') == 1
    # assert get_global_int(client, app_id, 'timesPonged') == 1

    # call 'ping' function on app, increasing local and global counter by 1
    txn = transaction.ApplicationCallTxn(
        sender=user['address'],
        sp=sp,
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=['ping'],
    )
    signed_txn = txn.sign(user['private_key'])
    txn_id = client.send_transactions([signed_txn])
    txn_status = client.pending_transaction_info(txn_id)
    assert txn_status['confirmed-round']

    # assert get_local_int(client, app_id, user['address'], 'timesPinged') == 2
    # assert get_global_int(client, app_id, 'timesPonged') == 2
