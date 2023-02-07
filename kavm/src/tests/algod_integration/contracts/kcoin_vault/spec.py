# type: ignore

import sys
from pathlib import Path

import algosdk
from pyk.kast.inner import KSort, KVariable

from kavm.kast.factory import KAVMTermFactory
from kavm.proof import KAVMProof


def test_mint_spec(initial_state_fixture):
    '''
    Demonstrate generating a KAVM spec and proving it by starting from scratch

    * Deploy KCoin Vault contract (see 'initial_state_fixture' in 'conftest.py')
    * Request the concrete account state after deployment
    * construct the py-algorand-sdk transaction group to call the contract's 'mint' method
    * edit the account state and transaction group by adding symbolic variables for balances and
      payment amout
    * generate the K claim and prover it
    '''
    sys.setrecursionlimit(15000000)
    # this will deploy the contract and make the cline availible
    kcoin_vault_client, user_addr, user_private_key = initial_state_fixture

    kcoin_vault_client.algod.kavm.use_directory = Path('.kavm')

    mint_group = kcoin_vault_client.call_mint(
        sender_addr=user_addr, sender_pk=user_private_key, microalgo_amount=10000, dry_run=True
    )

    sdk_app_account_dict = kcoin_vault_client.algod.account_info(
        address=algosdk.logic.get_application_address(kcoin_vault_client.app_id)
    )

    # request the creator account's modified state and make the balance symbolic
    creator_balance_var = KVariable('CREATOR_BALANCE', sort=KSort('Int'))
    payment_amount_var = KVariable('PAYMENT_AMOUNT', sort=KSort('Int'))
    symbolic_creator_account_dict = kcoin_vault_client.algod.account_info(address=user_addr)
    symbolic_creator_account_dict['amount'] = creator_balance_var
    # make payment amount symbolic
    mint_group[0].txn.amt = payment_amount_var

    creator_balance_bounds = KAVMTermFactory.range(lower_bound=1000000, upper_bound=2000000, term=creator_balance_var)
    payment_amount_bounds = KAVMTermFactory.range(lower_bound=1000, upper_bound=10000, term=payment_amount_var)

    proof = KAVMProof(
        kavm=kcoin_vault_client.algod.kavm,
        claim_name='kcoin-vault-mint',
        accts=[symbolic_creator_account_dict, sdk_app_account_dict],
        sdk_txns=[txn_with_signer.txn for txn_with_signer in mint_group],
        teal_sources_dir=Path('.decompiled-teal'),
        preconditions=[creator_balance_bounds, payment_amount_bounds],
    )

    proof.prove()
