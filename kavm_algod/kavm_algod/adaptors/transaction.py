from typing import Any, Dict

from algosdk.constants import ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.future.transaction import (
    AssetTransferTxn,
    PaymentTxn,
    SuggestedParams,
    Transaction,
)
from pyk.kast import KApply, KAst

from kavm_algod.pyk_utils import extract_cells, int_token_cell, string_token_cell


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
    txHeaderFields: Dict[str, KAst] = {}
    txHeaderFields = extract_cells(
        kast_term,
        [
            '<sender>',
            '<fee>',
            '<firstValid>',
            '<lastValid>',
            '<genesisHash>',
            '<txType>',
        ],
    )

    sp = SuggestedParams(
        int(txHeaderFields['<fee>'].args[0].token),
        int(txHeaderFields['<firstValid>'].args[0].token),
        int(txHeaderFields['<lastValid>'].args[0].token),
        txHeaderFields['<genesisHash>'].args[0].token,
        flat_fee=True,
    )

    txnType = txHeaderFields['<txType>'].args[0].token.strip('"')
    result = None
    if txnType == PAYMENT_TXN:
        payTxFields: Dict[str, Any] = {}
        payTxFields = extract_cells(kast_term, ['<receiver>', '<amount>', '<closeTo>'])
        result = PaymentTxn(
            sender=txHeaderFields['<sender>'].args[0].token.strip('"'),
            sp=sp,
            receiver=payTxFields['<receiver>'].args[0].token.strip('"'),
            amt=int(payTxFields['<amount>'].args[0].token),
        )
    elif txnType == ASSETTRANSFER_TXN:
        assetTransferTxFields: Dict[str, Any] = {}
        assetTransferTxFields = extract_cells(
            kast_term,
            [
                '<xferAsset>',
                '<assetAmount>',
                '<assetReceiver>',
                '<assetASender>',
                '<assetCloseTo>',
            ],
        )
        result = AssetTransferTxn(
            sender=txHeaderFields['<sender>'].args[0].token.strip('"'),
            sp=sp,
            receiver=assetTransferTxFields['<assetReceiver>'].args[0].token.strip('"'),
            amt=int(assetTransferTxFields['<assetAmount>'].args[0].token.strip('"')),
            index=int(assetTransferTxFields['<xferAsset>'].args[0].token.strip('"')),
        )
    else:
        raise ValueError(
            f'Cannot instantiate a Transaction of an unexpected type {txnType}'
        )

    return result
