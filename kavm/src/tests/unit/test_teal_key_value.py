from typing import Any

import pytest
from algosdk.v2client import models
from pyk.kast.inner import KApply, KToken

from kavm.adaptors.teal_key_value import teal_key_value_store_from_k_cell

k_map_bytes_bytes = KApply(
    '_Map_',
    [
        KApply(
            '_|->_',
            args=(
                KToken('b"key1"', 'Bytes'),
                KToken('b"value1"', 'Bytes'),
            ),
        ),
        KApply(
            '_|->_',
            args=(
                KToken('b"key2"', 'Bytes'),
                KToken('b"value2"', 'Bytes'),
            ),
        ),
    ],
)

teal_store_bytes_bytes = [
    models.TealKeyValue(key='key1', value={'bytes': 'value1', 'type': 1, 'uint': None}),
    models.TealKeyValue(key='key2', value={'bytes': 'value2', 'type': 1, 'uint': None}),
]

teal_store_bytes_ints = [
    models.TealKeyValue(key='key1', value={'bytes': None, 'type': 2, 'uint': 1}),
    models.TealKeyValue(key='key2', value={'bytes': None, 'type': 2, 'uint': 2}),
]

k_map_bytes_int = KApply(
    '_Map_',
    [
        KApply(
            '_|->_',
            args=(
                KToken('b"key1"', 'Bytes'),
                KToken('1', 'Int'),
            ),
        ),
        KApply(
            '_|->_',
            args=(
                KToken('b"key2"', 'Bytes'),
                KToken('2', 'Int'),
            ),
        ),
    ],
)


@pytest.mark.parametrize(
    'input,expected',
    [
        (KApply('.Map'), []),
        (k_map_bytes_bytes, teal_store_bytes_bytes),
        (k_map_bytes_int, teal_store_bytes_ints),
    ],
)
def test_teal_key_value_store_from_k(input: Any, expected: Any) -> None:
    parsed = teal_key_value_store_from_k_cell(input)
    assert parsed == expected
    # for i in range(len(parsed)):
    #     assert parsed[i]['key'] == expected[i]['key']
    #     assert parsed[i]['value'].dictify() == expected[i]['value']
