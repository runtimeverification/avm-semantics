from typing import Tuple

from algosdk.abi import Contract
from pyteal import (
    App,
    Approve,
    Assert,
    BareCallActions,
    Bytes,
    Div,
    Expr,
    Global,
    InnerTxn,
    InnerTxnBuilder,
    Int,
    Mul,
    OnCompleteAction,
    Router,
    Seq,
    Subroutine,
    TealType,
    Txn,
    TxnField,
    TxnType,
    abi,
)
from pyteal.compiler.optimizer import optimizer

ASSET_TOTAL = 1000000
ASSET_DECIMALS = 3
INITIAL_EXCHANGE_RATE = 2
WRONG_SCALING_FACTOR = Int(10)
SCALING_FACTOR = Int(100)

# The PyTeal router
router = Router(
    name="K Coin Vault",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction.never(),
        delete_application=OnCompleteAction.never(),
        clear_state=OnCompleteAction.never(),
    ),
)


@router.method
def init_asset(*, output: abi.Uint64) -> Expr:
    """
    Create the K Coin asset

    Can only be executed by the contract's creator

    Returns: created asset id

    """
    return Seq(
        Assert(Txn.sender() == Global.creator_address()),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: Int(ASSET_TOTAL),
                TxnField.config_asset_decimals: Int(ASSET_DECIMALS),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
                TxnField.config_asset_name: Bytes("K Coin"),
                TxnField.config_asset_unit_name: Bytes("microK"),
            }
        ),
        InnerTxnBuilder.Submit(),
        App.globalPut(Bytes("asset_id"), InnerTxn.created_asset_id()),
        App.globalPut(Bytes("exchange_rate"), Int(INITIAL_EXCHANGE_RATE)),
        output.set(InnerTxn.created_asset_id()),
    )


@Subroutine(TealType.uint64)
def algos_to_kcoin(algo_amount: Expr) -> Expr:
    """Convert microalgos to microKs"""
    return Div(algo_amount, App.globalGet(Bytes("exchange_rate")))


@Subroutine(TealType.uint64)
def kcoin_to_algos(asset_amount: Expr) -> Expr:
    """Convert microKs to microalgos"""
    return Mul(asset_amount, App.globalGet(Bytes("exchange_rate")))


@router.method
def mint(payment: abi.PaymentTransaction, *, output: abi.Uint64) -> Expr:
    """
    Mint K Coins, issuing an inner asset transfer transaction to sender if successful

    Args:
        payment: A payment transaction containing the amount of Algos the user wishes to mint with.
            The receiver of this transaction must be this app's escrow account.

    Returns: minted amount of K Coins that the user gets
    """
    amount_to_mint = algos_to_kcoin(payment.get().amount())
    asset_id = App.globalGet(Bytes("asset_id"))
    return Seq(
        Assert(payment.get().receiver() == Global.current_application_address()),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: amount_to_mint,
                TxnField.fee: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
        output.set(amount_to_mint),
    )


@router.method
def burn(asset_transfer: abi.AssetTransferTransaction, *, output: abi.Uint64) -> Expr:
    """
    Burn K Coins, issuing an inner payment transaction to sender if successful

    Args:
        asset_transfer: An asset transfer transaction containing the amount of K Coins (in microKs) the user wishes to burn.
            The receiver of this transaction must be this app's escrow account.

    Returns: amount of microalgos the users gets
    """
    microalgos_output = kcoin_to_algos(asset_transfer.get().asset_amount())
    return Seq(
        Assert(asset_transfer.get().asset_receiver() == Global.current_application_address()),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: microalgos_output,
                TxnField.fee: Int(0),
            }
        ),
        InnerTxnBuilder.Submit(),
        output.set(microalgos_output),
    )


def compile_to_teal() -> Tuple[str, str, Contract]:
    """Compile approval and clear programs, and generate the contract description object"""
    approval, clear, contract = router.compile_program(
        version=6, optimize=optimizer.OptimizeOptions(scratch_slots=True)
    )
    return approval, clear, contract
