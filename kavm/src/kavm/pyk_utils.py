from collections.abc import MutableMapping
from base64 import b64encode
from typing import List, Optional, Union, cast, Callable, Any, Type
import re

from algosdk.future.transaction import OnComplete
from pyk.kast import KAst, KApply, KInner, KLabel, top_down
from pyk.prelude import build_cons, build_assoc, intToken, stringToken


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


def tvalue_list(value: List[Union[str, int, bytes]]) -> KInner:
    if len(value) == 0:
        return KApply('.TValueList')
    else:
        raise NotImplementedError()


class KCellMap(MutableMapping):
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
        self._store = dict()
        self._unit_klabel = unit_klabel.name if isinstance(unit_klabel, KLabel) else unit_klabel
        assert self._unit_klabel.endswith('CellMap')
        self._item_cell_name = '<' + re.sub('CellMap$', '', self._unit_klabel).strip('.').lower() + '>'
        self._cons_klabel = cons_klabel.name if isinstance(cons_klabel, KLabel) else cons_klabel
        assert self._cons_klabel.endswith('CellMap_')
        self._key_klabel = key_klabel.name if isinstance(key_klabel, KLabel) else key_klabel
        self._value_initializer = value_initializer
        self._value_k_cell = value_k_cell

        def extractor(inner: KInner):
            if type(inner) is KApply and inner.label.name == self._item_cell_name:
                key = int(inner.args[0].args[0].token) if key_type is int else str(inner.args[0].args[0].token)
                self._store[key] = value_initializer(inner)
            return inner

        if term:
            top_down(extractor, cast(KInner, term))

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __eq__(self, other: 'KCellMap'):
        klabels_are_same = self._unit_klabel == other._unit_klabel and self._cons_klabel == other._cons_klabel
        stores_are_same = len(self._store) == len(other._store) and self._store == other._store
        return klabels_are_same and stores_are_same

    def __repr__(self):
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


class AccountCellMap(KCellMap):
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


class AppCellMap(KCellMap):
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
    def from_list(apps: List[Any]):
        result = AppCellMap()
        for app in apps:
            result._store[app._appID] = app
        return result
