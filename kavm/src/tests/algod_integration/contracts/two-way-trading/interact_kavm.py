# type: ignore

# flake8: noqa

import base64
import logging
import os
import sys
from datetime import timedelta

import algosdk
import pytest
from algosdk import future
from algosdk.abi import *
from algosdk.account import *
from algosdk.atomic_transaction_composer import *
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.future import *
from algosdk.mnemonic import *
from algosdk.v2client.algod import *
from algosdk.v2client.algod import AlgodClient
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from kavm.algod import KAVMAtomicTransactionComposer, KAVMClient


def setup_app(
    client,
    sender,
    private_key,
) -> Tuple[Contract, int]:
    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval and clear TEAL programs
    with open(os.path.join(path, "./approval.teal")) as f:
        approval_source = f.read()

    with open(os.path.join(path, "clear.teal")) as f:
        clear_source = f.read()

    # Compile approval and clear TEAL programs
    approval_program = compile_program(client, approval_source)
    clear_program = compile_program(client, clear_source)

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

    # print("TXID: ", tx_id)
    # print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))

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

    # read json and create ABI Contract description
    with open(os.path.join(path, "contract.json")) as f:
        js = f.read()
    c = Contract.from_json(js)

    return (c, app_id)


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


@pytest.fixture(scope='session')
def initial_state() -> Tuple[AlgodClient, Contract, int, str, str, int]:

    creator_private_key, creator_addr = generate_account()
    # Manually setup Algod Client
    client = KAVMClient(faucet_address=creator_addr, log_level=logging.DEBUG)

    # create new application
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


MIN_ARG_VALUE = 10
MAX_ARG_VALUE = 1 * 10**6


@settings(deadline=(timedelta(seconds=2)), max_examples=25, phases=[Phase.generate])
@given(
    microalgos=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
)
def test_contract(initial_state, microalgos: int) -> None:
    client, contract, app_id, creator_addr, creator_private_key, asset_id = initial_state
    minted = call_mint(client, contract, app_id, creator_addr, creator_private_key, asset_id, microalgos)
    got_back = call_burn(client, contract, app_id, creator_addr, creator_private_key, asset_id, minted)
    assert abs(got_back - microalgos) <= 1


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stdout)

    creator_private_key, creator_addr = generate_account()
    # Manually setup Algod Client
    client = KAVMClient(faucet_address=creator_addr)

    # create new application
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

    resp = comp.execute(client, 2, override_tx_ids=['0', '1'])
    # for result in resp.abi_results:
    #     print(f"{result.method.name} => {result.return_value}")

    asset_id = resp.abi_results[0].return_value

    # Opt-in to app's asset
    comp = KAVMAtomicTransactionComposer()
    comp.add_transaction(
        TransactionWithSigner(future.transaction.AssetOptInTxn(sender=creator_addr, sp=sp, index=asset_id), signer)
    )
    comp.execute(client, 2)

    microalgos = 100
    minted = call_mint(client, contract, app_id, creator_addr, creator_private_key, asset_id, microalgos)
    got_back = call_burn(client, contract, app_id, creator_addr, creator_private_key, asset_id, minted)
    assert abs(got_back - microalgos) <= 1
