import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from pyk.kast import KApply, KAst, KInner, KSort, KToken, Subst
from pyk.kastManip import flatten_label, split_config_from
from pyk.prelude import intToken

from kavm.constants import MIN_BALANCE
from kavm.pyk_utils import AppCellMap, split_direct_subcells_from


class KAVMAccount:
    """
    Convenience class bundling an Algorand address with its associated KAVM entities
    """

    def __init__(
        self,
        address: str,
        balance: int = 0,
        min_balance: int = MIN_BALANCE,
        round: int = 0,
        pre_rewards: int = 0,
        rewards: int = 0,
        status: int = 0,
        key: str = '',
        apps_created: Optional[AppCellMap] = None,
        apps_opted_in: Optional[List[int]] = None,
        assets_created: Optional[List[int]] = None,
        assets_opted_in: Optional[List[int]] = None,
    ) -> None:
        """
        Create a KAVM account cell.
        """
        self._address = address
        self._balance = balance
        self._min_balance = min_balance
        self._round = round
        self._pre_rewards = pre_rewards
        self._rewards = rewards
        self._status = status
        self._key = address if key == '' else key
        self._apps_created = apps_created if apps_created else AppCellMap()
        self._apps_opted_in = apps_opted_in if apps_opted_in else []
        self._assets_created = assets_created if assets_created else []
        self._assets_opted_in = assets_opted_in if assets_opted_in else []

    # TODO: implement better eq
    def __eq__(self, other: Any) -> bool:
        return self._address == other._address

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
    def apps_created(self) -> AppCellMap:
        return self._apps_created

    @property
    def account_cell(self) -> KInner:
        return KApply(
            '<account>',
            [
                KApply('<address>', [KToken(self._address, KSort('TAddressLiteral'))]),
                KApply('<balance>', [intToken(self._balance)]),
                KApply('<minBalance>', [intToken(self._min_balance)]),
                KApply('<round>', [intToken(self._round)]),
                KApply('<preRewards>', [intToken(self._pre_rewards)]),
                KApply('<rewards>', [intToken(self._rewards)]),
                KApply('<status>', [intToken(self._status)]),
                KApply('<key>', [KToken(self._key, KSort('TAddressLiteral'))]),
                # TODO: handle apps and assets
                KApply(
                    '<appsCreated>',
                    self._apps_created.k_cell,
                ),
                KApply('<appsOptedIn>', [KApply('.OptInAppCellMap')]),
                KApply('<assetsCreated>', [KApply('.AssetCellMap')]),
                KApply('<assetsOptedIn>', [KApply('.OptInAssetCellMap')]),
            ],
        )

    @staticmethod
    def to_account_cell(account: 'KAVMAccount') -> KInner:
        return account.account_cell

    @staticmethod
    def from_account_cell(term: KInner) -> 'KAVMAccount':
        """
        Parse a KAVMAccount instance from a Kast term
        """
        # (_, subst) = split_config_from(term)
        (_, subst) = split_direct_subcells_from(term)
        return KAVMAccount(
            address=subst['ADDRESS_CELL'].token,
            balance=int(subst['BALANCE_CELL'].token),
            min_balance=int(subst['MINBALANCE_CELL'].token),
            round=int(subst['ROUND_CELL'].token),
            pre_rewards=int(subst['PREREWARDS_CELL'].token),
            rewards=int(subst['REWARDS_CELL'].token),
            status=int(subst['STATUS_CELL'].token),
            key=subst['KEY_CELL'].token,
            apps_created=AppCellMap(subst['APPSCREATED_CELL']),
            apps_opted_in=[],
            assets_created=[],
            assets_opted_in=[],
        )

    def to_kore_term(self, kavm: Any) -> str:
        '''
        Encode account as a KORE term

        A KAVM instance must be passed to use kavm.kast
        '''
        with tempfile.NamedTemporaryFile('w+t', delete=True) as tmp_kast_json_file:
            term = self.account_cell
            term_json = json.dumps({'format': 'KAST', 'version': 2, 'term': term.to_dict()})
            tmp_kast_json_file.write(term_json)
            tmp_kast_json_file.seek(0)
            kore_term = kavm.kast(
                input_file=Path(tmp_kast_json_file.name),
                module='ALGO-BLOCKCHAIN',
                sort=KSort('AccountCell'),
                input='json',
                output='kore',
            ).stdout
            return kore_term

    @staticmethod
    def from_kore_term(kore_term: str, kavm: Any) -> 'KAVMAccount':
        '''
        Decode an account from a KORE term

        A KAVM instance must be passed to use kavm.kast
        '''
        with tempfile.NamedTemporaryFile('w+t', delete=True) as tmp_kore_file:
            tmp_kore_file.write(kore_term)
            tmp_kore_file.seek(0)
            kast_term_json = kavm.kast(
                input_file=Path(tmp_kore_file.name),
                module='ALGO-BLOCKCHAIN',
                sort=KSort('AccountCell'),
                input='kore',
                output='json',
            ).stdout
            kast_term = KAst.from_dict(json.loads(kast_term_json)['term'])
            return KAVMAccount.from_account_cell(cast(KInner, kast_term))

    def dictify(self) -> Dict[str, Union[str, int]]:
        """
        Return a dictified representation of the account cell to pass to py-algorand-sdk
        See https://github.com/algorand/go-algorand/blob/87867c9381260dc4efb5a42abaeb9e038b1c10af/daemon/algod/api/algod.oas2.json#L1785 for format
        """
        return {
            'round': self._round,
            'address': self._address,
            'amount': self._balance,
            'pending-rewards': self._pre_rewards,
            # TODO: figure out what's amount-without-pending-rewards
            'amount-without-pending-rewards': 0,
            'rewards': self._rewards,
            'status': self._status,
            'min-balance': self._min_balance,
            'total-apps-opted-in': len(self._apps_opted_in) if self._apps_opted_in else 0,
            'total-assets-opted-in': len(self._assets_opted_in) if self._assets_opted_in else 0,
            'total-created-apps': len(self._apps_created) if self._apps_created else 0,
            'total-created-assets': len(self._assets_created) if self._assets_created else 0,
        }

    def __repr__(self) -> str:
        return repr(self.dictify())


def get_account(address: str, accounts_map_cell: KInner) -> KInner:
    (symbolic_account_cell_term, _) = split_config_from(KAVMAccount(address).account_cell)
    account_pattern = Subst({'ADDRESS_CELL': KToken(address, KSort('TAddressLiteral'))}).apply(
        symbolic_account_cell_term
    )
    account_cells = flatten_label('_AccountCellMap_', accounts_map_cell)
    for term in account_cells:
        if account_pattern.match(term) is not None:
            return term

    raise KeyError(f'address {address} not found')
