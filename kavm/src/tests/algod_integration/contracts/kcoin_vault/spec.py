# type: ignore

import os
import logging
import sys
from pathlib import Path

import algosdk
from algosdk.account import generate_account
from kavm.algod import KAVMClient
from kavm.kavm import KAVM

from kavm.proof import KAVMProof
from pyk.kast.outer import read_kast_definition

# from kavm.prover import AutoProver

# from kcoin_vault_pyteal import router


def test_spec(initial_state_fixture):
    sys.setrecursionlimit(15000000)
    kcoin_vault_client, user_addr, user_private_key = initial_state_fixture
    kcoin_vault_client.algod.kavm.use_directory = Path('.kavm')
    sdk_creator_account_dict = kcoin_vault_client.algod.account_info(address=user_addr)
    sdk_app_account_dict = kcoin_vault_client.algod.account_info(
        address=algosdk.logic.get_application_address(kcoin_vault_client.app_id)
    )

    mint_group = kcoin_vault_client.call_mint(
        sender_addr=user_addr, sender_pk=user_private_key, microalgo_amount=10000, dry_run=True
    )

    # kcoin_vault_client.algod.kavm._verification_definition = Path(os.environ.get('KAVM_VERIFICATION_DEFINITION_DIR'))
    proof = KAVMProof(
        kavm=kcoin_vault_client.algod.kavm,
        claim_name='test-claim',
        accts=[sdk_creator_account_dict, sdk_app_account_dict],
        sdk_txns=[txn_with_signer.txn for txn_with_signer in mint_group],
        teal_sources_dir=Path('.decompiled-teal'),
    )

    proof.prove()
    # prover = AutoProver(
    #     use_directory=Path('.kavm'),
    #     pyteal_module_name='tests.algod_integration.contracts.kcoin_vault.kcoin_vault_pyteal',
    #     app_id=1,
    #     sdk_app_creator_account_dict=sdk_creator_account_dict,
    #     sdk_app_account_dict=sdk_app_account_dict,
    # )
    # prover.prove('mint')


if __name__ == "__main__":
    sys.setrecursionlimit(15000000)
    logging.basicConfig(level=logging.INFO)

    creator_private_key, creator_addr = generate_account()
    creator_addr = str(creator_addr)
    algod = KAVMClient(faucet_address=creator_addr)
    algod.kavm.use_directory = Path('.kavm')

    proof = KAVMProof(kavm=algod.kavm, claim_name='test-claim', pre_accts=[], pre_txns=[])
    proof.kavm._write_claim_definition(proof.build_claim(), proof._claim_name)
