from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn, SuggestedParams

from kavm_algod.algod import KAVMClient
from .constants import ALGOD_ADDRESS, ALGOD_TOKEN


def test_kalgod_init():
    _ = KAVMClient(ALGOD_ADDRESS, ALGOD_TOKEN)


def test_send_payments(kalgod: KAVMClient, suggested_params: SuggestedParams) -> None:

    # generate accounts
    private_key_sender, sender = account.generate_account()
    private_key_receiver, receiver = account.generate_account()

    # create a transactions
    sp = suggested_params
    amount1 = 111
    amount2 = 222
    txn1 = PaymentTxn(sender, sp, receiver, amount1)
    txn2 = PaymentTxn(receiver, sp, sender, amount2)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transactions
    stxn1 = txn1.sign(private_key_sender)
    stxn2 = txn2.sign(private_key_receiver)

    # send them over network
    kalgod.send_transactions([stxn1, stxn2])
