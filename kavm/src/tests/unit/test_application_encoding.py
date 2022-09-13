from typing import Any

import pytest

from kavm.constants import MIN_BALANCE
from kavm.adaptors.application import KAVMApplication
from kavm.kavm import KAVM


def application_blank(kavm: KAVM) -> KAVMApplication:
    return KAVMApplication(appID=42, approvalPgmSrc=kavm.parse_teal('int 0'), clearStatePgmSrc=kavm.parse_teal('int 1'))


# def account_one_app_created() -> KAVMAccount:
#     return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


# def account_two_apps_created() -> KAVMAccount:
#     return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


# def account_one_app_optedin() -> KAVMAccount:
#     return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


# def account_two_apps_optedin() -> KAVMAccount:
#     return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


# def account_complex() -> KAVMAccount:
#     return KAVMAccount(address="test", balance=42, min_balance=MIN_BALANCE)


@pytest.fixture(params=[application_blank])
def application(kavm: KAVM, request) -> KAVMApplication:
    return request.param(kavm)


def test_application_k_encoding(application: KAVMApplication):
    rountrip_application = KAVMApplication.from_app_cell(application.app_cell)
    # travers attributes of KAVMAccount and assert that the ones starting with _ are the same,
    # ignoring the __ ones
    for attr in [a for a in dir(application) if a.startswith('_') and not a.startswith('__')]:
        assert getattr(application, attr) == getattr(rountrip_application, attr)
