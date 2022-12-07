from pyteal import *
from kavm.adaptors.algod_account import KAVMApplication

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

@ABIReturnSubroutine
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """Adds the two arguments and returns the result.

    If addition will overflow a uint64, this method will fail.
    """
    return output.set(a.get() + b.get())


# Register the `add` method with the router, using the default `MethodConfig`
# (only no-op, non-creation calls allowed).
router.add_method_handler(add)

if __name__ == "__main__":
    approval_pgm, clear_pgm, contract = router.compile_program(version=8)
    print(approval_pgm)
    print(clear_pgm)
    print(contract.dictify())
#    prover = AutoProver
