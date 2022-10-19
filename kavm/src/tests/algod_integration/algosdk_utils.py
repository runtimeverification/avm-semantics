from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import encode_address
from typing import Optional
from base64 import b32decode, b32encode, b64decode, b64encode


def list_to_dict_state(l):
    d = {}
    for item in l:
        d[item['key']] = item['value']
    return d


def list_to_dict_apps_created(l):
    d = {}
    for item in l:
        d[item['id']] = item
    return d


def get_created_app_id(client: AlgodClient, txn_id: int) -> Optional[int]:
    return client.pending_transaction_info(txn_id)['application-index']


def get_balance(client: AlgodClient, address: str) -> Optional[int]:
    return client.account_info(address)['amount']


def get_local_int(client: AlgodClient, app_id: int, address: str, key: str) -> Optional[int]:
    local_state = list_to_dict_state(
        list_to_dict_apps_created(client.account_info(address)['apps-local-state'])[app_id]['key-value']
    )
    print(local_state)
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    return local_state[encoded_key]['uint']


def get_local_bytes(client: AlgodClient, app_id: int, address: str, key: str) -> Optional[str]:
    return b64decode(
        list_to_dict_state(
            list_to_dict_apps_created(client.account_info(address)['apps-local-state'])[app_id]['key-value']
        )[key]['bytes']
    ).decode('ascii')


def get_global_int(client: AlgodClient, app_id: int, key: str) -> Optional[int]:
    global_state = list_to_dict_state(client.application_info(app_id)['params']['global-state'])
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    return global_state[encoded_key]['uint']


def get_global_bytes(client: AlgodClient, app_id: int, key: str) -> Optional[str]:
    global_state = list_to_dict_state(client.application_info(app_id)['params']['global-state'])
    encoded_key = b64encode(key.encode('ascii')).decode('ascii')
    return global_state[encoded_key]['bytes']
