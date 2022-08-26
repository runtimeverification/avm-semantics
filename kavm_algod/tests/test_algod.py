from typing import Any

from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn, SuggestedParams

from kavm_algod.algod import KAVMClient

from .constants import ALGOD_ADDRESS, ALGOD_TOKEN


def test_kalgod_init() -> None:
    _ = KAVMClient(ALGOD_ADDRESS, ALGOD_TOKEN, None)


def test_faucet(
    kalgod: KAVMClient,
    suggested_params: SuggestedParams,
    kalgod_faucet: Any,
) -> None:

    # generate accounts
    private_key_alice, alice = account.generate_account()
    private_key_bob, bob = account.generate_account()

    # fund accounts from the KAVM faucet
    sp = suggested_params
    amount1 = 100_001
    amount2 = 100_002
    txn1 = PaymentTxn(kalgod_faucet['address'], sp, alice, amount1)
    txn2 = PaymentTxn(kalgod_faucet['address'], sp, bob, amount2)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transactions
    stxn1 = txn1.sign(kalgod_faucet['private_key'])
    stxn2 = txn2.sign(kalgod_faucet['private_key'])

    # send them over network
    kalgod.send_transactions([stxn1, stxn2])

    alice_balance = kalgod.account_info(alice)['amount']
    bob_balance = kalgod.account_info(bob)['amount']

    assert alice_balance == amount1
    assert bob_balance == amount2
