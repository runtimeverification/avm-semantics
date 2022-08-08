from typing import Any, Dict, Optional, Union

from algosdk.future.transaction import PaymentTxn, SuggestedParams, Transaction
from pyk.kast import KApply, KAst
from pyk.prelude import intToken, stringToken


def int_token_cell(name: str, value: Optional[int]) -> KApply:
    """Construct a cell containing an Int token. Default to 0 if None is supplied."""

    if isinstance(value, int):
        token = intToken(value)
    elif value is None:
        token = intToken(0)
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'<{name}>', [token])


def string_token_cell(name: str, value: Optional[str]) -> KApply:
    """Construct a cell containing an String token. Default to the empty string if None is supplied."""

    if isinstance(value, str):
        token = stringToken(value)
    elif value is None:
        token = stringToken('')
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'<{name}>', [token])


def transaction_to_k(txn: Transaction) -> KApply:
    """Convert a Transaction objet to K configuration"""
    header = KApply(
        '<txHeader>',
        [
            int_token_cell('fee', txn.fee),
            int_token_cell('firstValid', txn.first_valid_round),
            int_token_cell('lastValid', txn.last_valid_round),
            string_token_cell('genesisHash', txn.genesis_hash),
            string_token_cell('sender', txn.sender),
            string_token_cell('txType', txn.type),
            # TODO: convert type to type enum, an int token
            string_token_cell('typeEnum', txn.type),
            # TODO: 'group' should probably be int, investigate
            string_token_cell('group', str(txn.group)),
            string_token_cell('genesisID', str(txn.genesis_id)),
            string_token_cell('lease', str(txn.lease)),
            string_token_cell('rekeyTo', str(txn.rekey_to)),
        ],
    )
    type_specific_fields = None
    if txn.type == 'pay':
        type_specific_fields = payment_fields_to_k(txn)
    if type_specific_fields is None:
        raise ValueError(f'Transaction object {txn} is invalid')
    return KApply(
        '<transaction>',
        [header, type_specific_fields],
    )


def payment_fields_to_k(txn: PaymentTxn) -> KApply:
    """Convert a PaymentTxn objet to K configuration"""
    config = KApply(
        '<payTxFields>',
        [
            string_token_cell('receiver', txn.receiver),
            int_token_cell('amount', txn.amt),
            string_token_cell('closeRemainderTo', txn.close_remainder_to),
        ],
    )
    return config


def transaction_from_k(kast_term: KAst) -> Transaction:
    term_dict = kast_term.to_dict()
    txHeader: Dict[str, Any] = {}
    payTxFields: Dict[str, Any] = {}
    for i, term in enumerate(term_dict['args']):
        txHeader = term if term['label']['name'] == '<txHeader>' else txHeader
        payTxFields = term if term['label']['name'] == '<payTxFields>' else payTxFields
    sender: Dict[str, Any] = {}
    sp: Dict[str, Any] = {}
    note: Dict[str, Any] = {}
    lease: Dict[str, Any] = {}
    txn_type: Dict[str, Any] = {}
    rekey_to: Dict[str, Any] = {}
    fee: Dict[str, Any] = {}
    first_valid: Dict[str, Any] = {}
    last_valid: Dict[str, Any] = {}
    genesis_hash: Dict[str, Any] = {}
    for i, term in enumerate(txHeader['args']):
        sender = term if term['label']['name'] == '<sender>' else sender
        note = term if term['label']['name'] == '<note>' else note
        lease = term if term['label']['name'] == '<lease>' else lease
        txn_type = term if term['label']['name'] == '<txType>' else txn_type
        rekey_to = term if term['label']['name'] == '<rekeyTo>' else rekey_to
        fee = term if term['label']['name'] == '<fee>' else fee
        first_valid = term if term['label']['name'] == '<firstValid>' else first_valid
        last_valid = term if term['label']['name'] == '<lastValid>' else last_valid
        genesis_hash = (
            term if term['label']['name'] == '<genesisHash>' else genesis_hash
        )
    receiver: Dict[str, Any] = {}
    amount: Dict[str, Any] = {}
    close_to: Dict[str, Any] = {}
    for i, term in enumerate(payTxFields['args']):
        receiver = term if term['label']['name'] == '<receiver>' else receiver
        amount = term if term['label']['name'] == '<amount>' else amount
        close_to = term if term['label']['name'] == '<close_to>' else close_to

    sp = SuggestedParams(
        int(fee['args'][0]['token']),
        int(first_valid['args'][0]['token']),
        int(last_valid['args'][0]['token']),
        genesis_hash['args'][0]['token'],
        flat_fee=True,
    )

    return PaymentTxn(
        sender['args'][0]['token'].strip('"'),
        sp,
        receiver['args'][0]['token'].strip('"'),
        int(amount['args'][0]['token']),
    )
