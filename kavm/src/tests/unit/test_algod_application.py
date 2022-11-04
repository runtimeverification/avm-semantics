import typing
from typing import Any

import pytest
from algosdk.v2client import models

import tests.unit.test_teal_key_value as teal_store_test_data
from kavm.adaptors.algod_application import KAVMApplication, KAVMApplicationParams, application_k_term


@typing.no_type_check
@pytest.mark.parametrize(
    'input,expected',
    [
        (
            application_k_term(app_id=42),
            KAVMApplication(
                id=42,
                params=KAVMApplicationParams(
                    global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                    local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                ),
            ),
        ),
        (
            application_k_term(
                app_id=42,
                global_state=None,
                global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
            ),
            KAVMApplication(
                id=42,
                params=KAVMApplicationParams(
                    global_state=None,
                    global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                    local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                ),
            ),
        ),
        (
            application_k_term(
                app_id=42,
                global_state=teal_store_test_data.teal_store_bytes_bytes,
                global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=2),
                local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
            ),
            KAVMApplication(
                id=42,
                params=KAVMApplicationParams(
                    global_state=teal_store_test_data.teal_store_bytes_bytes,
                    global_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=2),
                    local_state_schema=models.ApplicationStateSchema(num_uint=0, num_byte_slice=0),
                ),
            ),
        ),
    ],
)
def test_application_from_k(input: Any, expected: Any) -> None:
    assert KAVMApplication.from_k_cell(input, expected.params.creator) == expected
