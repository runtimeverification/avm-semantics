from typing import Any

from algosdk.future.transaction import PaymentTxn, SuggestedParams, Transaction
from pyk.kast import KApply, KAst
from pyk.prelude import intToken, stringToken


def transaction_to_k(txn: Transaction) -> KApply:
    """Convert a Transaction objet to K configuration"""
    header = KApply(
        '<txHeader>',
        [
            KApply(
                '<fee>',
                [
                    intToken(
                        txn.fee,
                    )
                ],
            ),
            KApply(
                '<firstValid>',
                [intToken(txn.first_valid_round)],
            ),
            KApply(
                '<lastValid>',
                [
                    intToken(
                        txn.last_valid_round,
                    )
                ],
            ),
            KApply(
                '<genesisHash>',
                [
                    stringToken(
                        f'{txn.genesis_hash}',
                    )
                ],
            ),
            KApply(
                '<sender>',
                [
                    stringToken(
                        f'{txn.sender}',
                    )
                ],
            ),
            KApply(
                '<txType>',
                [
                    stringToken(
                        f'{txn.type}',
                    )
                ],
            ),
            # TODO: convert type to type enum
            KApply(
                '<typeEnum>',
                [
                    stringToken(
                        f'{txn.type}',
                    )
                ],
            ),
            KApply(
                '<group>',
                [
                    stringToken(
                        f'{txn.group}',
                    )
                ],
            ),
            KApply(
                '<genesisID>',
                [
                    stringToken(
                        f'{txn.genesis_id}',
                    )
                ],
            ),
            KApply(
                '<lease>',
                [
                    stringToken(
                        f'{txn.lease}',
                    )
                ],
            ),
            KApply(
                '<rekeyTo>',
                [
                    stringToken(
                        f'{txn.rekey_to}',
                    )
                ],
            ),
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
            KApply(
                '<receiver>',
                [
                    stringToken(
                        f'{txn.receiver}',
                    )
                ],
            ),
            KApply(
                '<amount>',
                [
                    intToken(
                        txn.amt,
                    )
                ],
            ),
            KApply(
                '<closeRemainderTo>',
                [
                    stringToken(
                        f'{txn.close_remainder_to}',
                    )
                ],
            ),
        ],
    )
    return config


def transaction_from_k(kast_term: KAst) -> Transaction:
    term_dict = kast_term.to_dict()
    txHeader: dict[str, Any] = {}
    payTxFields: dict[str, Any] = {}
    for i, term in enumerate(term_dict['args']):
        txHeader = term if term['label']['name'] == '<txHeader>' else txHeader
        payTxFields = term if term['label']['name'] == '<payTxFields>' else payTxFields
    sender: dict[str, Any] = {}
    sp: dict[str, Any] = {}
    note: dict[str, Any] = {}
    lease: dict[str, Any] = {}
    txn_type: dict[str, Any] = {}
    rekey_to: dict[str, Any] = {}
    fee: dict[str, Any] = {}
    first_valid: dict[str, Any] = {}
    last_valid: dict[str, Any] = {}
    genesis_hash: dict[str, Any] = {}
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
    receiver: dict[str, Any] = {}
    amount: dict[str, Any] = {}
    close_to: dict[str, Any] = {}
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
