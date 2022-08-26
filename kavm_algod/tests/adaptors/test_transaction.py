from algosdk import account
from algosdk.future.transaction import PaymentTxn, SuggestedParams

from kavm_algod.adaptors.transaction import KAVMTransaction, transaction_from_k
from kavm_algod.kavm import KAVM


def test_payment_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    """Converting a transaction to the KAVM representation and back yeilds the same transaction"""
    private_key_sender, sender = account.generate_account()
    private_key_receiver, receiver = account.generate_account()
    amount = 10000
    txn = PaymentTxn(sender, suggested_params, receiver, amount)
    kavm_transaction = KAVMTransaction(kalgod.kavm, txn, "0")
    parsed_txn = transaction_from_k(kavm_transaction.transaction_cell)
    assert parsed_txn.dictify() == txn.dictify()
