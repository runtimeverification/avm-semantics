from base64 import b64decode
from typing import List, Optional, cast

from algosdk.v2client import models
from pyk.kast import KApply, KInner, KLabel, KSort, KToken
from pyk.kastManip import split_config_from

from kavm.adaptors.teal_key_value import (
    list_state_to_dict_bytes_bytes,
    list_state_to_dict_bytes_ints,
    teal_key_value_store_from_k_cell,
)
from kavm.pyk_utils import map_bytes_bytes, map_bytes_ints


class KAVMApplicationParams(models.ApplicationParams):

    inverted_attribute_map = {v: k for k, v in models.ApplicationParams.attribute_map.items()}


class KAVMApplication(models.Application):
    """
    Convenience class abstracting an Algorand smart contract (aka stateful application)
    """

    inverted_attribute_map = {v: k for k, v in models.Application.attribute_map.items()}

    @staticmethod
    def from_k_cell(term: KInner, creator: str) -> 'KAVMApplication':
        """
        Parse a KAVMApplication instance from a Kast term
        """
        (_, subst) = split_config_from(term)
        parsed_app_id = int(cast(KToken, subst['APPID_CELL']).token)
        parsed_approval_program = b64decode(cast(KToken, subst['APPROVALPGM_CELL']).token)
        parsed_clear_state_program = b64decode(cast(KToken, subst['CLEARSTATEPGM_CELL']).token)
        parsed_global_state = teal_key_value_store_from_k_cell(
            subst['GLOBALINTS_CELL']
        ) + teal_key_value_store_from_k_cell(subst['GLOBALBYTES_CELL'])
        parsed_params = KAVMApplicationParams(
            # approval_pgm_src=subst['APPROVALPGMSRC_CELL'],
            # clear_state_pgm_src=subst['CLEARSTATEPGMSRC_CELL'],
            creator=creator,
            approval_program=parsed_approval_program if parsed_approval_program else None,
            clear_state_program=parsed_clear_state_program if parsed_clear_state_program else None,
            local_state_schema=models.ApplicationStateSchema(
                num_uint=int(cast(KToken, subst['LOCALNUMINTS_CELL']).token),
                num_byte_slice=int(cast(KToken, subst['LOCALNUMBYTES_CELL']).token),
            ),
            global_state_schema=models.ApplicationStateSchema(
                num_uint=int(cast(KToken, subst['GLOBALNUMINTS_CELL']).token),
                num_byte_slice=int(cast(KToken, subst['GLOBALNUMBYTES_CELL']).token),
            ),
            global_state=parsed_global_state if len(parsed_global_state) else None,
            # extra_pages=int(cast(KToken, subst['EXTRAPAGES_CELL']).token),
        )
        return KAVMApplication(id=parsed_app_id, params=parsed_params)


def application_k_term(
    app_id: int,
    global_state_schema: Optional[models.ApplicationStateSchema] = None,
    local_state_schema: Optional[models.ApplicationStateSchema] = None,
    global_state: Optional[List[models.TealKeyValue]] = None,
) -> KInner:
    global_num_ints = global_state_schema.num_uint if global_state_schema else 0
    global_num_byte_slice = global_state_schema.num_byte_slice if global_state_schema else 0
    local_num_ints = local_state_schema.num_uint if local_state_schema else 0
    local_num_byte_slice = local_state_schema.num_byte_slice if local_state_schema else 0
    global_bytes = list_state_to_dict_bytes_bytes(global_state) if global_state else {}
    global_ints = list_state_to_dict_bytes_ints(global_state) if global_state else {}

    return KApply(
        label=KLabel(name='<app>', params=()),
        args=(
            KApply(label=KLabel(name='<appID>', params=()), args=(KToken(token=str(app_id), sort=KSort(name='Int')),)),
            KApply(
                label=KLabel(name='<approvalPgmSrc>', params=()),
                args=(KApply(label=KLabel(name='.K', params=()), args=()),),
            ),
            KApply(
                label=KLabel(name='<clearStatePgmSrc>', params=()),
                args=(KApply(label=KLabel(name='.K', params=()), args=()),),
            ),
            KApply(
                label=KLabel(name='<approvalPgm>', params=()), args=(KToken(token='""', sort=KSort(name='String')),)
            ),
            KApply(
                label=KLabel(name='<clearStatePgm>', params=()), args=(KToken(token='""', sort=KSort(name='String')),)
            ),
            KApply(
                label=KLabel(name='<globalState>', params=()),
                args=(
                    KApply(
                        label=KLabel(name='<globalNumInts>', params=()),
                        args=(KToken(token=str(global_num_ints), sort=KSort(name='Int')),),
                    ),
                    KApply(
                        label=KLabel(name='<globalNumBytes>', params=()),
                        args=(KToken(token=str(global_num_byte_slice), sort=KSort(name='Int')),),
                    ),
                    KApply(
                        label=KLabel(name='<globalBytes>', params=()),
                        args=[map_bytes_bytes(global_bytes)],
                    ),
                    KApply(
                        label=KLabel(name='<globalInts>', params=()),
                        args=[map_bytes_ints(global_ints)],
                    ),
                ),
            ),
            KApply(
                label=KLabel(name='<localState>', params=()),
                args=(
                    KApply(
                        label=KLabel(name='<localNumInts>', params=()),
                        args=(KToken(token=str(local_num_ints), sort=KSort(name='Int')),),
                    ),
                    KApply(
                        label=KLabel(name='<localNumBytes>', params=()),
                        args=(KToken(token=str(local_num_byte_slice), sort=KSort(name='Int')),),
                    ),
                ),
            ),
            KApply(label=KLabel(name='<extraPages>', params=()), args=(KToken(token='0', sort=KSort(name='Int')),)),
        ),
    )
