import typing
from typing import Any
import json

import pytest
from algosdk.v2client import models

from kavm.adaptors.algod_account import KAVMAccount, account_k_term
from kavm.adaptors.algod_application import KAVMApplicationParams, application_k_term


@typing.no_type_check
@pytest.mark.parametrize(
    'test_case_description,input,expected',
    [
        (
            "Blank account",
            account_k_term(address="test", amount=42, created_apps_terms=[]),
            KAVMAccount(address="test", amount=42, auth_addr="test"),
        ),
        (
            "Account with one app created",
            account_k_term(address="test", amount=42, created_apps_terms=[application_k_term(app_id=1)]),
            KAVMAccount(
                address="test",
                amount=42,
                auth_addr="test",
                created_apps=[
                    KAVMApplicationParams(
                        creator="test",
                        global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                        local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                    )
                ],
            ),
        ),
    ],
)
def test_account_from_k(test_case_description: str, input: Any, expected: Any) -> None:
    assert KAVMAccount.from_k_cell(input) == expected
