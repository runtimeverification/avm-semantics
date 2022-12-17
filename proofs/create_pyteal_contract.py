import logging
from pathlib import Path
from algosdk.abi.contract import get_method_by_name
from algosdk.account import generate_account
from algosdk.future.transaction import PaymentTxn, StateSchema
from kavm.adaptors.algod_transaction import transaction_k_term
from kavm.algod import KAVMClient
from pyteal import *
from kavm.prover import AutoProver, MethodWithSpec

from pyk.prelude.bytes import bytesToken
from pyk.prelude.kint import intToken
from pyk.kast.inner import KApply, KInner, KSort, KToken, Subst, KVariable

router = Router(
    name="Calculator",
    bare_calls=BareCallActions(
        # Allow this app to be created with a no-op call
        no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
        # Allow standalone user opt in and close out
        opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
        close_out=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
    ),
)


@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Adds the two arguments and returns the result.

    If addition will overflow a uint64, this method will fail.
    """
    return output.set(a.get() + b.get())


@router.method
def donate(payment: abi.PaymentTransaction, *, output: abi.Uint64) -> Expr:
    """Donate Algos to the contaract. Returns the donated amount."""
    return Seq(
        Assert(payment.get().receiver() == Global.current_application_address()),
        output.set(payment.get().amount()),
    )


def write_to_file(program: str, path: Path):
    with open(path, "w") as f:
        f.write(program)


if __name__ == "__main__":
    # add_method_with_spec = KAVMMethod(get_method_by_name(name='add', methods=router.methods))

    logging.basicConfig(level=logging.INFO)

    approval_pgm, clear_pgm, contract = router.compile_program(version=8)
    write_to_file(approval_pgm, Path('approval.teal'))
    write_to_file(clear_pgm, Path('clear.teal'))

    # print(contract.dictify())
    add_with_spec = MethodWithSpec(
        preconditions=[
            AutoProver._in_bounds_uint64(
                KApply("_+Int_", [KVariable("A"), KVariable("B")])
            )
        ],
        postconditions=[
            KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(A +Int B, BE, Unsigned), 8, 0)
                "_==K_",
                [
                    KVariable('?FINAL_LOGDATA_CELL'),
                    KApply(
                        '_+Bytes_',
                        [
                            bytesToken("\\x15\\x1f|u"),
                            KApply(
                                'padLeftBytes',
                                [
                                    KApply(
                                        'Int2Bytes',
                                        [
                                            KApply(
                                                "_+Int_",
                                                [KVariable("A"), KVariable("B")],
                                            ),
                                            KToken('BE', KSort('Endianness')),
                                            KToken('Unsigned', KSort('Signedness')),
                                        ],
                                    ),
                                    intToken(8),
                                    intToken(0),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
        sdk_method=get_method_by_name(name='add', methods=contract.methods),
    )
    contract.methods[0] = add_with_spec
    contract.methods[1] = MethodWithSpec(
        preconditions=[KApply('_<=Int_', [KVariable('PAYMENT'), intToken(100000)])],
        postconditions=[
            KApply(  # ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(PAYMENT, BE, Unsigned), 8, 0)
                "_==K_",
                [
                    KVariable('?FINAL_LOGDATA_CELL'),
                    KApply(
                        '_+Bytes_',
                        [
                            bytesToken("\\x15\\x1f|u"),
                            KApply(
                                'padLeftBytes',
                                [
                                    KApply(
                                        'Int2Bytes',
                                        [
                                            KVariable('PAYMENT'),
                                            KToken('BE', KSort('Endianness')),
                                            KToken('Unsigned', KSort('Signedness')),
                                        ],
                                    ),
                                    intToken(8),
                                    intToken(0),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
        sdk_method=get_method_by_name(name='donate', methods=contract.methods),
    )

    prover = AutoProver(
        definition_dir=Path('./tests/specs/verification-kompiled'),
        approval_pgm=Path('approval.teal'),
        clear_pgm=Path('clear.teal'),
        contract=contract,
        global_schema=StateSchema(0, 0),
        local_schema=StateSchema(0, 0),
    )
    prover.prove('donate')
