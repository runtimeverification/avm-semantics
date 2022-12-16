import logging
import sys
from pathlib import Path

from algosdk.abi.contract import get_method_by_name
from algosdk.future.transaction import StateSchema
from algosdk.v2client import models
from kcoin_vault_pyteal import router
from pyk.kast.inner import KApply, KVariable, KSort, KToken
from pyk.prelude.kint import intToken
from pyk.prelude.bytes import bytesToken

from kavm.kavm import KAVM
from kavm.prover import AutoProver, MethodWithSpec
from kavm.kast.factory import KAVMTermFactory


def write_to_file(program: str, path: Path):
    with open(path, "w") as f:
        f.write(program)


if __name__ == "__main__":
    sys.setrecursionlimit(15000000)
    logging.basicConfig(level=logging.INFO)

    approval_pgm, clear_pgm, contract = router.compile_program(version=8)
    write_to_file(approval_pgm, Path('approval.teal'))
    write_to_file(clear_pgm, Path('clear.teal'))

    kavm = KAVM(definition_dir=Path('./tests/specs/verification-kompiled'))

    sdk_app_creator_account_dict = {
        "address": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
        "amount": 999999000000,
        "amount-without-pending-rewards": None,
        "apps-local-state": None,
        "apps-total-schema": None,
        "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": 0}],
        "created-apps": [
            {
                "id": 1,
                "params": {
                    "creator": "DJPACABYNRWAEXBYKT4WMGJO5CL7EYRENXCUSG2IOJNO44A4PWFAGLOLIA",
                    "approval-program": "approve.teal",
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
        "assets": [{"amount": 500000, "asset-id": 1, "is-frozen": 0}],
        "created-apps": [],
        "created-assets": [
            {
                "index": 1,
                "params": {
                    "clawback": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                    "creator": "WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM",
                    "decimals": 3,
                    "default-frozen": 0,
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

    contract.methods[1] = MethodWithSpec(
        preconditions=[
            KApply('_>Int_', [KVariable('PAYMENT'), intToken(1000)]),
            KApply('_<=Int_', [KVariable('PAYMENT'), intToken(100000)]),
            # KApply('_==Int_', [KVariable('PAYMENT'), intToken(10000)]),
        ],
        postconditions=[
            KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(PAYMENT /Int 2, BE, Unsigned), 8, 0)
                "_==K_",
                [
                    KVariable('?FINAL_LOGDATA_CELL'),
                    KApply(
                        '_+Bytes_',
                        [
                            bytesToken("\\x15\\x1f|u"),
                            KApply(
                                'padLeftBytes',
                                [
                                    KApply(
                                        'Int2Bytes',
                                        [
                                            KApply('_/Int_', [KVariable('PAYMENT'), intToken(2)]),
                                            KToken('BE', KSort('Endianness')),
                                            KToken('Unsigned', KSort('Signedness')),
                                        ],
                                    ),
                                    intToken(8),
                                    intToken(0),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
        sdk_method=get_method_by_name(name='mint', methods=contract.methods),
    )

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

# Need to kompile verification like this:
# kompile --output-definition tests/specs/verification-kompiled tests/specs/verification.k --verbose --emit-json --backend haskell --hook-namespaces KRYPTO -I .build/usr/lib/kavm/include/kframework -I /home/geo2a/Workspace/RV/avm-semantics/.build/usr/lib/kavm/blockchain-k-plugin/include/kframework


# #Not ( { b"\x15\x1f|u" +Bytes padLeftBytes ( Int2Bytes ( log2Int ( PAYMENT:Int /Int 2 ) +Int 8 /Int 8 , PAYMENT:Int /Int 2 , BE ) , 8 , 0 ) #Equals b"\x15\x1f|u" +Bytes padLeftBytes ( Int2Bytes ( log2Int ( PAYMENT:Int ) +Int 8 /Int 8 , PAYMENT:Int , BE ) , 8 , 0 ) } )
