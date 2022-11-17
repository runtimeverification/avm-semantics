from pyteal import Approve, BareCallActions, Expr, OnCompleteAction, OptimizeOptions, Router, abi

# Main router class
router = Router(
    # Name of the contract
    name="calculator",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction.never(),
        delete_application=OnCompleteAction.never(),
        clear_state=OnCompleteAction.never(),
    ),
)


@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """sum a and b, return the result"""
    return output.set(a.get() + b.get())


@router.method
def sub(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """subtract b from a, return the result"""
    return output.set(a.get() - b.get())


@router.method
def mul(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """multiply a and b, return the result"""
    return output.set(a.get() * b.get())


@router.method
def div(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """divide a by b, return the result"""
    return output.set(a.get() / b.get())


if __name__ == "__main__":
    import json
    import os

    path = os.path.dirname(os.path.abspath(__file__))
    approval, clear, contract = router.compile_program(version=6, optimize=OptimizeOptions(scratch_slots=True))

    # Dump out the contract as json that can be read in by any of the SDKs
    with open(os.path.join(path, "contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(clear)
