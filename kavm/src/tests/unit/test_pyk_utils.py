import pytest

from pyk.kast import KApply
from pyk.prelude import intToken, stringToken

from kavm.pyk_utils import maybe_tvalue


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
