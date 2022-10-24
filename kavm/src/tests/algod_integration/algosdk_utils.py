import typing
from base64 import b64decode, b64encode
from typing import Dict, Optional

from algosdk import account
from algosdk.future import transaction
from algosdk.v2client import algod


@typing.no_type_check
def list_to_dict_state(l):
    d = {}
    for item in l:
        d[item['key']] = item['value']
    return d


@typing.no_type_check
def list_to_dict_apps_created(l):
    d = {}
    for item in l:
        d[item['id']] = item
    return d


def generate_and_fund_account(client: algod.AlgodClient, faucet: Dict[str, str]) -> Dict[str, str]:
    private_key, address = account.generate_account()

    # fund the account from the faucet
    sp = client.suggested_params()
    client.send_transaction(
        transaction.PaymentTxn(faucet['address'], sp, address, 1_000_000).sign(faucet['private_key'])
    )

    return {'address': address, 'private_key': private_key}


def compile_program(client: algod.AlgodClient, source_code: str) -> bytes:
    compile_response = client.compile(source_code)
    return b64decode(compile_response["result"])


def get_created_app_id(client: algod.AlgodClient, txn_id: int) -> Optional[int]:
    return client.pending_transaction_info(txn_id)['application-index']


def get_balance(client: algod.AlgodClient, address: str) -> Optional[int]:
    return client.account_info(address)['amount']


def get_local_int(client: algod.AlgodClient, app_id: int, address: str, key: str) -> Optional[int]:
    local_state = list_to_dict_state(
        list_to_dict_apps_created(client.account_info(address)['apps-local-state'])[app_id]['key-value']
    )
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    return local_state[encoded_key]['uint']


def get_local_bytes(client: algod.AlgodClient, app_id: int, address: str, key: str) -> Optional[bytes]:
    local_state = list_to_dict_state(
        list_to_dict_apps_created(client.account_info(address)['apps-local-state'])[app_id]['key-value']
    )
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    value = local_state[encoded_key]['bytes']
    if value:
        return b64decode(value.encode('ascii'))
    else:
        return None


def get_global_int(client: algod.AlgodClient, app_id: int, key: str) -> Optional[int]:
    global_state = list_to_dict_state(client.application_info(app_id)['params']['global-state'])
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    return global_state[encoded_key]['uint']


def get_global_bytes(client: algod.AlgodClient, app_id: int, key: str) -> Optional[bytes]:
    global_state = list_to_dict_state(client.application_info(app_id)['params']['global-state'])
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    value = global_state[encoded_key]['bytes']
    if value:
        return b64decode(value.encode('ascii'))
    else:
        return None
