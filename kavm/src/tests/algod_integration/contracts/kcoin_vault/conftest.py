import logging
from typing import Tuple

import pytest
from algosdk.account import generate_account

from kavm.algod import KAVMClient

from ..kcoin_vault.client import ContractClient


@pytest.fixture(scope='session')
def initial_state_fixture() -> Tuple[ContractClient, str, str]:
    creator_private_key, creator_addr = generate_account()
    creator_addr = str(creator_addr)
    algod = KAVMClient(faucet_address=creator_addr, log_level=logging.ERROR)
    return ContractClient(algod, creator_addr, creator_private_key), str(creator_addr), creator_private_key
