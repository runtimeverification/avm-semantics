import pytest
from algosdk.future.transaction import SuggestedParams
from algosdk.v2client.algod import AlgodClient
from algosdk.kmd import KMDClient

from kavm_algod.algod import KAVMClient
from .constants import ALGOD_TOKEN, ALGOD_ADDRESS, KMD_TOKEN, KMD_ADDRESS


@pytest.fixture
def algod():
    """AlgodClient connected to an Algorand Sandbox"""
    return AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


@pytest.fixture
def kmd():
    """KMDClient connected to an Algorand Sandbox"""
    return KMDClient(KMD_TOKEN, KMD_ADDRESS)


@pytest.fixture
def faucet(algod, kmd):
    """
    Faucet address and private key of the active Algorand Sandbox
    """
    wallets = kmd.list_wallets()
    default_wallet = [
        w if w["name"] == "unencrypted-default-wallet" else None for w in wallets
    ][0]
    default_wallet_handle = kmd.init_wallet_handle(default_wallet["id"], "")
    default_wallet_keys = kmd.list_keys(default_wallet_handle)
    faucet_address = None
    for key in default_wallet_keys:
        account = algod.account_info(key)
        if account["status"] != "Offline" and account["amount"] > 1000_000_000:
            faucet_address = key
            break
        pass

    faucet_private_key = kmd.export_key(default_wallet_handle, "", faucet_address)

    return {"address": faucet_address, "private_key": faucet_private_key}


@pytest.fixture
def kalgod():
    """Dummy KAVMAlgodClient"""
    algod_token = "ktealktealktealkteal"
    algod_address = "http://kteal:8080"
    return KAVMClient(algod_token, algod_address)


@pytest.fixture
def suggested_params():
    """Dummy transaction parameters"""
    return SuggestedParams(
        fee=1000, first=0, last=1, gh="ktealktealktealkteal", flat_fee=True
    )
