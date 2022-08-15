from algosdk.constants import ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.future.transaction import (
    AssetTransferTxn,
    PaymentTxn,
    SuggestedParams,
    Transaction,
)
from pyk.kast import KAst, KInner, KSort, Subst
from pyk.kastManip import collectFreeVars, splitConfigFrom

from kavm_algod.kavm import KAVM
from kavm_algod.pyk_utils import maybeTValue, tvalueList


def txn_type_to_type_enum(txn_type: str) -> int:
    if txn_type == 'unknown':
        return 0
    elif txn_type == 'pay':
        return 1
    elif txn_type == 'keyreg':
        return 2
    elif txn_type == 'acfg':
        return 3
    elif txn_type == 'axfer':
        return 4
    elif txn_type == 'afrz':
        return 5
    elif txn_type == 'appl':
        return 6
    else:
        raise ValueError(f'unknown transaction type {txn_type}')


def transaction_to_k(kavm: KAVM, txn: Transaction) -> KInner:
    """Convert a Transaction objet to a K cell"""
    empty_transaction_cell = kavm.definition.empty_config(KSort('TransactionCell'))

    header_subst = Subst(
        {
            'FEE_CELL': maybeTValue(kavm, txn.fee),
            'FIRSTVALID_CELL': maybeTValue(kavm, txn.first_valid_round),
            'LASTVALID_CELL': maybeTValue(kavm, txn.last_valid_round),
            'GENESISHASH_CELL': maybeTValue(kavm, txn.genesis_hash),
            'GENESISID_CELL': maybeTValue(kavm, txn.genesis_id),
            'SENDER_CELL': maybeTValue(kavm, txn.sender),
            'TXTYPE_CELL': maybeTValue(kavm, txn.type),
            # TODO: convert type to type enum, an int token
            'TYPEENUM_CELL': maybeTValue(kavm, txn_type_to_type_enum(txn.type)),
            'GROUP_CELL': maybeTValue(kavm, txn.group),
            'LEASE_CELL': maybeTValue(kavm, txn.lease),
            'NOTE_CELL': maybeTValue(kavm, txn.note),
            'REKEYTO_CELL': maybeTValue(kavm, txn.rekey_to),
        }
    )
    type_specific_subst = None
    if txn.type == PAYMENT_TXN:
        type_specific_subst = Subst(
            {
                'RECEIVER_CELL': maybeTValue(kavm, txn.receiver),
                'AMOUNT_CELL': maybeTValue(kavm, txn.amt),
                'CLOSEREMAINDERTO_CELL': maybeTValue(kavm, txn.close_remainder_to),
            }
        )
    if txn.type == ASSETTRANSFER_TXN:
        raise NotImplementedError()
    if type_specific_subst is None:
        raise ValueError(f'Transaction object {txn} is invalid')

    fields_subst = (
        Subst({'TXID_CELL': maybeTValue(kavm, 0)})
        .compose(header_subst)
        .compose(type_specific_subst)
    )
    empty_array_fields_subst = Subst(
        {
            'ACCOUNTS_CELL': tvalueList(kavm, []),
            'APPLICATIONARGS_CELL': tvalueList(kavm, []),
            'FOREIGNAPPS_CELL': tvalueList(kavm, []),
            'FOREIGNASSETS_CELL': tvalueList(kavm, []),
        }
    )
    transaction_cell = fields_subst.apply(empty_transaction_cell)
    empty_fields_subst = Subst(
        {k: maybeTValue(kavm, None) for k in collectFreeVars(empty_transaction_cell)}
    )

    return empty_fields_subst.compose(empty_array_fields_subst).apply(transaction_cell)


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
