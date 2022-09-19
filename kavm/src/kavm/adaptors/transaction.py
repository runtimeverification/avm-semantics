from base64 import b64decode
from typing import Any

from algosdk.constants import APPCALL_TXN, ASSETTRANSFER_TXN, PAYMENT_TXN
from algosdk.future.transaction import (
    ApplicationCallTxn,
    AssetTransferTxn,
    OnComplete,
    PaymentTxn,
    StateSchema,
    SuggestedParams,
    Transaction,
)
from pyk.kast import KApply, KAst, KInner, KSort, KToken, Subst
from pyk.kastManip import free_vars, split_config_from
from pyk.prelude import intToken

from kavm.pyk_utils import maybe_tvalue, tvalue, tvalue_list


class KAVMTransaction:
    """
    Convenience class represenring an Algorandtransaction in KAVM
    """

    # TODO: figure out how to easily remove the `kavm` argument, since this definition must be static.
    #       Currently, access to the K definition is required to figure out which cells are empty and put nothing into them
    def __init__(self, kavm: Any, txn: Transaction, txid: int) -> None:
        """
        Create a KAVM transaction cell.
        """

        self._transaction_cell = KAVMTransaction.transaction_to_k(kavm, txn, txid)
        self._txid = txid

    @property
    def txid(self) -> int:
        return self._txid

    @property
    def transaction_cell(self) -> KInner:
        return self._transaction_cell

    # TODO: txid must be assigned by KAVM itslef and must be str
    @staticmethod
    def transaction_to_k(kavm: Any, txn: Transaction, txid: int) -> KInner:
        """Convert a Transaction objet to a K cell"""
        empty_transaction_cell = kavm.definition.empty_config(KSort('TransactionCell'))

        header_subst = Subst(
            {
                'FEE_CELL': maybe_tvalue(txn.fee),
                'FIRSTVALID_CELL': maybe_tvalue(txn.first_valid_round),
                'LASTVALID_CELL': maybe_tvalue(txn.last_valid_round),
                'GENESISHASH_CELL': maybe_tvalue(txn.genesis_hash),
                'GENESISID_CELL': maybe_tvalue(txn.genesis_id),
                'SENDER_CELL': KToken(txn.sender.strip("'"), KSort('TAddressLiteral')),
                'TXTYPE_CELL': maybe_tvalue(txn.type),
                'TYPEENUM_CELL': maybe_tvalue(txn_type_to_type_enum(txn.type)),
                'GROUP_CELL': maybe_tvalue(txn.group),
                'LEASE_CELL': maybe_tvalue(txn.lease),
                'NOTE_CELL': maybe_tvalue(txn.note),
                'REKEYTO_CELL': maybe_tvalue(txn.rekey_to),
            }
        )
        type_specific_subst = None
        if txn.type == PAYMENT_TXN:
            type_specific_subst = Subst(
                {
                    'RECEIVER_CELL': KToken(txn.receiver.strip("'"), KSort('TAddressLiteral')),
                    'AMOUNT_CELL': maybe_tvalue(txn.amt),
                    'CLOSEREMAINDERTO_CELL': maybe_tvalue(txn.close_remainder_to),
                }
            )
        if txn.type == ASSETTRANSFER_TXN:
            raise NotImplementedError()
        if txn.type == APPCALL_TXN:
            type_specific_subst = Subst(
                {
                    'APPLICATIONID_CELL': maybe_tvalue(txn.index),
                    'ONCOMPLETION_CELL': maybe_tvalue(int(txn.on_complete))
                    if txn.on_complete is not None
                    else maybe_tvalue(None),
                    'ACCOUNTS_CELL': tvalue_list(txn.accounts) if txn.accounts is not None else tvalue_list([]),
                    'APPROVALPROGRAM_CELL': maybe_tvalue(txn.approval_program),
                    'APPROVALPROGRAMSRC_CELL': KToken('int 0', KSort('TealInputPgm')),
                    'CLEARSTATEPROGRAM_CELL': maybe_tvalue(txn.clear_program),
                    'CLEARSTATEPROGRAMSRC_CELL': KToken('int 1', KSort('TealInputPgm')),
                    'APPLICATIONARGS_CELL': tvalue_list(txn.app_args) if txn.app_args is not None else tvalue_list([]),
                    'FOREIGNAPPS_CELL': tvalue_list(txn.foreign_apps)
                    if txn.foreign_apps is not None
                    else tvalue_list([]),
                    'FOREIGNASSETS_CELL': tvalue_list(txn.foreign_assets)
                    if txn.foreign_assets is not None
                    else tvalue_list([]),
                    'GLOBALNUI_CELL': maybe_tvalue(txn.global_schema.num_uints)
                    if txn.global_schema is not None
                    else maybe_tvalue(0),
                    'GLOBALNBS_CELL': maybe_tvalue(txn.global_schema.num_byte_slices)
                    if txn.global_schema is not None
                    else maybe_tvalue(0),
                    'LOCALNUI_CELL': maybe_tvalue(txn.local_schema.num_uints)
                    if txn.local_schema is not None
                    else maybe_tvalue(0),
                    'LOCALNBS_CELL': maybe_tvalue(txn.local_schema.num_byte_slices)
                    if txn.local_schema is not None
                    else maybe_tvalue(0),
                    'EXTRAPROGRAMPAGES_CELL': maybe_tvalue(txn.extra_pages)
                    if txn.extra_pages is not None
                    else maybe_tvalue(0),
                    'LOGS_CELL': tvalue_list([]),
                    'LOGSIZE_CELL': tvalue(0),
                    'TXSCRATCH_CELL': KApply('.Map'),
                }
            )
        if type_specific_subst is None:
            raise ValueError(f'Transaction object {txn} is invalid')

        fields_subst = Subst({'TXID_CELL': intToken(txid)}).compose(header_subst).compose(type_specific_subst)
        empty_array_fields_subst = Subst(
            {
                'ACCOUNTS_CELL': tvalue_list([]),
                'APPLICATIONARGS_CELL': tvalue_list([]),
                'FOREIGNAPPS_CELL': tvalue_list([]),
                'FOREIGNASSETS_CELL': tvalue_list([]),
            }
        )
        empty_pgm_fileds_subst = Subst(
            {
                'APPROVALPROGRAM_CELL': maybe_tvalue(None),
                'APPROVALPROGRAMSRC_CELL': KToken('int 0', KSort('TealInputPgm')),
                'CLEARSTATEPROGRAM_CELL': maybe_tvalue(None),
                'CLEARSTATEPROGRAMSRC_CELL': KToken('int 1', KSort('TealInputPgm')),
            }
        )
        empty_service_fields_subst = Subst(
            {'LOGS_CELL': tvalue_list([]), 'LOGSIZE_CELL': tvalue(0), 'TXSCRATCH_CELL': KApply('.Map')}
        )
        transaction_cell = fields_subst.apply(empty_transaction_cell)
        empty_fields_subst = Subst({k: maybe_tvalue(None) for k in free_vars(empty_transaction_cell)})

        return empty_fields_subst.compose(
            empty_service_fields_subst.compose(empty_array_fields_subst.compose(empty_pgm_fileds_subst))
        ).apply(transaction_cell)


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


