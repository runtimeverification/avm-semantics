from algosdk import account
from algosdk.future.transaction import PaymentTxn, SuggestedParams
from kavm_algod.adaptors.transaction import transaction_from_k, transaction_to_k
from kavm_algod.kavm import KAVM


def test_payment_txn_encode_decode(
    kavm: KAVM, suggested_params: SuggestedParams
) -> None:
    # generate accounts
    private_key_sender, sender = account.generate_account()
    private_key_receiver, receiver = account.generate_account()

    # create a transaction
    sp = suggested_params
    amount = 10000
    txn = PaymentTxn(sender, sp, receiver, amount)

    kast_term = transaction_to_k(kavm, txn)

    parsed_txn = transaction_from_k(kast_term)

    assert parsed_txn.dictify() == txn.dictify()
