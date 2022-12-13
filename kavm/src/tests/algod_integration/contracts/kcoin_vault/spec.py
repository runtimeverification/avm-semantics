import logging
import sys
from pathlib import Path

from algosdk.abi.contract import get_method_by_name
from algosdk.future.transaction import StateSchema
from kcoin_vault_pyteal import router
from pyk.kast.inner import KApply, KVariable
from pyk.prelude.kint import intToken

from kavm.prover import AutoProver, MethodWithSpec


def write_to_file(program: str, path: Path):
    with open(path, "w") as f:
        f.write(program)


if __name__ == "__main__":
    sys.setrecursionlimit(15000000)
    logging.basicConfig(level=logging.INFO)

    approval_pgm, clear_pgm, contract = router.compile_program(version=8)
    write_to_file(approval_pgm, Path('approval.teal'))
    write_to_file(clear_pgm, Path('clear.teal'))

    # add_with_spec = MethodWithSpec(
    #     preconditions=[AutoProver._in_bounds_uint64(KApply("_+Int_", [KVariable("A"), KVariable("B")]))],
    #     postconditions=[
    #         KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(A +Int B, BE, Unsigned), 8, 0)
    #             "_==K_",
    #             [
    #                 KVariable('?FINAL_LOGDATA_CELL'),
    #                 KApply(
    #                     '_+Bytes_',
    #                     [
    #                         bytesToken("\\x15\\x1f|u"),
    #                         KApply(
    #                             'padLeftBytes',
    #                             [
    #                                 KApply(
    #                                     'Int2Bytes',
    #                                     [
    #                                         KApply(
    #                                             "_+Int_",
    #                                             [KVariable("A"), KVariable("B")],
    #                                         ),
    #                                         KToken('BE', KSort('Endianness')),
    #                                         KToken('Unsigned', KSort('Signedness')),
    #                                     ],
    #                                 ),
    #                                 intToken(8),
    #                                 intToken(0),
    #                             ],
    #                         ),
    #                     ],
    #                 ),
    #             ],
    #         )
    #     ],
    #     sdk_method=get_method_by_name(name='', methods=contract.methods),
    # )
    # contract.methods[0] = add_with_spec
    contract.methods[1] = MethodWithSpec(
        preconditions=[KApply('_<=Int_', [KVariable('PAYMENT'), intToken(100000)])],
        # postconditions=[
        #     KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(PAYMENT, BE, Unsigned), 8, 0)
        #         "_==K_",
        #         [
        #             KVariable('?FINAL_LOGDATA_CELL'),
        #             KApply(
        #                 '_+Bytes_',
        #                 [
        #                     bytesToken("\\x15\\x1f|u"),
        #                     KApply(
        #                         'padLeftBytes',
        #                         [
        #                             KApply(
        #                                 'Int2Bytes',
        #                                 [
        #                                     KVariable('PAYMENT'),
        #                                     KToken('BE', KSort('Endianness')),
        #                                     KToken('Unsigned', KSort('Signedness')),
        #                                 ],
        #                             ),
        #                             intToken(8),
        #                             intToken(0),
        #                         ],
        #                     ),
        #                 ],
        #             ),
        #         ],
        #     )
        # ],
        sdk_method=get_method_by_name(name='mint', methods=contract.methods),
    )

    prover = AutoProver(
        definition_dir=Path('./tests/specs/verification-kompiled'),
        approval_pgm=Path('approval.teal'),
        clear_pgm=Path('clear.teal'),
        contract=contract,
        global_schema=StateSchema(num_uints=2, num_byte_slices=0),
        local_schema=StateSchema(0, 0),
    )
    prover.prove('mint')
