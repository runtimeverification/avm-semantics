import re
import typing
from base64 import b64encode
from collections.abc import MutableMapping
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, cast

from algosdk.future.transaction import OnComplete
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken
from pyk.kast import (
    KApply,
    KAst,
    KInner,
    KLabel,
    KSort,
    KToken,
    KVariable,
    build_assoc,
    build_cons,
    top_down,
)


def maybe_tvalue(value: Optional[Union[str, int, bytes]]) -> KInner:
    if value is None:
        return KApply('NoTValue')
    elif type(value) is int:
        return intToken(value)
    elif type(value) is OnComplete:
        return intToken(int(value))
    elif type(value) is str:
        return stringToken(value)
    elif type(value) is bytes:
        return stringToken(b64encode(value).decode('utf8'))
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


def tvalue_elem(value: Union[str, int, bytes]) -> KInner:
    if type(value) is int:
        return intToken(value)
    elif type(value) is OnComplete:
        return intToken(int(value))
    elif type(value) is str:
        return stringToken(value)
    elif type(value) is bytes:
        return stringToken(value.decode())
    else:
        raise TypeError()


def tvalue_list(value: List[Union[str, int, bytes]]) -> KInner:
    if len(value) == 0:
        return KApply('.TValueList')
    if len(value) == 1:
        return tvalue_elem(value[0])
    return KApply('TValueListCons', [tvalue_elem(value[0]), tvalue_list(value[1:])])


def map_bytes_bytes(d):
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


def from_map(term: KInner) -> Dict:
    if term.label.name == '_|->_':
        if term.args[1].sort.name == 'Bytes':
            return {term.args[0].token[2:-1]: term.args[1].token[2:-1]}
        if term.args[1].sort.name == 'Int':
            return {term.args[0].token[2:-1]: int(term.args[1].token)}
    if term.label.name == '_Map_':
        return from_map(term.args[0]) | from_map(term.args[1])
    if term.label.name == '.Map':
        return {}


def map_bytes_ints(d):
    """Convert a Dict[str, int] into a K Bytes to Int Map"""
    return build_assoc(
        KApply('.Map'),
        KLabel('_Map_'),
        [
            KApply('_|->_', [KToken(token=f'b"{k}"', sort=KSort('Bytes')), KToken(str(v), sort=KSort('Int'))])
            for k, v in d.items()
        ],
    )


def unescape_global_storage_bytes(value: str):
    """Prepare a Bytes token for algosdk consumption"""
    unescaped_token_bytes = value.encode('utf-8').decode('unicode_escape').encode('latin-1')
    return b64encode(unescaped_token_bytes).decode('ascii')


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


class KCellMap(MutableMapping):
    '''Represents K type=map cell as a Python dict'''

    def __init__(
        self,
        unit_klabel: Union[str, KLabel],
        cons_klabel: Union[str, KLabel],
        key_klabel: Union[str, KLabel],
        key_type: Type,
        value_initializer: Callable[[KInner], Any],
        value_k_cell: Callable[[Any], KInner],
        term: Optional[KAst] = None,
    ):
        self._store: Dict[Any, Any] = {}
        self._unit_klabel = unit_klabel.name if isinstance(unit_klabel, KLabel) else unit_klabel
        assert self._unit_klabel.endswith('CellMap')
        item_name = re.sub('CellMap$', '', self._unit_klabel).strip('.')
        self._item_cell_name = '<' + item_name[0].lower() + item_name[1:] + '>'
        self._cons_klabel = cons_klabel.name if isinstance(cons_klabel, KLabel) else cons_klabel
        assert self._cons_klabel.endswith('CellMap_')
        self._key_klabel = key_klabel.name if isinstance(key_klabel, KLabel) else key_klabel
        self._value_initializer = value_initializer
        self._value_k_cell = value_k_cell

        @typing.no_type_check
        def extractor(inner: KInner) -> KInner:
            if type(inner) is KApply and inner.label.name == self._item_cell_name:
                key = int(inner.args[0].args[0].token) if key_type is int else str(inner.args[0].args[0].token)
                self._store[key] = value_initializer(inner)
            return inner

        if term:
            top_down(extractor, cast(KInner, term))

    def __getitem__(self, key: Any) -> Any:
        return self._store[key]

    def __setitem__(self, key: Any, value: Any) -> Any:
        self._store[key] = value

    def __delitem__(self, key: Any) -> None:
        del self._store[key]

    def __iter__(self) -> Any:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __eq__(self, other: Any) -> bool:
        klabels_are_same = self._unit_klabel == other._unit_klabel and self._cons_klabel == other._cons_klabel
        stores_are_same = len(self._store) == len(other._store) and self._store == other._store
        return klabels_are_same and stores_are_same

    def __repr__(self) -> str:
        return repr(self._store)

    @property
    def k_cell(self) -> KInner:
        if len(self):
            return build_cons(
                unit=KApply(
                    label=KLabel(name=self._unit_klabel),
                ),
                label=self._cons_klabel,
                terms=[self._value_k_cell(value) for value in self._store.values()],
            )
        else:
            return KApply(
                label=KLabel(name=self._unit_klabel),
            )


class TransactionCellMap(KCellMap):
    '''Python-friendly access to <transactions> cell'''

    def __init__(
        self,
        kavm: Any,
        term: Optional[KAst] = None,
    ):
        from kavm.adaptors.transaction import KAVMTransaction

        super().__init__(
            unit_klabel='.TransactionCellMap',
            cons_klabel='_TransactionCellMap_',
            key_klabel='<txID>',
            key_type=str,
            value_initializer=lambda x: KAVMTransaction.transaction_from_k(kavm, x),
            value_k_cell=lambda x: x.transaction_cell,
            term=term,
        )


class AccountCellMap(KCellMap):
    '''Python-friendly access to <accounts> cell'''

    def __init__(
        self,
        term: Optional[KAst] = None,
    ):
        from kavm.adaptors.account import KAVMAccount

        super().__init__(
            unit_klabel='.AccountCellMap',
            cons_klabel='_AccountCellMap_',
            key_klabel='<address>',
            key_type=str,
            value_initializer=KAVMAccount.from_account_cell,
            value_k_cell=KAVMAccount.to_account_cell,
            term=term,
        )


class AppOptInCellMap(KCellMap):
    '''Python-friendly access to <appsOptedIn> cell'''

    def __init__(
        self,
        term: Optional[KAst] = None,
    ):
        from kavm.adaptors.account import KAVMOptInApp

        super().__init__(
            unit_klabel='.OptInAppCellMap',
            cons_klabel='_OptInAppCellMap_',
            key_klabel='<optInAppID>',
            key_type=int,
            value_initializer=KAVMOptInApp.from_optin_app_cell,
            value_k_cell=KAVMOptInApp.to_optin_app_cell,
            term=term,
        )


class AppCellMap(KCellMap):
    '''Python-friendly access to <appsCreated> cell'''

    def __init__(
        self,
        term: Optional[KAst] = None,
    ):
        from kavm.adaptors.application import KAVMApplication

        super().__init__(
            unit_klabel='.AppCellMap',
            cons_klabel='_AppCellMap_',
            key_klabel='<appID>',
            key_type=int,
            value_initializer=KAVMApplication.from_app_cell,
            value_k_cell=KAVMApplication.to_app_cell,
            term=term,
        )

    @staticmethod
    def from_list(apps: List[Any]) -> 'AppCellMap':
        result = AppCellMap()
        for app in apps:
            result._store[app._app_id] = app
        return result
