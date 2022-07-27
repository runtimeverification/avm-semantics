from pyteal import *

@Subroutine(TealType.none)
def init():
    return Approve()

@Subroutine(TealType.none)
def create_asset():

    return Seq(

        Assert(Txn.application_args.length() == Int(3)),

        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetConfig,
            TxnField.config_asset_total: Int(1),
            TxnField.config_asset_decimals: Int(0),
            TxnField.config_asset_unit_name: Bytes("assets"),
            TxnField.config_asset_name: Bytes("my_asset"),
        }),
        InnerTxnBuilder.Submit(),

        App.globalPut(Bytes("start_time"), Btoi(Txn.application_args[1])),
        App.globalPut(Bytes("end_time"), Btoi(Txn.application_args[2])),
        App.globalPut(Bytes("asset_id"), InnerTxn.created_asset_id()),
        App.globalPut(Bytes("highest_bidder"), Txn.sender()),
        App.globalPut(Bytes("highest_bid"), Int(0)),

        Approve()

    )


@Subroutine(TealType.none)
def bid():
    return Seq(
        Assert(Txn.application_args.length() == Int(1)),
        Assert(Global.group_size() == Int(2)),
        Assert(Txn.group_index() == Int(0)),
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].receiver() == Global.current_application_address()),
        Assert(Gtxn[1].amount() > App.globalGet(Bytes("highest_bid"))),
        Assert(Global.latest_timestamp() <= App.globalGet(Bytes("end_time"))),

        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: App.globalGet(Bytes("highest_bid")),
            TxnField.receiver: App.globalGet(Bytes("highest_bidder"))
        }),
        InnerTxnBuilder.Submit(),

        App.globalPut(Bytes("highest_bidder"), Txn.sender()),
        App.globalPut(Bytes("highest_bid"), Gtxn[1].amount()),

        Approve()
    )


@Subroutine(TealType.none)
def redeem():
    return Seq(
        Assert(Txn.application_args.length() == Int(1)),
        Assert(Global.group_size() == Int(2)),
        Assert(Txn.group_index() == Int(1)),
        Assert(Gtxn[0].type_enum() == TxnType.AssetTransfer),
        Assert(Gtxn[0].asset_receiver() == Txn.sender()),
        Assert(Gtxn[0].asset_amount() == Int(0)),
        Assert(Gtxn[0].sender() == Txn.sender()),
        Assert(App.globalGet(Bytes("highest_bidder")) == Txn.sender()),

        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_amount: Int(1),
            TxnField.asset_receiver: Txn.sender(),
            TxnField.xfer_asset: App.globalGet(Bytes("asset_id")),
        }),
        InnerTxnBuilder.Submit(),

        Approve()
    )


def auction():
    return Seq(
        Cond(
            [Txn.application_id() == Int(0), init()],
            [Txn.application_args[0] == Bytes("create_asset"), create_asset()],
            [Txn.application_args[0] == Bytes("bid"), bid()],
            [Txn.application_args[0] == Bytes("redeem"), redeem()]
        ),
        Reject()
    )

