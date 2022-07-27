from hashlib import sha256
from base64 import b64decode
from base64 import b64encode
from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import (
    PaymentTxn,
    ApplicationCreateTxn,
    ApplicationCallTxn,
    OnComplete,
    ApplicationOptInTxn,
    AssetCreateTxn,
    AssetTransferTxn,
    AssetOptInTxn
)
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
    AccountTransactionSigner
)
from algosdk.logic import get_application_address
from algosdk.future.transaction import wait_for_confirmation
from algosdk.encoding import encode_address

from pyteal import (
    compileTeal,
    Mode
)
import auction

from time import (
    time,
    sleep
)

INITIAL_BALANCE = 100_000_000
WAGER_AMOUNT = 2_000
CONTRACT_INITIAL_FUND = 100_000_000
CONTRACT_CREATOR_INITIAL_FUND = 10_000_000_000

BID1 = 1_000
BID2 = 5_000
BID3 = 3_000
BID4 = 6_000

PLAYER_1_SECRET = "abac"
PLAYER_2_SECRET = "defgh"

def params_nofee(algod):
    params = algod.suggested_params()
    params.fee = 0
    return params


def compile_pyteal():
    approval_file = open("tests/contracts/auction/auction.approval.teal", "w")
    approval_file.write(
        compileTeal(auction.auction(), mode=Mode.Application, version=6)
    )


def load_and_compile_teal(algod, filename_base):

    filename_approval = f'tests/contracts/auction/{filename_base}.approval.teal'
    filename_clear = f'tests/contracts/auction/{filename_base}.clear.teal'

    approval_file = open(filename_approval, "r")
    clear_file = open(filename_clear, "r")

    approval_code = approval_file.read()
    clear_code = clear_file.read()

    approval_pgm = algod.compile(approval_code)["result"]
    clear_pgm = algod.compile(clear_code)["result"]

    return (b64decode(approval_pgm), b64decode(clear_pgm))


def generate_and_fund_account(algod, faucet, amount):
    private_key, address = account.generate_account()

    # fund the account from the faucet
    algod.send_transaction(
        PaymentTxn(faucet["address"], algod.suggested_params(), address, amount).sign(
            faucet["private_key"]
        )
    )

    return {"address": address, "private_key": private_key}


def create_auction_contract(algod, faucet, creator_account):

    compile_pyteal()

    approval_pgm, clear_pgm = load_and_compile_teal(algod, "auction")

    global_schema = transaction.StateSchema(num_uints=4, num_byte_slices=1)
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    # Create the contract
    create_contract_txn = ApplicationCreateTxn(
        creator_account["address"],
        params_nofee(algod),
        OnComplete.NoOpOC,
        approval_pgm,
        clear_pgm,
        global_schema,
        local_schema
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(create_contract_txn, AccountTransactionSigner(creator_account["private_key"])))
    return group.execute(algod, 1000)

def fund_contract(
    algod,
    faucet,
    creator_account,
    app_address,
):
    # Fund the contract for inner transaction fees
    fund_txn = PaymentTxn(
        faucet["address"],
        algod.suggested_params(),
        app_address,
        CONTRACT_INITIAL_FUND
    )
    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(fund_txn, AccountTransactionSigner(faucet["private_key"])))
    return group.execute(algod, 1000)

def init_contract(
    algod,
    app_id,
    creator_account,
    begin_time,
    end_time
):
    # Call the contract telling it to create a unique asset for auction
    create_asset_txn = ApplicationCallTxn(
        creator_account["address"],
        params_nofee(algod),
        app_id,
        OnComplete.NoOpOC,

        app_args= [
            bytearray("create_asset", "ascii"),
            int(begin_time),
            int(end_time)
        ]
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(create_asset_txn, AccountTransactionSigner(creator_account["private_key"])))
    return group.execute(algod, 1000)

def list_to_dict(l):
    d = {}
    for item in l:
        d[b64decode(item["key"]).decode("ascii")] = item["value"]
    return d

def bid(
    algod,
    app_id,
    sender,
    amount
):
    app_global_state = list_to_dict(algod.application_info(app_id)["params"]["global-state"])

    current_highest_bidder = encode_address(b64decode(app_global_state["highest_bidder"]["bytes"]))

    txn = ApplicationCallTxn(
        sender["address"],
        params_nofee(algod),
        app_id,
        OnComplete.NoOpOC,

        app_args = [
            bytearray("bid", "ascii"),
        ],

        accounts = [
            sender["address"],
            current_highest_bidder
        ]
    )

    app_address = get_application_address(app_id)

    pay_txn = PaymentTxn(
        sender["address"],
        params_nofee(algod),
        app_address,
        amount
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(txn, AccountTransactionSigner(sender["private_key"])))
    group.add_transaction(TransactionWithSigner(pay_txn, AccountTransactionSigner(sender["private_key"])))
    return group.execute(algod, 1000)

