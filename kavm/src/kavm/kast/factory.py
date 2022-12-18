from typing import Dict, Optional

from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_address_to_k_bytes

from pyk.kast.inner import KInner, KSort, Subst
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken
from pyk.kast.manip import split_config_from


class KAVMTermFactory:
    def __init__(self, kavm: KAVM):
        self._kavm = kavm
        pass

    def asset_cell(self, sdk_asset_dict: Dict, symbolic_fields_subst: Optional[Subst] = None) -> KInner:
        symbolic_fields_subst = symbolic_fields_subst if symbolic_fields_subst else Subst({})

        symbolic_asset_cell, _ = split_config_from(self._kavm.definition.init_config(KSort('AssetCellMap')))

        sdk_fields_subst = Subst(
            {
                'ASSETID_CELL': intToken(sdk_asset_dict['index']),
                'ASSETNAME_CELL': stringToken(sdk_asset_dict['params']['name']),
                'ASSETUNITNAME_CELL': stringToken(sdk_asset_dict['params']['unit-name']),
                'ASSETTOTAL_CELL': intToken(sdk_asset_dict['params']['total']),
                'ASSETDECIMALS_CELL': intToken(sdk_asset_dict['params']['decimals']),
                'ASSETDEFAULTFROZEN_CELL': intToken(1) if sdk_asset_dict['params']['default-frozen'] else intToken(0),
                'ASSETURL_CELL': stringToken(sdk_asset_dict['params']['url']),
                'ASSETMETADATAHASH_CELL': stringToken(sdk_asset_dict['params']['metadata-hash']),
                'ASSETMANAGERADDR_CELL': algorand_address_to_k_bytes(sdk_asset_dict['params']['manager']),
                'ASSETRESERVEADDR_CELL': algorand_address_to_k_bytes(sdk_asset_dict['params']['reserve']),
                'ASSETFREEZEADDR_CELL': algorand_address_to_k_bytes(sdk_asset_dict['params']['freeze']),
                'ASSETCLAWBACKADDR_CELL': algorand_address_to_k_bytes(sdk_asset_dict['params']['clawback']),
            }
        )

        asset_cell = sdk_fields_subst.compose(symbolic_fields_subst).apply(symbolic_asset_cell)  # type: ignore

        return asset_cell

    def account_cell(self, sdk_account_dict: Dict) -> KInner:
        pass

    def app_cell(self, sdk_app_dict: Dict) -> KInner:
        pass
