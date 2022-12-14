from typing import Tuple

from algosdk.abi import Contract
from pyteal import (Approve, BareCallActions, Expr, OnCompleteAction, Router, abi, InnerTxnBuilder, Int,
        Extract, InnerTxn, Seq, Btoi)
from pyteal.compiler.optimizer import optimizer

# Main router class
router = Router(
    # Name of the contract
    name="call_calculator",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction.never(),
        delete_application=OnCompleteAction.never(),
        clear_state=OnCompleteAction.never(),
    ),
)


@router.method
def add(app: abi.Application, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """sum a and b, return the result"""
    return output.set(
        Seq([
            InnerTxnBuilder.ExecuteMethodCall(
                app_id=app.application_id(),
                method_signature="add(uint64,uint64)uint64",
                args=[a, b],
            ),
            Btoi(Extract(InnerTxn.last_log(), Int(4), Int(8)))
        ])
    )


@router.method
def sub(app: abi.Application, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """subtract b from a, return the result"""
    return output.set(
        Seq([
            InnerTxnBuilder.ExecuteMethodCall(
                app_id=app.application_id(),
                method_signature="sub(uint64,uint64)uint64",
                args=[a, b],
            ),
            Btoi(Extract(InnerTxn.last_log(), Int(4), Int(8)))
        ])
    )


@router.method
def mul(app: abi.Application, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """multiply a and b, return the result"""
    return output.set(
        Seq([
            InnerTxnBuilder.ExecuteMethodCall(
                app_id=app.application_id(),
                method_signature="mul(uint64,uint64)uint64",
                args=[a, b],
            ),
            Btoi(Extract(InnerTxn.last_log(), Int(4), Int(8)))
        ])
    )


@router.method
def div(app: abi.Application, a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """divide a by b, return the result"""
    return output.set(
        Seq([
            InnerTxnBuilder.ExecuteMethodCall(
                app_id=app.application_id(),
                method_signature="div(uint64,uint64)uint64",
                args=[a, b],
            ),
            Btoi(Extract(InnerTxn.last_log(), Int(4), Int(8)))
        ])
    )


def compile_to_teal() -> Tuple[str, str, Contract]:
    """Compile approval and clear programs, and generate the contract description object"""
    approval, clear, contract = router.compile_program(
        version=6, optimize=optimizer.OptimizeOptions(scratch_slots=True)
    )
    return approval, clear, contract