def redeem(
    algod,
    app_id,
    sender,
    asset_id
):
    txn = ApplicationCallTxn(
        sender["address"],
        params_nofee(algod),
        app_id,
        OnComplete.NoOpOC,

        app_args = [
            bytearray("redeem", "ascii")
        ],

        foreign_assets = [
            asset_id
        ]
    )

    opt_in_txn = AssetOptInTxn(
        sender["address"],
        params_nofee(algod),
        asset_id
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(opt_in_txn, AccountTransactionSigner(sender["private_key"])))
    group.add_transaction(TransactionWithSigner(txn, AccountTransactionSigner(sender["private_key"])))
    return group.execute(algod, 1000)

def compute_total_fee(algod, result):
    sum = 0
    for id in result.tx_ids:
        sum += algod.pending_transaction_info(id)["txn"]["txn"]["fee"]
    return sum

def compute_contract_fee(algod, result):
    sum = 0
    for id in result.tx_ids:
        if algod.pending_transaction_info(id).get("inner-txns") != None:
            for inner_txn in algod.pending_transaction_info(id)["inner-txns"]:
                sum += inner_txn["txn"]["txn"]["fee"]
    return sum


def test_auction(algod, faucet):

    assert(BID1 < BID2)
    assert(BID3 < BID2)
    assert(BID4 > BID2)

    # Create account for contract creator
    creator_account = generate_and_fund_account(algod, faucet, CONTRACT_CREATOR_INITIAL_FUND)

    result = create_auction_contract(algod, faucet, creator_account)

    app_id = algod.pending_transaction_info(result.tx_ids[0])["application-index"]

    app_address = get_application_address(app_id)
    fund_contract(algod, faucet, creator_account, app_address)

    current_time = int(time())
    result = init_contract(algod, app_id, creator_account, current_time, current_time + 10)
    contract_fee = compute_contract_fee(algod, result)

    player1_account = generate_and_fund_account(algod, faucet, INITIAL_BALANCE)
    player2_account = generate_and_fund_account(algod, faucet, INITIAL_BALANCE)

    assert(algod.account_info(app_address)["amount"] == CONTRACT_INITIAL_FUND - contract_fee)

    print(creator_account["address"])
    print(player1_account["address"])
    print(player2_account["address"])

    result = bid(
        algod,
        app_id,
        sender=player1_account,
        amount=BID1
    )
    player1_fee = compute_total_fee(algod, result)
    contract_fee += compute_contract_fee(algod, result)

    assert(algod.account_info(player1_account["address"])["amount"] == INITIAL_BALANCE - player1_fee - BID1)
    assert(algod.account_info(app_address)["amount"] == CONTRACT_INITIAL_FUND - contract_fee + BID1)

    result = bid(
        algod,
        app_id,
        sender=player2_account,
        amount=BID2
    )
    player2_fee = compute_total_fee(algod, result)
    contract_fee += compute_contract_fee(algod, result)

    assert(algod.account_info(player1_account["address"])["amount"] == INITIAL_BALANCE - player1_fee)
    assert(algod.account_info(player2_account["address"])["amount"] == INITIAL_BALANCE - player2_fee - BID2)
    assert(algod.account_info(app_address)["amount"] == CONTRACT_INITIAL_FUND - contract_fee + BID2)

    try:
        result = bid(
            algod,
            app_id,
            sender=player1_account,
            amount=BID3
        )
    except:
        ...
    else:
        assert False, "transaction should fail due to insufficiently high bid."

    sleep(15)

    app_global_state = list_to_dict(algod.application_info(app_id)["params"]["global-state"])
    print(app_global_state)

#    try:
#        result = bid(
#            algod,
#            app_id,
#            sender=player1_account,
#            amount=BID4
#        )
#        print(algod.pending_transaction_info(result.tx_ids[0]))
#    except:
#        ...
#    else:
#        assert False, "transaction should fail due to auction closed."

    asset_id = algod.account_info(app_address)["assets"][0]["asset-id"]

    try:
        redeem(
            algod,
            app_id,
            sender=player1_account,
            asset_id=asset_id
        )
    except:
        ...
    else:
        assert False, "transaction should fail because player 1 didn't win."

    result = redeem(
        algod,
        app_id,
        sender=player2_account,
        asset_id=asset_id
    )
    player2_fee += compute_total_fee(algod, result)
    contract_fee += compute_contract_fee(algod, result)

    assert(algod.account_info(player1_account["address"])["amount"] == INITIAL_BALANCE - player1_fee)
    assert(algod.account_info(player2_account["address"])["amount"] == INITIAL_BALANCE - player2_fee - BID2)
    assert(algod.account_info(app_address)["amount"] == CONTRACT_INITIAL_FUND - contract_fee + BID2)
