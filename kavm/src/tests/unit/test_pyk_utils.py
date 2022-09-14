import pytest

from pyk.kast import KApply, KToken, KSort
from pyk.prelude import intToken, stringToken

from kavm.pyk_utils import maybe_tvalue, split_direct_subcells_from


@pytest.mark.parametrize(
    'input,expected',
    [
        (None, KApply('NoTValue')),
        (42, intToken(42)),
        ("42", stringToken("42")),
        (b'42', stringToken('NDI=')),
    ],
)
def test_maybe_tvalue(input, expected):
    assert maybe_tvalue(input) == expected


@pytest.mark.parametrize(
    'input,expected',
    [
        (
            KApply(
                '<account>',
                [
                    KApply('<address>', [KToken('dummy', KSort('TAddressLiteral'))]),
                ],
            ),
            set(['ADDRESS_CELL']),
        ),
        (
            KApply(
                '<account>',
                [
                    KApply('<address>', [KToken('dummy', KSort('TAddressLiteral'))]),
                    KApply('<appsCreated>', [KApply('<app>', [KApply('<appID>', [intToken(1)])])]),
                ],
            ),
            set(['ADDRESS_CELL', 'APPSCREATED_CELL']),
        ),
        (
            KApply(
                '<account>',
                [
                    KApply('<address>', [KToken('dummy', KSort('TAddressLiteral'))]),
                    KApply(
                        '<appsCreated>',
                        [
                            KApply('<app>', [KApply('<appID>', [intToken(1)])]),
                            KApply('<app>', [KApply('<appID>', [intToken(2)])]),
                        ],
                    ),
                ],
            ),
            set(['ADDRESS_CELL', 'APPSCREATED_CELL']),
        ),
    ],
)
def test_split_direct_subcells_from(input, expected):
    (_, subst) = split_direct_subcells_from(input)
    assert set(subst.keys()) == expected