def transaction_from_k(kast_term: KAst) -> Transaction:
    """
    Covert a Kast term to one of the subclasses of the algosdk.Transaction

    Raise ValueError if the transaction is marformed
    """
    (_, tx_header) = split_config_from(kast_term)

    sp = SuggestedParams(
        int(tx_header['FEE_CELL'].token),
        int(tx_header['FIRSTVALID_CELL'].token),
        int(tx_header['LASTVALID_CELL'].token),
        tx_header['GENESISHASH_CELL'].token,
        flat_fee=True,
    )

    tx_type = tx_header['TXTYPE_CELL'].token.strip('"')
    result = None
    if tx_type == PAYMENT_TXN:
        (_, pay_tx_fields) = split_config_from(kast_term)
        result = PaymentTxn(
            sender=tx_header['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=pay_tx_fields['RECEIVER_CELL'].token.strip('"'),
            amt=int(pay_tx_fields['AMOUNT_CELL'].token),
        )
    elif tx_type == ASSETTRANSFER_TXN:
        (_, asset_transfer_tx_fields) = split_config_from(kast_term)
        result = AssetTransferTxn(
            sender=tx_header['SENDER_CELL'].token.strip('"'),
            sp=sp,
            receiver=asset_transfer_tx_fields['ASSETRECEIVER_CELL'].token.strip('"'),
            amt=int(asset_transfer_tx_fields['ASSETAMOUNT_CELL'].token.strip('"')),
            index=int(asset_transfer_tx_fields['XFERASSET_CELL'].token.strip('"')),
        )
    elif tx_type == APPCALL_TXN:
        (_, appcall_tx_fields) = split_config_from(kast_term)
        result = ApplicationCallTxn(
            sender=tx_header['SENDER_CELL'].token.strip('"'),
            sp=sp,
            index=int(appcall_tx_fields['APPLICATIONID_CELL'].token.strip('"')),
            on_complete=OnComplete(int(appcall_tx_fields['ONCOMPLETION_CELL'].token.strip('"'))),
            local_schema=StateSchema(
                int(appcall_tx_fields['LOCALNUI_CELL'].token.strip('"')),
                int(appcall_tx_fields['LOCALNBS_CELL'].token.strip('"')),
            ),
            global_schema=StateSchema(
                int(appcall_tx_fields['GLOBALNUI_CELL'].token.strip('"')),
                int(appcall_tx_fields['GLOBALNBS_CELL'].token.strip('"')),
            ),
            approval_program=b64decode(
                appcall_tx_fields['APPROVALPROGRAM_CELL'].token.strip('"')
                if hasattr(appcall_tx_fields['APPROVALPROGRAM_CELL'], 'token')
                else ''
            ),
            clear_program=b64decode(
                appcall_tx_fields['CLEARSTATEPROGRAM_CELL'].token.strip('"')
                if hasattr(appcall_tx_fields['CLEARSTATEPROGRAM_CELL'], 'token')
                else ''
            ),
            # TODO: handle array fields
            app_args=None,
            accounts=None,
            foreign_apps=None,
            foreign_assets=None,
            extra_pages=0,
        )
    else:
        raise ValueError(f'Cannot instantiate a Transaction of an unexpected type {tx_type}')

    return result
