from typing import Any

import pytest

from kavm.adaptors.account import KAVMAccount
from kavm.constants import MIN_BALANCE
from kavm.kavm import KAVM
from kavm.pyk_utils import AppCellMap
from tests.unit.test_application_encoding import application_blank


def account_blank(kavm: KAVM) -> KAVMAccount:
    return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


def account_one_app_created(kavm: KAVM) -> KAVMAccount:
    return KAVMAccount(
        address="test",
        balance=42,
        min_balance=MIN_BALANCE,
        apps_created=AppCellMap.from_list([application_blank(kavm)]),
    )


def account_two_apps_created() -> KAVMAccount:
    return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


def account_one_app_optedin() -> KAVMAccount:
    return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


def account_two_apps_optedin() -> KAVMAccount:
    return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


def account_complex() -> KAVMAccount:
    return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


@pytest.fixture(params=[account_blank, account_one_app_created])
def account(kavm: KAVM, request: Any) -> KAVMAccount:
    return request.param(kavm)


def test_init(account: KAVMAccount) -> None:
    assert account


def test_account_k_encoding(account: KAVMAccount) -> None:
    rountrip_account = KAVMAccount.from_account_cell(account.account_cell)
    # travers attributes of KAVMAccount and assert that the ones starting with _ are the same,
    # ignoring the __ ones
    for attr in [a for a in dir(account) if a.startswith('_') and not a.startswith('__')]:
        assert getattr(account, attr) == getattr(rountrip_account, attr)


def test_account_to_from_kore(kavm: KAVM, account: KAVMAccount) -> None:
    kore_term = account.to_kore_term(kavm)
    rountrip_account = KAVMAccount.from_kore_term(kore_term, kavm)
    assert rountrip_account == account
