from algosdk import account
<<<<<<< HEAD
from algosdk.future.transaction import PaymentTxn
=======
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn, SuggestedParams
>>>>>>> origin

from kavm_algod.adaptors.transaction import transaction_from_k, transaction_to_k


<<<<<<< HEAD
def test_payment_txn_encode_decode(suggested_params):
    # generate accounts
    private_key_sender, sender = account.generate_account()

=======
def test_payment_txn_encode_decode(suggested_params: SuggestedParams) -> None:
    # generate accounts
    private_key_sender, sender = account.generate_account()
>>>>>>> origin
    private_key_receiver, receiver = account.generate_account()

    # create a transaction
    sp = suggested_params
    amount = 10000
    txn = PaymentTxn(sender, sp, receiver, amount)

    kast_term = transaction_to_k(txn)
    parsed_txn = transaction_from_k(kast_term)

    assert parsed_txn.dictify() == txn.dictify()
<<<<<<< HEAD
=======


def test_asset_transfer_txn_encode_decode(suggested_params: SuggestedParams) -> None:
    # generate accounts
    private_key_sender, sender = account.generate_account()
    private_key_receiver, receiver = account.generate_account()

    # create a transaction
    sp = suggested_params
    amount = 10000
    txn = AssetTransferTxn(sender, sp, receiver, amount, 1)

    kast_term = transaction_to_k(txn)
    parsed_txn = transaction_from_k(kast_term)

    assert parsed_txn.dictify() == txn.dictify()
>>>>>>> origin
