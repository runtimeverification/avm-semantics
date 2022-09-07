from typing import Any, Dict, Optional

import pytest
from algosdk import account
from algosdk.future.transaction import SuggestedParams
from algosdk.kmd import KMDClient
from algosdk.v2client.algod import AlgodClient

from kavm.algod import KAVMClient
from kavm.kavm import KAVM

from .constants import ALGOD_ADDRESS, ALGOD_TOKEN, KMD_ADDRESS, KMD_TOKEN


@pytest.fixture(autouse=True)
def integration_tests_config(request: Any) -> Any:
    return request.config


# inspred by http://www.nakedape.cc/python/pytest-dynamic-fixtures.html
def pytest_addoption(parser: Any) -> None:
    """
    Command line option for the AVM implementation: kavm or algod
    """
    parser.addoption(
        '--backend',
        action='store',
        default='algod',
        choices=['kalgod', 'algod'],
        help='AVM implementaion to run tests against',
    )


@pytest.fixture
def client(request: Any) -> AlgodClient:
    if request.config.getoption('--backend') == 'algod':
        return request.getfixturevalue('algod')
    else:
        return request.getfixturevalue('kalgod')


@pytest.fixture
def faucet(request: Any) -> Dict[str, str]:
    if request.config.getoption('--backend') == 'algod':
        return request.getfixturevalue('algod_faucet')
    else:
        return request.getfixturevalue('kalgod_faucet')


@pytest.fixture
def algod() -> AlgodClient:
    """AlgodClient connected to an Algorand Sandbox"""
    return AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


@pytest.fixture
def kmd() -> KMDClient:
    """KMDClient connected to an Algorand Sandbox"""
    return KMDClient(KMD_TOKEN, KMD_ADDRESS)


@pytest.fixture
def algod_faucet(algod: AlgodClient, kmd: KMDClient) -> Dict[str, Optional[Any]]:
    """
    Faucet address and private key of the active Algorand Sandbox
    """
    wallets = kmd.list_wallets()
    default_wallet = [w if w['name'] == 'unencrypted-default-wallet' else None for w in wallets][0]
    default_wallet_handle = kmd.init_wallet_handle(default_wallet['id'], '')
    default_wallet_keys = kmd.list_keys(default_wallet_handle)
    faucet_address = None
    for key in default_wallet_keys:
        account = algod.account_info(key)
        if account['status'] != 'Offline' and account['amount'] > 1000_000_000:
            faucet_address = key
            break

    faucet_private_key = kmd.export_key(default_wallet_handle, '', faucet_address)

    return {'address': faucet_address, 'private_key': faucet_private_key}


@pytest.fixture
def kalgod_faucet() -> Dict[str, Optional[Any]]:
    """
    Faucet address and private key of the active KAVM
    """

    faucet_private_key, faucet_address = account.generate_account()
    return {'address': faucet_address, 'private_key': faucet_private_key}


@pytest.fixture
def kalgod(kalgod_faucet: Dict[str, Optional[Any]]) -> KAVMClient:
    """Dummy KAVMAlgodClient"""
    algod_token = 'ktealktealktealkteal'
    algod_address = 'http://kteal:8080'

    return KAVMClient(algod_token, algod_address, kalgod_faucet['address'])


@pytest.fixture
def kavm(kalgod: KAVMClient) -> KAVM:
    return kalgod.kavm


@pytest.fixture
def suggested_params() -> SuggestedParams:
    """Dummy transaction parameters"""
    return SuggestedParams(fee=1000, first=0, last=1, gh='ktealktealktealkteal', flat_fee=True)
