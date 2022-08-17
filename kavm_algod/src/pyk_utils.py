from base64 import b64encode
from typing import List, Optional, Union

from pyk.kast import KApply, KInner, KToken, KSort
from pyk.prelude import intToken, stringToken

from kavm_algod.kavm import KAVM


def maybeTValue(kavm: KAVM, value: Optional[Union[str, int]]) -> KInner:
    # print(kavm.definition.production_for_klabel(KLabel(name='MaybeTValue')))
    if value is None:
        return KApply('NoTValue')
    elif type(value) is int:
        return intToken(value)
    elif type(value) is str:
        return stringToken(value)
    elif type(value) is bytes:
        return stringToken(b64encode(value).decode('utf8'))
    else:
        raise TypeError()


def tvalueList(kavm: KAVM, value: List[Union[str, int, bytes]]) -> KInner:
    if len(value) == 0:
        return KApply('.TValueList')
    else:
        raise NotImplementedError()
