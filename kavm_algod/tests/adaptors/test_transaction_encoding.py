import pytest
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


@pytest.mark.skip(reason="KeyregTxn is not yet supported")
def test_keyreg_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="KeyregOnlineTxn is not yet supported")
def test_keyreg_online_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="KeyregOfflineTxn is not yet supported")
def test_keyreg_offline_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="KeyregNonpartisipationTxn is not yet supported")
def test_keyreg_nonpartisipation_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetConfigTxn is not yet supported")
def test_asset_config_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetCreateTxn is not yet supported")
def test_asset_create_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetDestroyTxn is not yet supported")
def test_asset_destroy_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetUpdateTxn is not yet supported")
def test_asset_update_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetFreezeTxn is not yet supported")
def test_asset_freeze_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetTransferTxn is not yet supported")
def test_asset_transfer_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetOptInTxn is not yet supported")
def test_asset_opt_in_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="AssetCloseOutTxn is not yet supported")
def test_asset_close_out_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationCallTxn is not yet supported")
def test_application_call_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationCreateTxn is not yet supported")
def test_application_create_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationUpdateTxn is not yet supported")
def test_application_update_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationDeleteTxn is not yet supported")
def test_application_delete_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationOptInTxn is not yet supported")
def test_application_opt_in_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationCloseOutTxn is not yet supported")
def test_application_close_out_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationClearStateTxn is not yet supported")
def test_application_clear_state_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="ApplicationNoOpTxn is not yet supported")
def test_application_no_op_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False


@pytest.mark.skip(reason="StateProofTxn is not yet supported")
def test_state_proof_txn_encode_decode(
    kalgod: KAVM, suggested_params: SuggestedParams
) -> None:
    assert False
