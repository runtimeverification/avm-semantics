from typing import Dict

from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn
from algosdk.v2client.algod import AlgodClient

# from kavm_algod.algod import KAVMClient
from kavm_algod.constants import FAUCET_ALGO_SUPPLY


def test_faucet(
    client: AlgodClient,
    faucet: Dict[str, str],
) -> None:
    """Faucet can fund two accounts using a group of two PaymentTxn"""
    private_key_alice, alice = account.generate_account()
    private_key_bob, bob = account.generate_account()

    # check faucet's balance
    faucet_balance = client.account_info(faucet['address'])['amount']
    assert faucet_balance >= FAUCET_ALGO_SUPPLY

    # fund accounts from the faucet
    sp = client.suggested_params()
    amount1 = 100_001
    amount2 = 100_002
    txn1 = PaymentTxn(faucet['address'], sp, alice, amount1)
    txn2 = PaymentTxn(faucet['address'], sp, bob, amount2)

    # get group id and assign it to transactions
    gid = transaction.calculate_group_id([txn1, txn2])
    txn1.group = gid
    txn2.group = gid

    # sign transactions
    stxn1 = txn1.sign(faucet['private_key'])
    stxn2 = txn2.sign(faucet['private_key'])

    # send them over network
    group_txn_id = client.send_transactions([stxn1, stxn2])

    group_status = client.pending_transaction_info(group_txn_id)

    # check that the first transaction in group,
    # hence the whole group, was confirmed --- call succeded
    assert group_status['confirmed-round']

    # check updated balances
    alice_balance = client.account_info(alice)['amount']
    bob_balance = client.account_info(bob)['amount']

    assert alice_balance == amount1
    assert bob_balance == amount2


def test_faucet_separate_groups(
    client: AlgodClient,
    faucet: Dict[str, str],
) -> None:
    """Faucet can fund two accounts using a two independent grous of signle PaymentTxn"""
    accounts: Dict[int, str] = {}
    _, accounts[0] = account.generate_account()
    _, accounts[1] = account.generate_account()

    for i in range(len(accounts)):
        # check faucet's balance is reasonably high
        faucet_balance = client.account_info(faucet['address'])['amount']
        assert faucet_balance >= 0.5 * FAUCET_ALGO_SUPPLY

        # fund accounts from the faucet
        sp = client.suggested_params()
        amount = 100_000 + i
        txn = PaymentTxn(faucet['address'], sp, accounts[i], amount)

        # get group id and assign it to transactions
        gid = transaction.calculate_group_id([txn])
        txn.group = gid

        # sign transaction
        stxn = txn.sign(faucet['private_key'])

        # send them over network
        group_txn_id = client.send_transactions([stxn])

        group_status = client.pending_transaction_info(group_txn_id)

        # check that the first transaction in group,
        # hence the whole group, was confirmed --- call succeded
        assert group_status['confirmed-round']

        # check updated balances
        assert client.account_info(accounts[i])['amount'] == amount
