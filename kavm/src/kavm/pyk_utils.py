import typing
from base64 import b64encode
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from algosdk.future.transaction import OnComplete
from pyk.kast.inner import KApply, KInner, KLabel, KSort, KToken, KVariable, build_assoc, top_down
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken


def maybe_tvalue(value: Optional[Union[str, int, bytes]]) -> KInner:
    if value is None:
        return KApply('NoTValue')
    elif type(value) is int:
        return intToken(value)
    elif type(value) is OnComplete:
        return intToken(int(value))
    elif type(value) is str:
        if len(value):
            return stringToken(value)
        else:
            return KApply('NoTValue')
    elif type(value) is bytes:
        if len(value):
            return stringToken(b64encode(value).decode('utf8'))
        else:
            return KApply('NoTValue')
    else:
        raise TypeError()


def tvalue(value: Union[str, int, bytes]) -> KInner:
    if type(value) is int:
        return intToken(value)
    elif type(value) is OnComplete:
        return intToken(int(value))
    elif type(value) is str:
        return stringToken(value)
    elif type(value) is bytes:
        return stringToken(b64encode(value).decode('utf8'))
    else:
        raise TypeError()


def tvalue_list(value: List[Union[str, int, bytes]]) -> KInner:
    if len(value) == 0:
        return KApply('.TValueList')
    else:
        raise NotImplementedError()


def map_bytes_bytes(d: Dict[str, str]) -> KInner:
    """Convert a Dict[str, str] into a K Bytes to Bytes Map"""
    return build_assoc(
        KApply('.Map'),
        KLabel('_Map_'),
        [
            KApply(
                '_|->_', [KToken(token=f'b"{k}"', sort=KSort('Bytes')), KToken(token=f'b"{v}"', sort=KSort('Bytes'))]
            )
            for k, v in d.items()
        ],
    )


def map_bytes_ints(d: Dict[str, int]) -> KInner:
    """Convert a Dict[str, int] into a K Bytes to Int Map"""
    return build_assoc(
        KApply('.Map'),
        KLabel('_Map_'),
        [
            KApply('_|->_', [KToken(token=f'b"{k}"', sort=KSort('Bytes')), KToken(str(v), sort=KSort('Int'))])
            for k, v in d.items()
        ],
    )


def split_direct_subcells_from(configuration: KInner) -> Tuple[KInner, Any]:
    """
    Split the *direct* subcell substitution from a given configuration.

    Like pyk.kastManip.split_config_from, but does not recurse deeper than one layer
    """
    initial_substitution = {}

    def _mk_cell_var(label: str) -> str:
        return label.replace('-', '_').replace('<', '').replace('>', '').upper() + '_CELL'

    def _replace_with_var(k: KInner) -> KInner:
        if type(k) is KApply and k.is_cell:
            config_var = _mk_cell_var(k.label.name)
            initial_substitution[config_var] = k.args[0]
            return KApply(k.label, [KVariable(config_var)])
        return k

    symbolic_config = configuration.map_inner(_replace_with_var)
    return (symbolic_config, initial_substitution)


@typing.no_type_check
def carefully_split_config_from(configuration: KInner, ignore_cells: Optional[Set[str]]) -> Tuple[KInner, Any]:
    """
    Like pyk.kastManip.split_config_from, but does not substitute the given cells with variables
    """
    initial_substitution = {}

    if ignore_cells is None:
        ignore_cells = set()

    def _mk_cell_var(label: str) -> str:
        return label.replace('-', '_').replace('<', '').replace('>', '').upper() + '_CELL'

    def _replace_with_var(k: KInner) -> KInner:
        if type(k) is KApply and k.is_cell:
            if (k.arity == 1 and not (type(k.args[0]) is KApply and k.args[0].is_cell)) or (
                k.arity == 1 and not (k.label.name in ignore_cells)
            ):
                config_var = _mk_cell_var(k.label.name)
                initial_substitution[config_var] = k.args[0]
                return KApply(k.label, [KVariable(config_var)])
        return k

    symbolic_config = top_down(_replace_with_var, configuration)
    return (symbolic_config, initial_substitution)
