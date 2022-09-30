from pyteal import *

# A trivial stateful application that does two things:
# * tacks how many times a specific account called the app
#   by incrementing a counter in the caller's local state
# * tracks haw many times the app was called overall
#   by incrementing a counter in the app's global state
def call_counter_approval_program():

    handle_creation = Seq(
        [
            App.globalPut(Bytes("Creator"), Txn.sender()),
            Return(Int(1)),
        ]
    )

    handle_closeout = Return(Int(1))

    handle_optin = Seq(
        [
            App.localPut(Txn.sender(), Bytes(b"timesPinged"), Int(0)),
            Return(Int(1)),
        ]
    )

    times_pinged = App.localGet(Txn.sender(), Bytes(b"timesPinged"))
    times_ponged = App.globalGet(Bytes(b"timesPonged"))
    handle_ping = Seq(
        [
            # increment the app's "pong" counter --- how many times the app was pinged overall
            App.globalPut(Bytes(b"timesPonged"), times_ponged + Int(1)),
            # increment the user's "ping" counter --- how many times this specific user pinged the app
            App.localPut(Txn.sender(), Bytes(b"timesPinged"), times_pinged + Int(1)),
            Return(Int(1)),
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [
            And(
                Txn.on_completion() == OnComplete.NoOp,
                Txn.application_args[0] == Bytes(b"ping"),
            ),
            handle_ping,
        ],
    )

    return program

def call_counter_clear_program():

    return Int(1)
