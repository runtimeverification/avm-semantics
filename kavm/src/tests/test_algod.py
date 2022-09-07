from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn, SuggestedParams

from kavm.algod import KAVMClient


def test_send_transactions(kalgod: KAVMClient, suggested_params: SuggestedParams) -> None:

    # generate accounts
    private_key_sender, sender = account.generate_account()
    private_key_receiver, receiver = account.generate_account()

    # create a transactions
    sp = suggested_params
    amount = 10000
    txn1 = PaymentTxn(sender, sp, receiver, amount)
    txn2 = PaymentTxn(sender, sp, receiver, amount)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transactions
    stxn1 = txn1.sign(private_key_sender)
    stxn2 = txn2.sign(private_key_receiver)

    # send them over network
    kalgod.send_transactions([stxn1, stxn2])
