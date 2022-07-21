import pytest
from algosdk.future.transaction import SuggestedParams

from kavm_algod.algod import KAVMClient


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
