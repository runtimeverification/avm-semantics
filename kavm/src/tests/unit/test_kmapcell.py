import pytest

from pyk.kast import KApply, KAst, KLabel, KToken, KSort
from pyk.prelude import intToken, stringToken

from kavm.pyk_utils import AccountCellMap
from kavm.adaptors.account import KAVMAccount


@pytest.fixture
def empty_accounts_term() -> KAst:
    return KApply(
        label=KLabel(name='.AccountCellMap', params=()),
    )


@pytest.fixture
def one_accounts_term() -> KAst:
    return KApply(
        label=KLabel(name='_AccountCellMap_', params=()),
        args=(
            KApply(
                label=KLabel(name='<account>', params=()),
                args=(
                    KApply(
                        label=KLabel(name='<address>', params=()),
                        args=(KToken(token='dummy', sort=KSort(name='TAddressLiteral')),),
                    ),
                    KApply(
                        label=KLabel(name='<balance>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(
                        label=KLabel(name='<minBalance>', params=()),
                        args=(KToken(token='100000', sort=KSort(name='Int')),),
                    ),
                    KApply(label=KLabel(name='<round>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<preRewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(
                        label=KLabel(name='<rewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(label=KLabel(name='<status>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<key>', params=()),
                        args=(KToken(token='dummy', sort=KSort(name='TAddressLiteral')),),
                    ),
                    KApply(
                        label=KLabel(name='<appsCreated>', params=()),
                        args=(KApply(label=KLabel(name='.AppCellMap', params=()), args=()),),
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
            ),
        ),
    )


@pytest.fixture
def two_accounts_term() -> KAst:
    return KApply(
        label=KLabel(name='_AccountCellMap_', params=()),
        args=(
            KApply(
                label=KLabel(name='<account>', params=()),
                args=(
                    KApply(
                        label=KLabel(name='<address>', params=()),
                        args=(KToken(token='dummy', sort=KSort(name='TAddressLiteral')),),
                    ),
                    KApply(
                        label=KLabel(name='<balance>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(
                        label=KLabel(name='<minBalance>', params=()),
                        args=(KToken(token='100000', sort=KSort(name='Int')),),
                    ),
                    KApply(label=KLabel(name='<round>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<preRewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(
                        label=KLabel(name='<rewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(label=KLabel(name='<status>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<key>', params=()),
                        args=(KToken(token='dummy', sort=KSort(name='TAddressLiteral')),),
                    ),
                    KApply(
                        label=KLabel(name='<appsCreated>', params=()),
                        args=(KApply(label=KLabel(name='.AppCellMap', params=()), args=()),),
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
            ),
            KApply(
                label=KLabel(name='<account>', params=()),
                args=(
                    KApply(
                        label=KLabel(name='<address>', params=()),
                        args=(
                            KToken(
                                token='E2577Y2GJFPUA2YBYRWZQ75DYWP7FBAAHLXVJOGVBT66JRQQKDFVS6E4AI',
                                sort=KSort(name='TAddressLiteral'),
                            ),
                        ),
                    ),
                    KApply(
                        label=KLabel(name='<balance>', params=()),
                        args=(KToken(token='1000000000', sort=KSort(name='Int')),),
                    ),
                    KApply(
                        label=KLabel(name='<minBalance>', params=()),
                        args=(KToken(token='100000', sort=KSort(name='Int')),),
                    ),
                    KApply(label=KLabel(name='<round>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<preRewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(
                        label=KLabel(name='<rewards>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)
                    ),
                    KApply(label=KLabel(name='<status>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
                    KApply(
                        label=KLabel(name='<key>', params=()),
                        args=(
                            KToken(
                                token='E2577Y2GJFPUA2YBYRWZQ75DYWP7FBAAHLXVJOGVBT66JRQQKDFVS6E4AI',
                                sort=KSort(name='TAddressLiteral'),
                            ),
                        ),
                    ),
                    KApply(
                        label=KLabel(name='<appsCreated>', params=()),
                        args=(KApply(label=KLabel(name='.AppCellMap', params=()), args=()),),
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
            ),
        ),
    )


def test_kmapcell_empty(empty_accounts_term):
    thing = AccountCellMap(
        term=empty_accounts_term,
    )
    assert len(thing) == 0


def test_kmapcell_one(one_accounts_term):
    thing = AccountCellMap(
        term=one_accounts_term,
    )
    assert len(thing) == 1


def test_kmapcell_two(two_accounts_term):
    thing = AccountCellMap(
        term=two_accounts_term,
    )
    assert len(thing) == 2
