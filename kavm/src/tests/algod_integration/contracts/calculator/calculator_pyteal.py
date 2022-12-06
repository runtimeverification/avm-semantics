from typing import Tuple

from algosdk.abi import Contract
from pyteal import Approve, BareCallActions, Expr, OnCompleteAction, Router, abi
from pyteal.compiler.optimizer import optimizer

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


def compile_to_teal() -> Tuple[str, str, Contract]:
    """Compile approval and clear programs, and generate the contract description object"""
    approval, clear, contract = router.compile_program(
        version=6, optimize=optimizer.OptimizeOptions(scratch_slots=True)
    )
    return approval, clear, contract
