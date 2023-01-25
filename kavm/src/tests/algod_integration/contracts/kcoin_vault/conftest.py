import logging
from typing import Tuple

import pytest
from algosdk.account import generate_account
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import AccountTransactionSigner, TransactionWithSigner

from kavm.algod import KAVMClient, KAVMAtomicTransactionComposer

from ..kcoin_vault.client import ContractClient


@pytest.fixture(scope='session')
def initial_state_fixture() -> Tuple[ContractClient, str, str]:
    creator_private_key, creator_addr = generate_account()
    creator_addr = str(creator_addr)
    algod = KAVMClient(faucet_address=creator_addr, log_level=logging.ERROR)
    client = ContractClient(
        algod,
        pyteal_code_module='tests.algod_integration.contracts.kcoin_vault.kcoin_vault_pyteal',
    )

    # deploy K Coin Vault
    client.deploy(creator_addr=creator_addr, creator_private_key=creator_private_key, app_account_microalgos=10**6)

    # Opt-in to app's asset
    comp = KAVMAtomicTransactionComposer()
    comp.add_transaction(
        TransactionWithSigner(
            transaction.AssetOptInTxn(sender=creator_addr, sp=client.suggested_params, index=client.asset_id),
            signer=AccountTransactionSigner(creator_private_key),
        )
    )
    comp.execute(client.algod, 2, override_tx_ids=['0'])
    return client, str(creator_addr), creator_private_key
