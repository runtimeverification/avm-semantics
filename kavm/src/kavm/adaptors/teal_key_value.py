import base64
import typing
from typing import Dict, List, cast

from algosdk.v2client import models
from pyk.kast.inner import KApply, KInner, KToken

# @typing.no_type_check
# def list_to_dict_state(l: List[models.TealKeyValue]) -> Dict[str, str | int]:
#     d = {}
#     for item in l:
#         if item.value['type'] == 1:
#             value = item.value['bytes']
#         else:
#             value = item.value['uint']
#         d[item.key] = value
#     return d


def raw_list_state_to_dict_bytes_bytes(l: List[Dict]) -> Dict[str, str]:
    d = {}
    for item in l:
        if item['value'] and item['value']['type'] == 1:
            value = item['value']['bytes']
            d[base64.b64decode(item['key']).decode('ascii')] = base64.b64decode(value).decode('ascii')
    return d


def raw_list_state_to_dict_bytes_ints(l: List[Dict]) -> Dict[str, int]:
    d = {}
    for item in l:
        if item['value'] and item['value']['type'] == 2:
            value = item['value']['uint']
            d[base64.b64decode(item['key']).decode('ascii')] = value
    return d


def list_state_to_dict_bytes_bytes(l: List[models.TealKeyValue]) -> Dict[str, str]:
    d = {}
    for item in l:
        if item.value and item.value['type'] == 1:
            value = item.value['bytes']
            d[item.key] = value
    return d


def list_state_to_dict_bytes_ints(l: List[models.TealKeyValue]) -> Dict[str, int]:
    d = {}
    for item in l:
        if item.value and item.value['type'] == 2:
            value = item.value['uint']
            d[item.key] = value
    return d


@typing.no_type_check
def list_to_dict_apps_created(l):
    d = {}
    for item in l:
        d[item['id']] = item
    return d


def teal_key_value_store_from_k_cell(term: KInner) -> List[models.TealKeyValue]:
    if cast(KApply, term).label.name == '_|->_':
        if cast(KToken, cast(KApply, term).args[1]).sort.name == 'Bytes':
            return [
                models.TealKeyValue(
                    key=cast(KToken, cast(KApply, term).args[0]).token[2:-1],
                    value=models.TealValue(type=1, bytes=cast(KToken, cast(KApply, term).args[1]).token[2:-1]),
                )
            ]
        if cast(KToken, cast(KApply, term).args[1]).sort.name == 'Int':
            return [
                models.TealKeyValue(
                    key=cast(KToken, cast(KApply, term).args[0]).token[2:-1],
                    value=models.TealValue(type=2, uint=int(cast(KToken, cast(KApply, term).args[1]).token)),
                )
            ]
        else:
            return []
    if cast(KApply, term).label.name == '_Map_':
        return teal_key_value_store_from_k_cell(cast(KApply, term).args[0]) + teal_key_value_store_from_k_cell(
            cast(KApply, term).args[1]
        )
    if cast(KApply, term).label.name == '.Map':
        return []
    return []


# class KAVMTealKeyValueStore(list):
#     @typing.no_type_check
#     @classmethod
#     def from_k_cell(cls, term: KInner) -> 'KAVMTealKeyValueStore':
#         if term.label.name == '_|->_':
#             if term.args[1].sort.name == 'Bytes':
#                 return KAVMTealKeyValueStore(
#                     [
#                         {
#                             'key': cast(KToken, term.args[0]).token[2:-1],
#                             'value': models.TealValue(type=1, bytes=cast(KToken, term.args[1]).token[2:-1]),
#                         }
#                     ]
#                 )
#             if term.args[1].sort.name == 'Int':
#                 return KAVMTealKeyValueStore(
#                     [
#                         {
#                             'key': cast(KToken, term.args[0]).token[2:-1],
#                             'value': models.TealValue(type=2, uint=int(cast(KToken, term.args[1]).token)),
#                         }
#                     ]
#                 )
#             else:
#                 return KAVMTealKeyValueStore([])
#         if term.label.name == '_Map_':
#             return cls.from_k_cell(term.args[0]) + cls.from_k_cell(term.args[1])
#         if term.label.name == '.Map':
#             return KAVMTealKeyValueStore([])
#         return KAVMTealKeyValueStore([])
