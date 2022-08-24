from pyk.kast import KAst, KInner, KSort, Subst, KApply, KLabel, KToken
from pyk.kastManip import inlineCellMaps, collectFreeVars
from pyk.cli_utils import run_process
from pyk.prelude import intToken, stringToken, build_assoc, buildCons, Sorts

from kavm_algod.constants import MIN_BALANCE


class KAVMAccount:
    """
    Convenience class bundling an Algorand address with its associated KAVM entities
    """

    def __init__(self, address: str, balance: int = 0) -> None:
        """
        Create a KAVM account cell.
        """
        from kavm_algod.pyk_utils import maybeTValue

        self._account_cell = KApply(
            '<account>',
            [
                KApply('<address>', [maybeTValue(address)]),
                KApply('<balance>', [intToken(balance)]),
                KApply('<minBalance>', [intToken(MIN_BALANCE)]),
                KApply('<round>', [intToken(0)]),
                KApply('<preRewards>', [intToken(0)]),
                KApply('<rewards>', [intToken(0)]),
                KApply('<status>', [intToken(0)]),
                KApply('<key>', [maybeTValue(address)]),
                KApply('<appsCreated>', [KApply('.AppCellMap')]),
                KApply('<appsOptedIn>', [KApply('.OptInAppCellMap')]),
                KApply('<assetsCreated>', [KApply('.AssetCellMap')]),
                KApply('<assetsOptedIn>', [KApply('.OptInAssetCellMap')]),
            ],
        )

    @property
    def address(self) -> str:
        return self._address

    @property
    def account_cell(self) -> KInner:
        return self._account_cell
