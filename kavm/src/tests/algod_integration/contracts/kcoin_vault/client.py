import base64
from typing import List

import pytest
import algosdk
from algosdk.atomic_transaction_composer import AccountTransactionSigner, TransactionWithSigner
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
import pyteal
import importlib

from kavm.algod import KAVMAtomicTransactionComposer


def compile_teal(client: AlgodClient, source_code: str) -> bytes:
    """Compile TEAL source code to binary for a transaction"""
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


class ContractClient:
    '''
    The initializer sets up initial state for testing:
      * create the app
      * trigger creation of app's asset
      * creator opts into app's asset
    '''

    def __init__(self, algod: AlgodClient, pyteal_code_module: str) -> None:
        self.algod = algod
        self.suggested_params = self.algod.suggested_params()
        self.suggested_params.flat_fee = True
        self.suggested_params.fee = 2000

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(
                target=pyteal.Router,
                name='hoare_method',
                value=lambda *args, **kwargs: lambda _: None,
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.Router,
                name='precondition',
                value=lambda *args, **kwargs: lambda _: None,
                raising=False,
            )
            monkeypatch.setattr(
                target=pyteal.Router,
                name='postcondition',
                value=lambda *args, **kwargs: lambda _: None,
                raising=False,
            )
            config = importlib.import_module(pyteal_code_module)
            approval_source, clear_source, self.contract_interface = config.compile_to_teal()

        # Compile approval and clear TEAL programs
        self.approval_program = compile_teal(algod, approval_source)
        self.clear_program = compile_teal(algod, clear_source)

        # initialize app_id and asset_id to 0
        self.app_id = 0
        self.asset_id = 0

    def deploy(
        self,
        creator_addr: str,
        creator_private_key: str,
        app_account_microalgos: int = 10**6,
    ):
        # create app
        on_complete = transaction.OnComplete.NoOpOC.real
        global_schema = transaction.StateSchema(num_uints=2, num_byte_slices=0)
        txn = transaction.ApplicationCreateTxn(
            creator_addr,
            self.suggested_params,
            on_complete,
            self.approval_program,
            self.clear_program,
            global_schema,
            local_schema=None,
        )
        signed_txn = txn.sign(creator_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.algod.send_transactions([signed_txn])
        transaction.wait_for_confirmation(self.algod, tx_id, 4)

        transaction_response = self.algod.pending_transaction_info(tx_id)
        self.app_id = transaction_response["application-index"]

        # Fund app with algos
        fund_app_account_txn = transaction.PaymentTxn(
            sender=creator_addr,
            sp=self.suggested_params,
            receiver=algosdk.logic.get_application_address(self.app_id),
            amt=app_account_microalgos,
        )
        signed_txn = fund_app_account_txn.sign(creator_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.algod.send_transactions([signed_txn])
        transaction.wait_for_confirmation(self.algod, tx_id, 4)

        # Initialize App's asset
        signer = AccountTransactionSigner(creator_private_key)
        comp = KAVMAtomicTransactionComposer()
        comp.add_method_call(
            self.app_id,
            self.contract_interface.get_method_by_name("init_asset"),
            creator_addr,
            self.suggested_params,
            signer,
        )
        resp = comp.execute(self.algod, 2, override_tx_ids=['0'])
        self.asset_id = resp.abi_results[0].return_value

    def call_mint(
        self, sender_addr: str, sender_pk: str, microalgo_amount: int, dry_run: bool = False
    ) -> int | List[TransactionWithSigner]:
        """
        Call app's 'mint' method
        """
        contract = self.contract_interface
        app_id = self.app_id
        asset_id = self.asset_id
        comp = KAVMAtomicTransactionComposer()
        signer = AccountTransactionSigner(sender_pk)
        sp = self.algod.suggested_params()
        sp.flat_fee = True
        sp.fee = 2000
        comp.add_method_call(
            app_id,
            contract.get_method_by_name('mint'),
            sender_addr,
            sp,
            signer,
            foreign_assets=[asset_id],
            method_args=[
                TransactionWithSigner(
                    transaction.PaymentTxn(
                        sender=sender_addr,
                        sp=sp,
                        receiver=algosdk.logic.get_application_address(app_id),
                        amt=microalgo_amount,
                    ),
                    signer,
                )
            ],
        )
        if not dry_run:
            resp = comp.execute(self.algod, 2, override_tx_ids=['0', '1'])
            return resp.abi_results[0].return_value
        else:
            return comp.build_group()

    def call_burn(
        self,
        sender_addr: str,
        sender_pk: str,
        asset_amount: int,
    ) -> int:
        """
        Call app's 'burn' method
        """
        contract = self.contract_interface
        app_id = self.app_id
        asset_id = self.asset_id
        comp = KAVMAtomicTransactionComposer()
        signer = AccountTransactionSigner(sender_pk)
        sp = self.algod.suggested_params()
        sp.flat_fee = True
        sp.fee = 2000
        comp.add_method_call(
            app_id,
            contract.get_method_by_name("burn"),
            sender_addr,
            sp,
            signer,
            foreign_assets=[asset_id],
            method_args=[
                TransactionWithSigner(
                    transaction.AssetTransferTxn(
                        sender=sender_addr,
                        sp=sp,
                        index=asset_id,
                        receiver=algosdk.logic.get_application_address(app_id),
                        amt=asset_amount,
                    ),
                    signer,
                )
            ],
        )
        resp = comp.execute(self.algod, 2, override_tx_ids=['0', '1'])
        return resp.abi_results[0].return_value
