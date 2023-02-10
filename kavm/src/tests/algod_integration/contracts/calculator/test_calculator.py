import base64
import contextlib
from typing import Any, Dict, List, Optional

import pytest
from algosdk import abi, account
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient

from kavm.algod import KAVMAtomicTransactionComposer

from ..calculator.calculator_pyteal import compile_to_teal


def create_app(
    client: AlgodClient,
    sender: str,
    private_key: str,
    approval_program: bytes,
    clear_program: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
) -> int:
    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    # tx_id = signed_txn.transaction.get_txid()

    # send transaction
    tx_id = client.send_transactions([signed_txn])

    # await confirmation
    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)

    print("TXID: ", tx_id)
    print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id: ", app_id)

    return app_id


def compile_program(client: AlgodClient, source_code: str) -> bytes:
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def generate_and_fund_account(client: AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = client.suggested_params()
    client.send_transaction(
        transaction.PaymentTxn(faucet['address'], sp, address, 10_000_000).sign(faucet['private_key'])
    )

    return {'address': address, 'private_key': private_key}


def compile_teal(client: AlgodClient, source_code: str) -> bytes:
    """Compile TEAL source code to binary for a transaction"""
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def create_contract(client: AlgodClient, app_creator: Dict[str, str]) -> abi.Contract:
    approval_source, clear_source, contract_interface = compile_to_teal()
    # Compile approval and clear TEAL programs
    approval_program = compile_teal(client, approval_source)
    clear_program = compile_teal(client, clear_source)

    # define empty schema
    global_schema = transaction.StateSchema(0, 0)
    local_schema = transaction.StateSchema(0, 0)

    # create new application
    app_id = create_app(
        client,
        app_creator['address'],
        app_creator['private_key'],
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    app_abi_spec = contract_interface.dictify()
    app_abi_spec['networks']['sandbox'] = abi.NetworkInfo(app_id=app_id).dictify()
    return abi.Contract.undictify(app_abi_spec)


@pytest.fixture
def user(client: AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    """User account for testing"""
    return generate_and_fund_account(client, faucet)


@pytest.fixture
def app_creator(client: AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    """Account that will create the application"""
    return generate_and_fund_account(client, faucet)


@pytest.fixture
def calculator_contract(client: AlgodClient, app_creator: Dict[str, str]) -> abi.Contract:
    """Calculator contract spec"""
    return create_contract(client, app_creator)


@pytest.mark.parametrize(
    'abi_method,method_args,expected_result,expectation',
    [
        ('sub', [2, 1], 1, contextlib.nullcontext()),
        ('div', [4, 2], 2, contextlib.nullcontext()),
        ('add', [1, 2], 3, contextlib.nullcontext()),
        ('mul', [2, 2], 4, contextlib.nullcontext()),
    ],
)
def test_calculator(
    client: AlgodClient,
    user: Dict[str, str],
    calculator_contract: abi.Contract,
    abi_method: str,
    method_args: List[int],
    expected_result: Optional[int],
    expectation: Any,
) -> None:
    sp = client.suggested_params()
    signer = AccountTransactionSigner(user['private_key'])

    app_id = calculator_contract.networks['sandbox'].app_id
    comp = KAVMAtomicTransactionComposer()
    comp.add_method_call(
        app_id,
        calculator_contract.get_method_by_name(abi_method),
        user['address'],
        sp,
        signer,
        method_args=method_args,
    )

    with expectation:
        resp = comp.execute(client, 2)
        assert resp.abi_results[0].return_value == expected_result
