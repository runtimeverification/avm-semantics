from typing import Optional

from pyk.kast import KApply
from pyk.prelude import intToken, stringToken


def int_token_cell(name: str, value: Optional[int]) -> KApply:
    """Construct a cell containing an Int token. Default to 0 if None is supplied."""

    if isinstance(value, int):
        token = intToken(value)
    elif value is None:
        token = intToken(0)
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'{name}', [token])


def string_token_cell(name: str, value: Optional[str]) -> KApply:
    """Construct a cell containing an String token. Default to the empty string if None is supplied."""

    if isinstance(value, str):
        token = stringToken(value)
    elif value is None:
        token = stringToken('')
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'{name}', [token])
