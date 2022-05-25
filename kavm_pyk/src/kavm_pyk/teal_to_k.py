import json
from pathlib import Path
from typing import Any, Callable, Dict, Mapping

from pyk.cli_utils import check_dir_path, check_file_path
from pyk.kast import KDefinition, KFlatModule
from pyk.ktool import KPrint, paren


class KAVM(KPrint):

    def __init__(self, kompiled_dir: Path):
        super().__init__(kompiled_dir)
        self.patch_symbol_table(self.symbol_table)

    @staticmethod
    def patch_symbol_table(symbol_table: Dict[str, Callable[..., str]]) -> None:
        symbol_table['_+Int_'] = paren(symbol_table['_+Int_'])


def teal_to_k(definition_dir: Path, contract_file: Path) -> str:
    check_dir_path(definition_dir)
    check_file_path(contract_file)

    with open(contract_file, 'r') as f:
        contract_json = json.load(f)

    kavm = KAVM(definition_dir)
    definition = create_definition(contract_json)
    return kavm.pretty_print(definition)


def create_definition(contract_json: Mapping[str, Any]) -> KDefinition:
    return KDefinition(
        main_module_name='TEST_MODULE',
        modules=[
            KFlatModule('TEST_MODULE'),
        ],
    )
