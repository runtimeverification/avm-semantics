import logging
import sys
from pathlib import Path
import json
import pytest

from algosdk.abi.method import Method
from algosdk.abi.contract import get_method_by_name
from algosdk.future.transaction import StateSchema
from algosdk.v2client import models
from kcoin_vault_pyteal import router
from pyk.kast.inner import KApply, KVariable, KSort, KToken
from pyk.prelude.kint import intToken
from pyk.prelude.bytes import bytesToken

from kavm.kavm import KAVM
from kavm.prover import AutoProver
from kavm.kast.factory import KAVMTermFactory


def write_to_file(program: str, path: Path):
    with open(path, "w") as f:
        f.write(program)


if __name__ == "__main__":
    sys.setrecursionlimit(15000000)
    logging.basicConfig(level=logging.INFO)

    kavm = KAVM(definition_dir=Path('./tests/specs/verification-kompiled'))

    approval_pgm, clear_pgm, contract = router.compile_program(version=8)
    write_to_file(approval_pgm, Path('approval.teal'))
    write_to_file(clear_pgm, Path('clear.teal'))

    # read initial state from files
    with open('app-creator-account.json', 'r') as file:
        sdk_app_creator_account_dict = json.load(file)
    with open('app-account.json', 'r') as file:
        sdk_app_account_dict = json.load(file)

    prover = AutoProver(
        definition_dir=Path('./tests/specs/verification-kompiled'),
        approval_pgm=Path('approval.teal'),
        clear_pgm=Path('clear.teal'),
        contract=contract,
        app_id=1,
        sdk_app_creator_account_dict=sdk_app_creator_account_dict,
        sdk_app_account_dict=sdk_app_account_dict,
    )
    prover.prove('mint')
    prover.prove('burn')

# Need to kompile verification like this:
# kompile --output-definition tests/specs/verification-kompiled tests/specs/verification.k --verbose --emit-json --backend haskell --hook-namespaces KRYPTO -I .build/usr/lib/kavm/include/kframework -I /home/geo2a/Workspace/RV/avm-semantics/.build/usr/lib/kavm/blockchain-k-plugin/include/kframework


# sdk_app_creator_account_dict = {
#     "address": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
#     "amount": 999999000000,
#     "amount-without-pending-rewards": None,
#     "apps-local-state": None,
#     "apps-total-schema": None,
#     "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": 0}],
#     "created-apps": [
#         {
#             "id": 1,
#             "params": {
#                 "creator": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
#                 "approval-program": "approve.teal",
#                 "clear-state-program": "clear.teal",
#                 "local-state-schema": {"nbs": 0, "nui": 0},
#                 "global-state-schema": {"nbs": 0, "nui": 2},
#                 "global-state": [
#                     {"key": "YXNzZXRfaWQ=", "value": {"bytes": "", "type": 2, "uint": 1}},
#                     {"key": "ZXhjaGFuZ2VfcmF0ZQ==", "value": {"bytes": "", "type": 2, "uint": 2}},
#                 ],
#             },
#         }
#     ],
#     "created-assets": [],
#     "participation": None,
#     "pending-rewards": None,
#     "reward-base": None,
#     "rewards": None,
#     "round": None,
#     "status": None,
#     "sig-type": None,
#     "auth-addr": None,
# }

# sdk_app_account_dict = {
#     "address": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#     "amount": 1000000,
#     "amount-without-pending-rewards": None,
#     "apps-local-state": None,
#     "apps-total-schema": None,
#     "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": 0}],
#     "created-apps": [],
#     "created-assets": [
#         {
#             "index": 1,
#             "params": {
#                 "clawback": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#                 "creator": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#                 "decimals": 3,
#                 "default-frozen": 0,
#                 "freeze": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#                 "manager": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#                 "metadata-hash": "",
#                 "name": "K Coin",
#                 "reserve": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
#                 "total": 1000000,
#                 "unit-name": "microK",
#                 "url": "",
#             },
#         }
#     ],
#     "participation": None,
#     "pending-rewards": None,
#     "reward-base": None,
#     "rewards": None,
#     "round": None,
#     "status": None,
#     "sig-type": None,
#     "auth-addr": None,
# }
