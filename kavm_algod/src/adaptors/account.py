from typing import Dict, List, Optional, Union

from kavm_algod.constants import MIN_BALANCE
from kavm_algod.pyk_utils import maybeTValue
from pyk.kast import KApply, KInner, Subst
from pyk.kastManip import flatten_label, splitConfigFrom
from pyk.prelude import intToken, stringToken


class KAVMAccount:
    """
    Convenience class bundling an Algorand address with its associated KAVM entities
    """

    def __init__(
        self,
        address: str,
        balance: int = 0,
        minBalance: int = MIN_BALANCE,
        round: int = 0,
        preRewards: int = 0,
        rewards: int = 0,
        status: int = 0,
        key: str = '""',
        appsCreated: List[int] = [],
        appsOptedIn: List[int] = [],
        assetsCreated: List[int] = [],
        assetsOptedIn: List[int] = [],
    ) -> None:
        """
        Create a KAVM account cell.
        """
        self._address = address
        self._balance = balance
        self._minBalance = minBalance
        self._round = round
        self._preRewards = preRewards
        self._rewards = rewards
        self._status = status
        self._key = address if key == '""' else key
        self._appsCreated = appsCreated
        self._appsOptedIn = appsOptedIn
        self._assetsCreated = assetsCreated
        self._assetsOptedIn = assetsOptedIn

    @property
    def address(self) -> str:
        return self._address

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, microalgos: int) -> None:
        self._balance = microalgos

    @property
    def account_cell(self) -> KInner:
        return KApply(
            '<account>',
            [
                KApply('<address>', [maybeTValue(self._address)]),
                KApply('<balance>', [intToken(self._balance)]),
                KApply('<minBalance>', [intToken(self._minBalance)]),
                KApply('<round>', [intToken(self._round)]),
                KApply('<preRewards>', [intToken(self._preRewards)]),
                KApply('<rewards>', [intToken(self._rewards)]),
                KApply('<status>', [intToken(self._status)]),
                KApply('<key>', [maybeTValue(self._key)]),
                # TODO: handle apps and assets
                KApply('<appsCreated>', [KApply('.AppCellMap')]),
                KApply('<appsOptedIn>', [KApply('.OptInAppCellMap')]),
                KApply('<assetsCreated>', [KApply('.AssetCellMap')]),
                KApply('<assetsOptedIn>', [KApply('.OptInAssetCellMap')]),
            ],
        )

    @staticmethod
    def from_account_cell(term: KInner) -> 'KAVMAccount':
        """
        Parse a KAVMAccount instance from a Kast term
        """

        (_, subst) = splitConfigFrom(term)
        return KAVMAccount(
            address=subst['ADDRESS_CELL'].token,
            balance=int(subst['BALANCE_CELL'].token),
            minBalance=int(subst['MINBALANCE_CELL'].token),
            round=int(subst['ROUND_CELL'].token),
            preRewards=int(subst['PREREWARDS_CELL'].token),
            rewards=int(subst['REWARDS_CELL'].token),
            status=int(subst['STATUS_CELL'].token),
            key=subst['KEY_CELL'].token,
        )

    def dictify(self) -> Dict[str, Union[str, int]]:
        """
        Return a dictified representation of the account cell to pass to py-algorand-sdk
        See https://github.com/algorand/go-algorand/blob/87867c9381260dc4efb5a42abaeb9e038b1c10af/daemon/algod/api/algod.oas2.json#L1785 for format
        """
        return {
            'round': self._round,
            'address': self._address,
            'amount': self._balance,
            'pending-rewards': self._preRewards,
            # TODO: figure out what's amount-without-pending-rewards
            'amount-without-pending-rewards': 0,
            'rewards': self._rewards,
            'status': self._status,
            'min-balance': self._minBalance,
            'total-apps-opted-in': len(self._appsOptedIn),
            'total-assets-opted-in': len(self._assetsOptedIn),
            'total-created-apps': len(self._appsCreated),
            'total-created-assets': len(self._assetsCreated),
        }


def get_account(address: str, accountsMapCell: KInner) -> Optional[KInner]:
    (symbolic_account_cell_term, _) = splitConfigFrom(KAVMAccount(address).account_cell)
    account_pattern = Subst({'ADDRESS_CELL': stringToken(address)}).apply(
        symbolic_account_cell_term
    )
    account_cells = flatten_label('_AccountCellMap_', accountsMapCell)
    for term in account_cells:
        if account_pattern.match(term) is not None:
            return term
    return None
