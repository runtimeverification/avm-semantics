from typing import Any, Dict, List, Optional

from algosdk.future.transaction import PaymentTxn, SuggestedParams, Transaction
from pyk.kast import KApply, KAst, KInner, top_down
from pyk.prelude import intToken, stringToken


def int_token_cell(name: str, value: Optional[int]) -> KApply:
    """Construct a cell containing an Int token. Default to 0 if None is supplied."""

    if isinstance(value, int):
        token = intToken(value)
    elif value is None:
        token = intToken(0)
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'{name}', [token])


def string_token_cell(name: str, value: Optional[str]) -> KApply:
    """Construct a cell containing an String token. Default to the empty string if None is supplied."""

    if isinstance(value, str):
        token = stringToken(value)
    elif value is None:
        token = stringToken('')
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'{name}', [token])


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
    if txn.type == 'pay':
        type_specific_fields = payment_to_k(txn)
    if type_specific_fields is None:
        raise ValueError(f'Transaction object {txn} is invalid')
    return KApply('<transaction>', [header, type_specific_fields])


def payment_to_k(txn: PaymentTxn) -> KApply:
    """Convert a PaymentTxn objet to K configuration"""
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


def extract_cells(kast_term: KInner, label_names: List[str]) -> Dict[str, KInner]:
    """Iterate over the Kast term and extract a flat Python list of cells with the specified labels"""
    result: Dict[str, KAst] = {}

    def find_labels(x, labels):
        if isinstance(x, KApply) and x.label.name in labels:
            result[x.label.name] = x
        return x

    top_down(lambda x: find_labels(x, label_names), kast_term)
    return result


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

    txnType = txHeaderFields['<txType>'].args[0].token
    if txnType == '"pay"':
        payTxFields: Dict[str, Any] = {}
        payTxFields = extract_cells(kast_term, ['<receiver>', '<amount>', '<closeTo>'])
        return PaymentTxn(
            txHeaderFields['<sender>'].args[0].token.strip('"'),
            sp,
            payTxFields['<receiver>'].args[0].token.strip('"'),
            int(payTxFields['<amount>'].args[0].token),
        )
    else:
        raise ValueError(
            f'Cannot instantiate a Transaction of an unexpected type {txnType}'
        )
