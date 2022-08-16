<<<<<<< HEAD
from algosdk.future.transaction import PaymentTxn, SuggestedParams, Transaction
from pyk.kast import KApply, KAst
from pyk.prelude import intToken, stringToken


def transaction_to_k(txn: Transaction):
    """Convert a Transaction objet to K configuration"""
    header = KApply(
        "<txHeader>",
        [
            KApply(
                "<fee>",
                [
                    intToken(
                        f"{txn.fee}",
                    )
                ],
            ),
            KApply(
                "<firstValid>",
                [intToken(f"{txn.first_valid_round}")],
            ),
            KApply(
                "<lastValid>",
                [
                    intToken(
                        f"{txn.last_valid_round}",
                    )
                ],
            ),
            KApply(
                "<genesisHash>",
                [
                    stringToken(
                        f"{txn.genesis_hash}",
                    )
                ],
            ),
            KApply(
                "<sender>",
                [
                    stringToken(
                        f"{txn.sender}",
                    )
                ],
            ),
            KApply(
                "<txType>",
                [
                    stringToken(
                        f"{txn.type}",
                    )
                ],
            ),
            # TODO: convert type to type enum
            KApply(
                "<typeEnum>",
                [
                    stringToken(
                        f"{txn.type}",
                    )
                ],
            ),
            KApply(
                "<group>",
                [
                    stringToken(
                        f"{txn.group}",
                    )
                ],
            ),
            KApply(
                "<genesisID>",
                [
                    stringToken(
                        f"{txn.genesis_id}",
                    )
                ],
            ),
            KApply(
                "<lease>",
                [
                    stringToken(
                        f"{txn.lease}",
                    )
                ],
            ),
            KApply(
                "<rekeyTo>",
                [
                    stringToken(
                        f"{txn.rekey_to}",
                    )
                ],
            ),
        ],
    )
    type_specific_fields = None
    if txn.type == "pay":
        type_specific_fields = payment_fields_to_k(txn)
    if type_specific_fields is None:
        raise ValueError(f"Transaction object {txn} is invalid")
    return KApply(
        "<transaction>",
        [header, type_specific_fields],
    )


def payment_fields_to_k(txn: PaymentTxn):
    """Convert a PaymentTxn objet to K configuration"""
    config = KApply(
        "<payTxFields>",
        [
            KApply(
                "<receiver>",
                [
                    stringToken(
                        f"{txn.receiver}",
                    )
                ],
            ),
            KApply(
                "<amount>",
                [
                    intToken(
                        f"{txn.amt}",
                    )
                ],
            ),
            KApply(
                "<closeRemainderTo>",
                [
                    stringToken(
                        f"{txn.close_remainder_to}",
                    )
                ],
            ),
=======
from algosdk.constants import ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.future.transaction import (
    AssetTransferTxn,
    PaymentTxn,
    SuggestedParams,
    Transaction,
)
from pyk.kast import KApply, KAst
from pyk.kastManip import splitConfigFrom

from kavm_algod.pyk_utils import int_token_cell, string_token_cell


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
>>>>>>> origin
        ],
    )
    return config


<<<<<<< HEAD
def transaction_from_k(kast_term: KAst):
    term_dict = kast_term.to_dict()
    txHeader = None
    payTxFields = None
    for i, term in enumerate(term_dict["args"]):
        txHeader = term if term["label"]["name"] == "<txHeader>" else txHeader
        payTxFields = term if term["label"]["name"] == "<payTxFields>" else payTxFields
    sender = None
    sp = None
    note = None
    lease = None
    txn_type = None
    rekey_to = None
    fee = None
    first_valid = None
    last_valid = None
    genesis_hash = None
    for i, term in enumerate(txHeader["args"]):
        sender = term if term["label"]["name"] == "<sender>" else sender
        note = term if term["label"]["name"] == "<note>" else note
        lease = term if term["label"]["name"] == "<lease>" else lease
        txn_type = term if term["label"]["name"] == "<txType>" else txn_type
        rekey_to = term if term["label"]["name"] == "<rekeyTo>" else rekey_to
        fee = term if term["label"]["name"] == "<fee>" else fee
        first_valid = term if term["label"]["name"] == "<firstValid>" else first_valid
        last_valid = term if term["label"]["name"] == "<lastValid>" else last_valid
        genesis_hash = (
            term if term["label"]["name"] == "<genesisHash>" else genesis_hash
        )
    receiver = None
    amount = None
    close_to = None
    for i, term in enumerate(payTxFields["args"]):
        receiver = term if term["label"]["name"] == "<receiver>" else receiver
        amount = term if term["label"]["name"] == "<amount>" else amount
        close_to = term if term["label"]["name"] == "<close_to>" else close_to

    sp = SuggestedParams(
        int(fee["args"][0]["token"]),
        int(first_valid["args"][0]["token"]),
        int(last_valid["args"][0]["token"]),
        genesis_hash["args"][0]["token"],
        flat_fee=True,
    )

    return PaymentTxn(
        sender["args"][0]["token"].strip('"'),
        sp,
        receiver["args"][0]["token"].strip('"'),
        int(amount["args"][0]["token"]),
    )
=======
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
    (_, txHeaderCells) = splitConfigFrom(kast_term)

    sp = SuggestedParams(
        int(txHeaderCells['FEE_CELL'].token),
        int(txHeaderCells['FIRSTVALID_CELL'].token),
        int(txHeaderCells['LASTVALID_CELL'].token),
        txHeaderCells['GENESISHASH_CELL'].token,
        flat_fee=True,
    )

    txnType = txHeaderCells['TXTYPE_CELL'].token.strip('"')
    result = None
    if txnType == PAYMENT_TXN:
        (_, payTxCells) = splitConfigFrom(kast_term)
        result = PaymentTxn(
            sender=txHeaderCells['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=payTxCells['RECEIVER_CELL'].token.strip('"'),
            amt=int(payTxCells['AMOUNT_CELL'].token),
        )
    elif txnType == ASSETTRANSFER_TXN:
        (_, assetTransferTxCells) = splitConfigFrom(kast_term)
        result = AssetTransferTxn(
            sender=txHeaderCells['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=assetTransferTxCells['ASSETRECEIVER_CELL'].token.strip('"'),
            amt=int(assetTransferTxCells['ASSETAMOUNT_CELL'].token.strip('"')),
            index=int(assetTransferTxCells['XFERASSET_CELL'].token.strip('"')),
        )
    else:
        raise ValueError(
            f'Cannot instantiate a Transaction of an unexpected type {txnType}'
        )

    return result
>>>>>>> origin
