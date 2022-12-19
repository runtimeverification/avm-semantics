from typing import Dict, Optional

from pyk.kast.inner import KApply, KInner, KLabel, KSort, KToken, Subst, build_assoc
from pyk.kast.manip import split_config_from
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken

from kavm.adaptors.teal_key_value import raw_list_state_to_dict_bytes_bytes, raw_list_state_to_dict_bytes_ints
from kavm.constants import MIN_BALANCE
from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_address_to_k_bytes, map_bytes_bytes, map_bytes_ints


class KAVMTermFactory:
    def __init__(self, kavm: KAVM):
        self._kavm = kavm

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

    def opt_in_asset_cell(self, sdk_asset_holding: Dict, symbolic_fields_subst: Optional[Subst] = None) -> KInner:
        symbolic_fields_subst = symbolic_fields_subst if symbolic_fields_subst else Subst({})

        symbolic_opt_in_asset_cell, _ = split_config_from(self._kavm.definition.init_config(KSort('OptInAssetCellMap')))

        sdk_fields_subst = Subst(
            {
                'OPTINASSETID_CELL': intToken(sdk_asset_holding['asset-id']),
                'OPTINASSETBALANCE_CELL': intToken(sdk_asset_holding['amount']),
                'OPTINASSETFROZEN_CELL': intToken(1) if sdk_asset_holding['is-frozen'] else intToken(0),
            }
        )

        opt_in_asset_cell = sdk_fields_subst.compose(symbolic_fields_subst).apply(symbolic_opt_in_asset_cell)  # type: ignore

        return opt_in_asset_cell

    def account_cell(self, sdk_account_dict: Dict, symbolic_fields_subst: Optional[Subst] = None) -> KInner:
        symbolic_fields_subst = symbolic_fields_subst if symbolic_fields_subst else Subst({})

        symbolic_account_cell, default_fields_subst = split_config_from(
            self._kavm.definition.init_config(KSort('AccountCellMap'))
        )

        try:
            assert sdk_account_dict['apps-local-state']
            apps_local_state = sdk_account_dict['apps-local-state']
        except (KeyError, AssertionError):
            apps_local_state = []

        sdk_fields_subst = Subst(
            {
                'ADDRESS_CELL': algorand_address_to_k_bytes(sdk_account_dict['address']),
                'BALANCE_CELL': intToken(sdk_account_dict['amount']),
                'MINBALANCE_CELL': intToken(sdk_account_dict['min-balance'])
                if 'min-balance' in sdk_account_dict
                else intToken(MIN_BALANCE),
                'ROUND_CELL': intToken(sdk_account_dict['round'])
                if sdk_account_dict['round']
                else default_fields_subst['ROUND_CELL'],
                'PREREWARDS_CELL': intToken(sdk_account_dict['pending-rewards'])
                if sdk_account_dict['pending-rewards']
                else default_fields_subst['PREREWARDS_CELL'],
                'REWARDS_CELL': intToken(sdk_account_dict['rewards'])
                if sdk_account_dict['rewards']
                else default_fields_subst['REWARDS_CELL'],
                'STATUS_CELL': intToken(sdk_account_dict['status'])
                if sdk_account_dict['status']
                else default_fields_subst['STATUS_CELL'],
                'KEY_CELL': algorand_address_to_k_bytes(sdk_account_dict['auth-addr'])
                if sdk_account_dict['auth-addr']
                else algorand_address_to_k_bytes(sdk_account_dict['address']),
                'APPSCREATED_CELL': build_assoc(
                    KToken('.Bag', 'AppMapCell'),
                    '_AppCellMap_',
                    [self.app_cell(sdk_app) for sdk_app in sdk_account_dict['created-apps']],
                ),
                'APPSOPTEDIN_CELL': build_assoc(
                    KToken('.Bag', 'OptInAppMapCell'),
                    '_OptInAppCellMap_',
                    [self.opt_in_app_cell(sdk_app_local_state) for sdk_app_local_state in apps_local_state],
                ),
                'ASSETSCREATED_CELL': build_assoc(
                    KToken('.Bag', 'AssetMapCell'),
                    '_AssetCellMap_',
                    [self.asset_cell(sdk_asset) for sdk_asset in sdk_account_dict['created-assets']],
                ),
                'ASSETSOPTEDIN_CELL': build_assoc(
                    KToken('.Bag', 'OptInAssetMapCell'),
                    '_OptInAssetCellMap_',
                    [self.opt_in_asset_cell(sdk_asset_holding) for sdk_asset_holding in sdk_account_dict['assets']],
                ),
                'BOXES_CELL': build_assoc(KToken('.Bag', 'BoxMapCell'), '_BoxCellMap_', []),
            }
        )

        account_cell = sdk_fields_subst.compose(symbolic_fields_subst).apply(symbolic_account_cell)  # type: ignore

        return account_cell

    def app_cell(self, sdk_app_dict: Dict, symbolic_fields_subst: Optional[Subst] = None) -> KInner:
        symbolic_fields_subst = symbolic_fields_subst if symbolic_fields_subst else Subst({})

        symbolic_app_cell, _ = split_config_from(self._kavm.definition.init_config(KSort('AppCellMap')))

        try:
            global_num_uint = sdk_app_dict['params']['global-state-schema']['num-uint']
        except KeyError:
            global_num_uint = 0
        try:
            global_num_byte_slice = sdk_app_dict['params']['global-state-schema']['num-byte-slice']
        except KeyError:
            global_num_byte_slice = 0
        try:
            local_num_uint = sdk_app_dict['params']['local-state-schema']['num-uint']
        except KeyError:
            local_num_uint = 0
        try:
            local_num_byte_slice = sdk_app_dict['params']['local-state-schema']['num-byte-slice']
        except KeyError:
            local_num_byte_slice = 0
        try:
            extra_pages = sdk_app_dict['params']['extra-pages']
        except KeyError:
            extra_pages = 0
        try:
            global_state = sdk_app_dict['params']['global-state']
            global_bytes = raw_list_state_to_dict_bytes_bytes(global_state)
            global_ints = raw_list_state_to_dict_bytes_ints(global_state)
        except KeyError:
            global_bytes = {}
            global_ints = {}

        sdk_fields_subst = Subst(
            {
                'APPID_CELL': intToken(sdk_app_dict['id']),
                'APPROVALPGMSRC_CELL': KApply(
                    label=KLabel(name='int__TEAL-OPCODES_PseudoOpCode_PseudoTUInt64', params=()),
                    args=[KToken(token='0', sort=KSort(name='Int'))],
                ),
                'CLEARSTATEPGMSRC_CELL': KApply(
                    label=KLabel(name='int__TEAL-OPCODES_PseudoOpCode_PseudoTUInt64', params=()),
                    args=[KToken(token='0', sort=KSort(name='Int'))],
                ),
                'APPROVALPGM_CELL': stringToken(sdk_app_dict['params']['approval-program']),
                'CLEARSTATEPGM_CELL': stringToken(sdk_app_dict['params']['clear-state-program']),
                'GLOBALNUMINTS_CELL': intToken(global_num_uint),
                'GLOBALNUMBYTES_CELL': intToken(global_num_byte_slice),
                'LOCALNUMINTS_CELL': intToken(local_num_uint),
                'LOCALNUMBYTES_CELL': intToken(local_num_byte_slice),
                'GLOBALBYTES_CELL': map_bytes_bytes(global_bytes),
                'GLOBALINTS_CELL': map_bytes_ints(global_ints),
                'EXTRAPAGES_CELL': intToken(extra_pages),
            }
        )

        app_cell = sdk_fields_subst.compose(symbolic_fields_subst).apply(symbolic_app_cell)  # type: ignore

        return app_cell

    def opt_in_app_cell(self, sdk_app_local_state: Dict, symbolic_fields_subst: Optional[Subst] = None) -> KInner:
        raise NotImplementedError()

        symbolic_fields_subst = symbolic_fields_subst if symbolic_fields_subst else Subst({})

        symbolic_opt_in_app_cell, _ = split_config_from(self._kavm.definition.init_config(KSort('OptInAssetCellMap')))

        sdk_fields_subst = Subst({})

        opt_in_app_cell = sdk_fields_subst.compose(symbolic_fields_subst).apply(symbolic_opt_in_app_cell)  # type: ignore

        return opt_in_app_cell
