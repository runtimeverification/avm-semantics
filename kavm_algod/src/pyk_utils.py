from typing import Optional, Union, List

from pyk.kast import KApply, KLabel, KTerminal, KSort, KToken
from pyk.prelude import intToken, stringToken

from kavm_algod.kavm import KAVM


def maybeTValue(kavm: KAVM, value: Optional[Union[str, int, bytes]]) -> KApply:
    # print(kavm.definition.production_for_klabel(KLabel(name='MaybeTValue')))
    if value is None:
        return KApply('NoTValue')
    elif type(value) is int:
        return intToken(value)
    elif type(value) is str:
        return stringToken(value)
    elif type(value) is bytes:
        return KToken(value, KSort(name='Bytes'))


def tvalueList(kavm: KAVM, value: List[Union[str, int, bytes]]) -> KApply:
    if len(value) == 0:
        return KApply('.TValueList')
    else:
        raise NotImplementedError()


def tvalueToken(name: str, value: Optional[int]) -> KApply:
    """Construct a cell containing an Int token. Default to 0 if None is supplied."""

    if isinstance(value, int):
        token = intToken(value)
    elif value is None:
        token = intToken(0)
    else:
        raise TypeError(f'value {value} has unexpected type {type(value)}')
    return KApply(f'{name}', [token])
