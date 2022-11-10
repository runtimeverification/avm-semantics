from typing import Iterable, cast

from algosdk.v2client import models
from pyk.kast import KApply, KInner, KLabel, KSort, KToken, build_cons
from pyk.kastManip import flatten_label, split_config_from
from pyk.prelude.kint import intToken

from kavm.adaptors.algod_application import KAVMApplication
from kavm.constants import MIN_BALANCE


class KAVMAccount(models.Account):
    """
    Convenience class bundling an Algorand address with its associated KAVM entities
    """

    inverted_attribute_map = {v: k for k, v in models.Account.attribute_map.items()}

    def validate(self) -> bool:
        """Validate min_balance and perhaps some other fields"""
        raise NotImplementedError()

    @staticmethod
    def from_k_cell(term: KInner) -> 'KAVMAccount':
        """
        Parse a KAVMAccount instance from a Kast term
        """
        (_, subst) = split_config_from(term)
        parsed_address = cast(KToken, subst['ADDRESS_CELL']).token
        parsed_amount = int(cast(KToken, subst['BALANCE_CELL']).token)
        parsed_auth_addr = cast(KToken, subst['KEY_CELL']).token
        created_apps_terms = []
        if cast(KApply, subst['APPSCREATED_CELL']).label.name == '_AppCellMap_':
            created_apps_terms = flatten_label('_AppCellMap_', subst['APPSCREATED_CELL'])
        parsed_created_apps = []
        for app_term in created_apps_terms:
            if cast(KApply, app_term).label.name == '<app>':
                parsed_created_apps.append(KAVMApplication.from_k_cell(term=app_term, creator=parsed_address).params)
        return KAVMAccount(
            address=parsed_address,
            amount=parsed_amount,
            amount_without_pending_rewards=None,
            apps_local_state=None,
            apps_total_schema=None,
            assets=None,
            created_apps=parsed_created_apps if parsed_created_apps else None,
            participation=None,
            pending_rewards=None,
            reward_base=None,
            rewards=None,
            round=None,
            status=None,
            sig_type=None,
            auth_addr=parsed_auth_addr,
        )


def account_k_term(address: str, amount: int, created_apps_terms: Iterable[KInner]) -> KInner:
    return KApply(
        label=KLabel(name='<account>', params=()),
        args=(
            KApply(
                label=KLabel(name='<address>', params=()),
                args=[KToken(token=address, sort=KSort(name='String'))],
            ),
            KApply(label=KLabel(name='<balance>', params=()), args=[intToken(amount)]),
            KApply(label=KLabel(name='<minBalance>', params=()), args=[intToken(MIN_BALANCE)]),
            KApply(label=KLabel(name='<round>', params=()), args=[intToken(0)]),
            KApply(label=KLabel(name='<preRewards>', params=()), args=[intToken(0)]),
            KApply(label=KLabel(name='<rewards>', params=()), args=[intToken(0)]),
            KApply(label=KLabel(name='<status>', params=()), args=[intToken(0)]),
            KApply(
                label=KLabel(name='<key>', params=()),
                args=[KToken(token=address, sort=KSort(name='String'))],
            ),
            KApply(
                label=KLabel(name='<appsCreated>', params=()),
                args=[
                    build_cons(
                        unit=KApply('.AppCellMap'),
                        label='_AppCellMap_',
                        terms=created_apps_terms,
                    )
                ],
            ),
            KApply(
                label=KLabel(name='<appsOptedIn>', params=()),
                args=(KApply(label=KLabel(name='.OptInAppCellMap', params=()), args=()),),
            ),
            KApply(
                label=KLabel(name='<assetsCreated>', params=()),
                args=(KApply(label=KLabel(name='.AssetCellMap', params=()), args=()),),
            ),
            KApply(
                label=KLabel(name='<assetsOptedIn>', params=()),
                args=(KApply(label=KLabel(name='.OptInAssetCellMap', params=()), args=()),),
            ),
        ),
    )
