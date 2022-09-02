from algosdk.constants import ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn, SuggestedParams, Transaction
from pyk.kast import KApply, KAst
from pyk.kastManip import split_config_from

from kavm.pyk_utils import int_token_cell, string_token_cell


def transaction_to_k(txn: Transaction) -> KApply:
    """Convert a Transaction objet to a K cell"""
    header = KApply(
        '<txHeader>',
        [
            int_token_cell('<fee>', txn.fee),
            int_token_cell('<firstValid>', txn.first_valid_round),
            int_token_cell('<lastValid>', txn.last_valid_round),
            string_token_cell('<genesisHash>', txn.genesis_hash),
            string_token_cell('<sender>', txn.sender),
            string_token_cell('<txType>', txn.type),
            # TODO: convert type to type enum, an int token
            string_token_cell('<typeEnum>', txn.type),
            string_token_cell('<group>', txn.group),
            string_token_cell('<genesisID>', txn.genesis_id),
            string_token_cell('<lease>', txn.lease),
            string_token_cell('<note>', txn.note),
            string_token_cell('<rekeyTo>', txn.rekey_to),
        ],
    )
    type_specific_fields = None
    if txn.type == PAYMENT_TXN:
        type_specific_fields = _payment_to_k(txn)
    if txn.type == ASSETTRANSFER_TXN:
        type_specific_fields = _asset_transfer_to_k(txn)
    if type_specific_fields is None:
        raise ValueError(f'Transaction object {txn} is invalid')
    return KApply('<transaction>', [header, type_specific_fields])


def _payment_to_k(txn: PaymentTxn) -> KApply:
    """Convert a PaymentTxn objet to a K cell"""
    assert isinstance(txn, PaymentTxn)
    config = KApply(
        '<payTxFields>',
        [
            string_token_cell('<receiver>', txn.receiver),
            int_token_cell('<amount>', txn.amt),
            string_token_cell('<closeRemainderTo>', txn.close_remainder_to),
        ],
    )
    return config


def _asset_transfer_to_k(txn: AssetTransferTxn) -> KApply:
    """Convert an AssetTransferTxn objet to a K cell"""
    assert isinstance(txn, AssetTransferTxn)
    config = KApply(
        '<assetTransferTxFields>',
        [
            int_token_cell('<xferAsset>', txn.index),
            int_token_cell('<assetAmount>', txn.amount),
            string_token_cell('<assetReceiver>', txn.receiver),
            string_token_cell('<closeRemainderTo>', txn.close_assets_to),
            # TODO: make sure assetASender indeed corresponds to revocation_target
            string_token_cell('<assetASender>', txn.revocation_target),
        ],
    )
    return config


def transaction_from_k(kast_term: KAst) -> Transaction:
    """
    Covert a Kast term to one of the subclasses of the algosdk.Transaction

    Raise ValueError if the transaction is marformed
    """
    _, tx_header_cells = split_config_from(kast_term)

    sp = SuggestedParams(
        int(tx_header_cells['FEE_CELL'].token),
        int(tx_header_cells['FIRSTVALID_CELL'].token),
        int(tx_header_cells['LASTVALID_CELL'].token),
        tx_header_cells['GENESISHASH_CELL'].token,
        flat_fee=True,
    )

    txn_type = tx_header_cells['TXTYPE_CELL'].token.strip('"')
    result = None
    if txn_type == PAYMENT_TXN:
        _, pay_tx_cells = split_config_from(kast_term)
        result = PaymentTxn(
            sender=tx_header_cells['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=pay_tx_cells['RECEIVER_CELL'].token.strip('"'),
            amt=int(pay_tx_cells['AMOUNT_CELL'].token),
        )
    elif txn_type == ASSETTRANSFER_TXN:
        _, asset_transfer_tx_cells = split_config_from(kast_term)
        result = AssetTransferTxn(
            sender=tx_header_cells['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=asset_transfer_tx_cells['ASSETRECEIVER_CELL'].token.strip('"'),
            amt=int(asset_transfer_tx_cells['ASSETAMOUNT_CELL'].token.strip('"')),
            index=int(asset_transfer_tx_cells['XFERASSET_CELL'].token.strip('"')),
        )
    else:
        raise ValueError(f'Cannot instantiate a Transaction of an unexpected type {txn_type}')

    return result
