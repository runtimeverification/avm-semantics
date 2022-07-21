from algosdk.future.transaction import PaymentTxn, SuggestedParams

from algosdk import account
from kavm_algod.adaptors.transaction import transaction_to_k, transaction_from_k


def test_payment_txn_encode_decode():
    sp = SuggestedParams(1000, 0, 1, "ktealktealktealkteal", flat_fee=True)

    # generate accounts
    private_key_sender, sender = account.generate_account()

    private_key_receiver, receiver = account.generate_account()

    # create a transaction
    amount = 10000
    txn = PaymentTxn(sender, sp, receiver, amount)

    kast_term = transaction_to_k(txn)
    parsed_txn = transaction_from_k(kast_term)

    assert parsed_txn.dictify() == txn.dictify()
