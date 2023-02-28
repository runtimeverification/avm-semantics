import typing
from base64 import b64encode
from typing import Any, Callable, Collection, Dict, List, Optional, Set, Tuple, TypeVar, Union

from algosdk.encoding import decode_address
from algosdk.future.transaction import OnComplete
from pyk.kast.inner import KApply, KInner, KLabel, KSort, KToken, KVariable, Subst, bottom_up, build_assoc, top_down
from pyk.kast.manip import is_anon_var, split_config_from
from pyk.prelude.bytes import bytesToken
from pyk.prelude.k import DOTS
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken
from pyk.utils import dequote_str, hash_str

T = TypeVar("T")


def token_or_expr(
    token_constructor: Callable[[T], KInner],
    value: Union[T, KInner],
) -> KInner:
    if isinstance(value, KInner):
        return value
    else:
        return token_constructor(value)


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


def tvalue_list(values: List[Union[str, int, bytes]]) -> KInner:
    if len(values) == 0:
        return KApply('.TValueList')
    else:
        return generate_tvalue_list([maybe_tvalue(v) for v in values])


def tvalue_bytes_list(values: List[bytes]) -> KInner:
    if len(values) == 0:
        return KApply('.TValueList')
    else:
        return generate_tvalue_list([bytesToken(dequote_str(str(v))[2:-1]) for v in values])


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


def int_2_bytes(term: KInner) -> KInner:
    return KApply(
        "Int2Bytes",
        [
            term,
            KToken("BE", "Endianness"),
            KToken("Unsigned", "Signedness"),
        ],
    )


def generate_tvalue_list(tvlist: List[KInner]) -> KInner:
    if len(tvlist) == 1:
        return tvlist[0]
    else:
        return KApply(
            "___TEAL-TYPES-SYNTAX_TValueNeList_TValue_TValueNeList",
            [
                tvlist[0],
                generate_tvalue_list(tvlist[1:]),
            ],
        )


def algorand_address_to_k_bytes(addr: str) -> KToken:
    """Serialize an Algorand address string to K Bytes token"""
    return bytesToken(dequote_str(str(decode_address(addr)))[2:-1])


def method_selector_to_k_bytes(method_selector: bytes) -> KToken:
    """Serialize an Algorand address string to K Bytes token"""
    return bytesToken(dequote_str(str(method_selector))[2:-1])


def empty_cells_to_dots(kast: KInner, empty_labels: Collection[str]) -> KInner:
    def _empty_cells_to_dots(_kast: KInner) -> KInner:
        if (
            type(_kast) is KApply
            and _kast.is_cell
            and len(_kast.args) == 1
            and type(_kast.args[0]) is KApply
            and _kast.args[0].label.name in empty_labels
        ):
            return DOTS
        else:
            return _kast

    return bottom_up(_empty_cells_to_dots, kast)


def plusInt(i1: KInner, i2: KInner) -> KApply:  # noqa: N802
    return KApply('_+Int_', i1, i2)


def minusInt(i1: KInner, i2: KInner) -> KApply:  # noqa: N802
    return KApply('_-Int_', i1, i2)


def mulInt(i1: KInner, i2: KInner) -> KApply:  # noqa: N802
    return KApply('_*Int_', i1, i2)


def divInt(i1: KInner, i2: KInner) -> KApply:  # noqa: N802
    return KApply('_/Int_', i1, i2)


def eqK(i1: KInner, i2: KInner) -> KApply:  # noqa: N802
    return KApply('_==K_', i1, i2)


# borrowed from kevm_pyk
def existentialize_leafs(term: KInner, keep_vars: Collection[KVariable] = ()) -> KInner:
    '''
    Turn every leaf cell of the term into an existential varaible
    '''
    config, subst = split_config_from(term)
    term_hash = hash_str(term)[0:8]
    for s in subst:
        if not is_anon_var(subst[s]) and subst[s] not in keep_vars:
            subst[s] = KVariable('?' + s + '_' + term_hash)
    return Subst(subst)(config)
