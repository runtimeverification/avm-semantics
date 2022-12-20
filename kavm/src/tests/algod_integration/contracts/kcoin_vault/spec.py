# type: ignore

import logging
import sys

from kavm.prover import AutoProver

# from kcoin_vault_pyteal import router


sdk_app_creator_account_dict = {
    "address": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
    "amount": 999999000000,
    "amount-without-pending-rewards": None,
    "apps-local-state": None,
    "apps-total-schema": None,
    "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": False}],
    "created-apps": [
        {
            "id": 1,
            "params": {
                "creator": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
                "approval-program": "approval.teal",
                "clear-state-program": "clear.teal",
                "local-state-schema": {"nbs": 0, "nui": 0},
                "global-state-schema": {"nbs": 0, "nui": 2},
                "global-state": [
                    {"key": "YXNzZXRfaWQ=", "value": {"bytes": "", "type": 2, "uint": 1}},
                    {"key": "ZXhjaGFuZ2VfcmF0ZQ==", "value": {"bytes": "", "type": 2, "uint": 2}},
                ],
            },
        }
    ],
    "created-assets": [],
    "participation": None,
    "pending-rewards": None,
    "reward-base": None,
    "rewards": None,
    "round": None,
    "status": None,
    "sig-type": None,
    "auth-addr": None,
}

sdk_app_account_dict = {
    "address": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
    "amount": 1000000,
    "amount-without-pending-rewards": None,
    "apps-local-state": None,
    "apps-total-schema": None,
    "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": False}],
    "created-apps": [],
    "created-assets": [
        {
            "index": 1,
            "params": {
                "clawback": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                "creator": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                "decimals": 3,
                "default-frozen": False,
                "freeze": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                "manager": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                "metadata-hash": "",
                "name": "K Coin",
                "reserve": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                "total": 1000000,
                "unit-name": "microK",
                "url": "",
            },
        }
    ],
    "participation": None,
    "pending-rewards": None,
    "reward-base": None,
    "rewards": None,
    "round": None,
    "status": None,
    "sig-type": None,
    "auth-addr": None,
}


if __name__ == "__main__":
    sys.setrecursionlimit(15000000)
    logging.basicConfig(level=logging.INFO)

    prover = AutoProver(
        pyteal_module_name='kcoin_vault_pyteal',
        app_id=1,
        sdk_app_creator_account_dict=sdk_app_creator_account_dict,
        sdk_app_account_dict=sdk_app_account_dict,
    )
    prover.prove('mint')
    prover.prove('burn')
