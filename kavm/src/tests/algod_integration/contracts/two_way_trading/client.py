# type: ignore

# flake8: noqa

import base64
import logging
import sys

import algosdk
from algosdk import future
from algosdk.abi import *
from algosdk.account import *
from algosdk.atomic_transaction_composer import *
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.future import *
from algosdk.mnemonic import *
from algosdk.v2client.algod import *
from algosdk.v2client.algod import AlgodClient

from kavm.algod import KAVMAtomicTransactionComposer, KAVMClient

from .contract import compile_to_teal


def compile_teal(client, source_code):
    """Compile TEAL source code to binary for a transaction"""
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def setup_app(
    client,
    sender,
    private_key,
) -> Tuple[Contract, int]:
    """Compile the PyTeal contract and deploy it"""

    approval_source, clear_source, contract = compile_to_teal()

    # Compile approval and clear TEAL programs
    approval_program = compile_teal(client, approval_source)
    clear_program = compile_teal(client, clear_source)

    # create app
    on_complete = future.transaction.OnComplete.NoOpOC.real
    params = client.suggested_params()

    global_schema = future.transaction.StateSchema(num_uints=2, num_byte_slices=0)
    txn = future.transaction.ApplicationCreateTxn(
        sender, params, on_complete, approval_program, clear_program, global_schema, local_schema=None
    )

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    client.send_transactions([signed_txn])
    future.transaction.wait_for_confirmation(client, tx_id, 4)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    # print("Created new app-id: ", app_id)

    ## Fund app with algos
    fund_app_account_txn = future.transaction.PaymentTxn(
        sender=sender, sp=params, receiver=algosdk.logic.get_application_address(app_id), amt=10**6
    )
    signed_txn = fund_app_account_txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    future.transaction.wait_for_confirmation(client, tx_id, 4)

    return (contract, app_id)


def initial_state() -> Tuple[AlgodClient, Contract, int, str, str, int]:
    """
    Setup initial state for testing:
      * generate the app's creator account
      * trigger creation of app's asset
      * creator opts into app's asset
    """
    creator_private_key, creator_addr = generate_account()
    client = KAVMClient(faucet_address=creator_addr, log_level=logging.DEBUG)

    (contract, app_id) = setup_app(
        client=client,
        sender=creator_addr,
        private_key=creator_private_key,
    )

    signer = AccountTransactionSigner(creator_private_key)
    sp = client.suggested_params()
    sp.flat_fee = True
    sp.fee = 1000

    # Initialize App's asset
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(app_id, contract.get_method_by_name("init_asset"), creator_addr, sp, signer)

    resp = comp.execute(client, 2, override_tx_ids=['0'])
    # for result in resp.abi_results:
    #     print(f"{result.method.name} => {result.return_value}")

    asset_id = resp.abi_results[0].return_value

    # Opt-in to app's asset
    comp = KAVMAtomicTransactionComposer()
    comp.add_transaction(
        TransactionWithSigner(future.transaction.AssetOptInTxn(sender=creator_addr, sp=sp, index=asset_id), signer)
    )
    resp = comp.execute(client, 2, override_tx_ids=['0'])
    return (client, contract, app_id, creator_addr, creator_private_key, asset_id)


def call_mint(
    client: AlgodClient,
    contract: Contract,
    app_id: int,
    sender_addr: str,
    sender_pk: str,
    asset_id: int,
    microalgo_amount: int,
) -> int:
    """
    Call app's 'mint' method
    """
    comp = KAVMAtomicTransactionComposer()
    signer = AccountTransactionSigner(sender_pk)
    sp = client.suggested_params()
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
                future.transaction.PaymentTxn(
                    sender=sender_addr,
                    sp=sp,
                    receiver=algosdk.logic.get_application_address(app_id),
                    amt=microalgo_amount,
                ),
                signer,
            )
        ],
    )
    resp = comp.execute(client, 2, override_tx_ids=['0', '1'])
    return resp.abi_results[0].return_value


def call_burn(
    client: AlgodClient,
    contract: Contract,
    app_id: int,
    sender_addr: str,
    sender_pk: str,
    asset_id: int,
    asset_amount: int,
) -> int:
    """
    Call app's 'burn' method
    """
    comp = KAVMAtomicTransactionComposer()
    signer = AccountTransactionSigner(sender_pk)
    sp = client.suggested_params()
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
                future.transaction.AssetTransferTxn(
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
    resp = comp.execute(client, 2, override_tx_ids=['0', '1'])
    return resp.abi_results[0].return_value


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stdout)

    client, contract, app_id, creator_addr, creator_private_key, asset_id = initial_state()

    microalgos = 100
    minted = call_mint(client, contract, app_id, creator_addr, creator_private_key, asset_id, microalgos)
    got_back = call_burn(client, contract, app_id, creator_addr, creator_private_key, asset_id, minted)
    assert abs(got_back - microalgos) <= 1
