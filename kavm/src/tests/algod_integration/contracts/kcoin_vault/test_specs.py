# type: ignore

import sys
from pathlib import Path

import algosdk
from pyk.kast.inner import KSort, KVariable
from pyk.prelude.kint import intToken

from kavm import constants
from kavm.kast.factory import KAVMTermFactory
from kavm.proof import KAVMProof
from kavm.pyk_utils import divInt, eqK, minusInt, plusInt


def test_mint_spec(initial_state_fixture):
    '''
    Demonstrate generating a K claim and proving it by starting from scratch

    * Deploy KCoin Vault contract (see 'initial_state_fixture' in 'conftest.py')
    * Request the accounts' states after deployment
    * construct the py-algorand-sdk transaction group to call the contract's 'mint' method
    * edit the account state and transaction group by adding symbolic variables
    * generate the K claim and prover it

    Run from the project root like this:
    poetry -C kavm/ run pytest kavm/src/tests/algod_integration/contracts/kcoin_vault/test_specs.py

    '''
    sys.setrecursionlimit(15000000)

    # this will deploy the contract and make the client availible.
    # Ideally we'd want Beaker to give as a client, but for now it is defined manually
    # in ./client.py.
    kcoin_vault_client, user_addr, user_private_key = initial_state_fixture
    Path('.kavm').mkdir(parents=True, exist_ok=True)
    kcoin_vault_client.algod.kavm.use_directory = Path('.kavm')

    # declare all K symbolic variables that we'll use in the spec
    KCOIN_ASSET_TOTAL_VAR = KVariable('KCOIN_ASSET_TOTAL', sort=KSort('Int'))
    # * sender's (also the app's creator) balances
    CREATOR_BALANCE_VAR = KVariable('CREATOR_BALANCE', sort=KSort('Int'))
    CREATOR_MIN_BALANCE_VAR = KVariable('CREATOR_MIN_BALANCE', sort=KSort('Int'))
    CREATOR_KCOIN_BALANCE_VAR = KVariable('CREATOR_KCOIN_BALANCE', sort=KSort('Int'))
    # * app account's balances
    APP_BALANCE_VAR = KVariable('APP_BALANCE', sort=KSort('Int'))
    APP_MIN_BALANCE_VAR = KVariable('APP_MIN_BALANCE', sort=KSort('Int'))
    APP_KCOIN_BALANCE_VAR = KVariable('APP_KCOIN_BALANCE', sort=KSort('Int'))
    # * payment transaction amount
    PAYMENT_AMOUNT_VAR = KVariable('PAYMENT_AMOUNT', sort=KSort('Int'))

    # generate the transacton group
    mint_group = kcoin_vault_client.call_mint(
        sender_addr=user_addr, sender_pk=user_private_key, microalgo_amount=10000, dry_run=True
    )

    # make payment amount symbolic
    mint_group[0].txn.amt = PAYMENT_AMOUNT_VAR

    payment_amount_bounds = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=minusInt(CREATOR_BALANCE_VAR, CREATOR_MIN_BALANCE_VAR),
        term=PAYMENT_AMOUNT_VAR,
    )
    # do ask for more than there is
    # TODO: need to make asset holdings availible for manipulation
    payment_amount_is_reasonable = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=divInt(APP_KCOIN_BALANCE_VAR, intToken(2)),
        term=PAYMENT_AMOUNT_VAR,
    )

    # request the creator account's state and introduce symbolic vars
    creator_account_dict = kcoin_vault_client.algod.account_info(address=user_addr)
    creator_account_dict['min-balance'] = CREATOR_MIN_BALANCE_VAR
    creator_account_dict['amount'] = CREATOR_BALANCE_VAR
    # make creator's KCoin holdings symbolic, we must traverse all app account's asset holdings
    # to find the right one
    for asset in creator_account_dict['assets']:
        if asset['asset-id'] == kcoin_vault_client.asset_id:
            asset['amount'] = CREATOR_KCOIN_BALANCE_VAR
    # formulate constraints in the creator's vars, to be added as preconditions
    creator_min_balance_bounds = KAVMTermFactory.range(
        lower_bound=constants.MIN_BALANCE, upper_bound=constants.MIN_BALANCE, term=CREATOR_MIN_BALANCE_VAR
    )
    creator_balance_bounds = KAVMTermFactory.range(
        lower_bound=creator_account_dict['min-balance'], upper_bound=KAVMTermFactory.pow64(), term=CREATOR_BALANCE_VAR
    )
    creator_kcoin_balance_bounds = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=KCOIN_ASSET_TOTAL_VAR,
        term=CREATOR_KCOIN_BALANCE_VAR,
    )

    # request the apps account's state and introduce symbolic vars
    app_account_dict = kcoin_vault_client.algod.account_info(
        address=algosdk.logic.get_application_address(kcoin_vault_client.app_id)
    )
    app_account_dict['min-balance'] = APP_MIN_BALANCE_VAR
    app_account_dict['amount'] = APP_BALANCE_VAR
    # make the KCoin asset total symbolic, we must traverse all app account's created assets
    # to find the right one
    for asset in app_account_dict['created-assets']:
        if asset['index'] == kcoin_vault_client.asset_id:
            asset['params']['total'] = KCOIN_ASSET_TOTAL_VAR
    # make app's KCoin holdings symbolic, we must traverse all app account's asset holdings
    # to find the right one
    for asset in app_account_dict['assets']:
        if asset['asset-id'] == kcoin_vault_client.asset_id:
            asset['amount'] = APP_KCOIN_BALANCE_VAR
    # formulate constraints on app's account vars, to be added as preconditions
    app_min_balance_bounds = KAVMTermFactory.range(
        lower_bound=constants.MIN_BALANCE, upper_bound=constants.MIN_BALANCE, term=APP_MIN_BALANCE_VAR
    )
    app_balance_bounds = KAVMTermFactory.range(
        lower_bound=CREATOR_MIN_BALANCE_VAR, upper_bound=KAVMTermFactory.pow64(), term=APP_BALANCE_VAR
    )
    app_kcoin_balance_bounds = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=KCOIN_ASSET_TOTAL_VAR,
        term=APP_KCOIN_BALANCE_VAR,
    )

    # total balances of Algos and KCoin should be in bounds
    total_system_balance_bounds = KAVMTermFactory.range(
        lower_bound=plusInt(CREATOR_MIN_BALANCE_VAR, CREATOR_MIN_BALANCE_VAR),
        upper_bound=KAVMTermFactory.pow64(),
        term=plusInt(CREATOR_BALANCE_VAR, APP_BALANCE_VAR),
    )
    total_system_kcoin_balance_bounds = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=KCOIN_ASSET_TOTAL_VAR,
        term=plusInt(CREATOR_KCOIN_BALANCE_VAR, APP_KCOIN_BALANCE_VAR),
    )

    # initialize thr proof object.
    # The constructor will collect lhs variables and create a substitution into
    # existential rhs variables. We will use those to formulate postconditions.
    proof = KAVMProof(
        kavm=kcoin_vault_client.algod.kavm,
        claim_name='kcoin-vault-mint',
        accts=[creator_account_dict, app_account_dict],
        sdk_txns=[txn_with_signer.txn for txn_with_signer in mint_group],
        teal_sources_dir=Path('.decompiled-teal'),
    )
    # add the preconditions we've defined above
    proof.require(
        [
            creator_min_balance_bounds,
            creator_balance_bounds,
            app_min_balance_bounds,
            app_balance_bounds,
            creator_kcoin_balance_bounds,
            app_kcoin_balance_bounds,
            total_system_balance_bounds,
            total_system_kcoin_balance_bounds,
            payment_amount_bounds,
            payment_amount_is_reasonable,
        ]
    )
    # formulate postconditions, using the existentuil variables
    # from the proof._evar_mapping substitution
    post_total_system_balance_bounds = KAVMTermFactory.range(
        lower_bound=plusInt(
            proof._evar_mapping[CREATOR_MIN_BALANCE_VAR],
            proof._evar_mapping[CREATOR_MIN_BALANCE_VAR],
        ),
        upper_bound=KAVMTermFactory.pow64(),
        term=plusInt(proof._evar_mapping[CREATOR_BALANCE_VAR], proof._evar_mapping[APP_BALANCE_VAR]),
    )
    post_total_system_kcoin_balance_bounds = KAVMTermFactory.range(
        lower_bound=0,
        upper_bound=KCOIN_ASSET_TOTAL_VAR,
        term=plusInt(proof._evar_mapping[CREATOR_KCOIN_BALANCE_VAR], proof._evar_mapping[APP_KCOIN_BALANCE_VAR]),
    )
    creator_balance_post = eqK(
        proof._evar_mapping[CREATOR_BALANCE_VAR],
        minusInt(CREATOR_BALANCE_VAR, PAYMENT_AMOUNT_VAR),
    )
    creator_kcoin_balance_post = eqK(
        proof._evar_mapping[CREATOR_KCOIN_BALANCE_VAR],
        plusInt(CREATOR_KCOIN_BALANCE_VAR, divInt(PAYMENT_AMOUNT_VAR, intToken(2))),
    )
    app_balance_post = eqK(
        proof._evar_mapping[APP_BALANCE_VAR],
        plusInt(APP_BALANCE_VAR, PAYMENT_AMOUNT_VAR),
    )
    app_kcoin_balance_post = eqK(
        proof._evar_mapping[APP_KCOIN_BALANCE_VAR],
        minusInt(APP_KCOIN_BALANCE_VAR, divInt(PAYMENT_AMOUNT_VAR, intToken(2))),
    )
    # add preconditions
    proof.ensure(
        [
            post_total_system_balance_bounds,
            post_total_system_kcoin_balance_bounds,
            creator_balance_post,
            creator_kcoin_balance_post,
            app_balance_post,
            app_kcoin_balance_post,
        ]
    )

    # run the prover. It will pretty-print the claim and place it in the .kavm/ for reference
    proof.prove()
