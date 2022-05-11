import json
from pathlib import Path
from typing import Any, Callable, Dict, Mapping

from pyk.cli_utils import check_dir_path, check_file_path
from pyk.kast import KDefinition, KFlatModule
from pyk.ktool import KPrint


def teal_to_k(definition_dir: Path, contract_file: Path) -> str:
    check_dir_path(definition_dir)
    check_file_path(contract_file)

    with open(contract_file, 'r') as f:
        contract_json = json.load(f)

    definition = create_definition(contract_json)

    kprint = KPrint(definition_dir)
    patch_symbol_table(kprint.symbolTable)

    return kprint.prettyPrint(definition)


def create_definition(contract_json: Mapping[str, Any]) -> KDefinition:
    return KDefinition(
        main_module_name='TEST_MODULE',
        modules=[
            KFlatModule('TEST_MODULE'),
        ],
    )


def patch_symbol_table(symbol_table: Dict[str, Callable[..., str]]) -> None:
    return
