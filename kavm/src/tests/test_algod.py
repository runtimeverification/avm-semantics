from typing import Dict

from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn, SuggestedParams

from kavm.algod import KAVMClient


def test_send_transactions(faucet: Dict[str, str], kalgod: KAVMClient, suggested_params: SuggestedParams) -> None:
    # generate account
    _, receiver = account.generate_account()

    # create a transactions
    sp = suggested_params
    amount = 100000
    txn1 = PaymentTxn(faucet['address'], sp, receiver, amount)
    txn2 = PaymentTxn(faucet['address'], sp, receiver, amount)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transactions
    stxn1 = txn1.sign(faucet['private_key'])
    stxn2 = txn2.sign(faucet['private_key'])

    # send them over network
    kalgod.send_transactions([stxn1, stxn2])
