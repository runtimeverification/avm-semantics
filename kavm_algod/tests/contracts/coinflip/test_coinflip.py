from hashlib import sha256
from base64 import b64decode
from algosdk import account
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn
from algosdk.future.transaction import ApplicationCreateTxn
from algosdk.future.transaction import ApplicationCallTxn
from algosdk.future.transaction import OnComplete
from algosdk.future.transaction import ApplicationOptInTxn
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk.logic import get_application_address

INITIAL_BALANCE = 100_000_000
WAGER_AMOUNT = 2_000
CONTRACT_INITIAL_FUND = 100_000_000
CONTRACT_CREATOR_INITIAL_FUND = 10_000_000_000

PLAYER_1_SECRET = "abac"
PLAYER_2_SECRET = "defgh"

def load_and_compile_teal(algod, filename_base):

    filename_approval = f'tests/contracts/algosdk_test/{filename_base}.approval.teal'
    filename_clear = f'tests/contracts/algosdk_test/{filename_base}.clear.teal'

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
    sp = algod.suggested_params()
    algod.send_transaction(
        PaymentTxn(faucet["address"], sp, address, amount).sign(
            faucet["private_key"]
        )
    )

    return {"address": address, "private_key": private_key}


def create_coinflip_contract(algod, faucet):
    creator_account = generate_and_fund_account(algod, faucet, CONTRACT_CREATOR_INITIAL_FUND)

    approval_pgm, clear_pgm = load_and_compile_teal(algod, "coinflip")

    global_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    local_schema = transaction.StateSchema(num_uints=1, num_byte_slices=2)

    create_contract_txn = ApplicationCreateTxn(
        creator_account["address"],
        algod.suggested_params(),
        OnComplete.NoOpOC,
        approval_pgm,
        clear_pgm,
        global_schema,
        local_schema
    )

    signed_create_txn = create_contract_txn.sign(creator_account["private_key"])

    create_txn_id = algod.send_transaction(signed_create_txn)
    created_app_id = algod.pending_transaction_info(create_txn_id)["application-index"]

    app_address = get_application_address(created_app_id)

    sp = algod.suggested_params()
    algod.send_transaction(
        PaymentTxn(faucet["address"], sp, app_address, CONTRACT_INITIAL_FUND).sign(
            faucet["private_key"]
        )
    )

    return created_app_id


def compute_total_fee(algod, tx_ids):
    sum = 0
    for id in tx_ids:
        sum += algod.pending_transaction_info(id)["txn"]["txn"]["fee"]
    return sum

def issue_challenge(
    algod,
    app_id,
    sender,
    opponent,
    amount,
    secret_hash
):

    txn = ApplicationOptInTxn(
        sender["address"],
        algod.suggested_params(),
        app_id,

        app_args= [
            bytearray("init", "ascii"),
            secret_hash
        ],

        accounts= [
            sender["address"],
            opponent["address"]
        ]
    )

    app_address = get_application_address(app_id)

    pay_txn = PaymentTxn(
        sender["address"],
        algod.suggested_params(),
        app_address,
        amount
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(txn, AccountTransactionSigner(sender["private_key"])))
    group.add_transaction(TransactionWithSigner(pay_txn, AccountTransactionSigner(sender["private_key"])))
    return group.execute(algod, 1000)


def respond(
    algod,
    app_id,
    sender,
    opponent,
    amount,
    secret
):
    txn = ApplicationOptInTxn(
        sender["address"],
        algod.suggested_params(),
        app_id,

        app_args = [
            bytearray("respond", "ascii"),
            secret
        ],

        accounts = [
            sender["address"],
            opponent["address"]
        ]
    )

    app_address = get_application_address(app_id)

    pay_txn = PaymentTxn(
        sender["address"],
        algod.suggested_params(),
        app_address,
        amount
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(txn, AccountTransactionSigner(sender["private_key"])))
    group.add_transaction(TransactionWithSigner(pay_txn, AccountTransactionSigner(sender["private_key"])))
    return group.execute(algod, 1000)


def reveal(
    algod,
    app_id,
    sender,
    opponent,
    secret
):
    txn = ApplicationCallTxn(
        sender["address"],
        algod.suggested_params(),
        app_id,
        OnComplete.NoOpOC,

        app_args = [
            bytearray("reveal", "ascii"),
            secret
        ],

        accounts = [
            sender["address"],
            opponent["address"]
        ]
    )

    group = AtomicTransactionComposer()
    group.add_transaction(TransactionWithSigner(txn, AccountTransactionSigner(sender["private_key"])))
    return group.execute(algod, 1000)

def test_coinflip(algod, faucet):

    app_id = create_coinflip_contract(algod, faucet)

    player1_account = generate_and_fund_account(algod, faucet, INITIAL_BALANCE)
    player2_account = generate_and_fund_account(algod, faucet, INITIAL_BALANCE)

    challenge_result = issue_challenge(
        algod,
        app_id=app_id,
        sender=player1_account,
        opponent=player2_account,
        amount=WAGER_AMOUNT,
        secret_hash=sha256(bytes(PLAYER_1_SECRET, "ascii")).digest()
    )

    p1_info = algod.account_info(player1_account["address"])
    p1_balance = p1_info["amount"]
    p1_total_fee = compute_total_fee(algod, challenge_result.tx_ids)
    contract_balance = algod.account_info(get_application_address(app_id))["amount"]

    assert(INITIAL_BALANCE - p1_total_fee - WAGER_AMOUNT == p1_balance)
    assert(CONTRACT_INITIAL_FUND + WAGER_AMOUNT == contract_balance)

    respond_result = respond(
        algod,
        app_id=app_id,
        sender=player2_account,
        opponent=player1_account,
        amount=WAGER_AMOUNT,
        secret=bytearray(PLAYER_2_SECRET, "ascii")
    )

    p2_info = algod.account_info(player2_account["address"])
    p2_balance = p2_info["amount"]
    p2_total_fee = compute_total_fee(algod, respond_result.tx_ids)
    contract_balance = algod.account_info(get_application_address(app_id))["amount"]

    assert(INITIAL_BALANCE - p2_total_fee - WAGER_AMOUNT == p2_balance)
    assert(CONTRACT_INITIAL_FUND + WAGER_AMOUNT + WAGER_AMOUNT == contract_balance)


    reveal_result = reveal(
        algod,
        app_id=app_id,
        sender=player1_account,
        opponent=player2_account,
        secret=bytearray(PLAYER_1_SECRET, "ascii")
    )

    p1_info = algod.account_info(player1_account["address"])
    p2_info = algod.account_info(player2_account["address"])
    p1_balance = p1_info["amount"]
    p2_balance = p2_info["amount"]
    p1_total_fee += compute_total_fee(algod, reveal_result.tx_ids)
    contract_balance = algod.account_info(get_application_address(app_id))["amount"]
    inner_tx_fee = algod.pending_transaction_info(reveal_result.tx_ids[0])["inner-txns"][0]["txn"]["txn"]["fee"]

    concat_hash = sha256(bytes(PLAYER_1_SECRET + PLAYER_2_SECRET, "ascii")).digest().hex()
    print(concat_hash)

    if int(concat_hash, 16) & 1 == 0:
        assert(INITIAL_BALANCE - p1_total_fee + WAGER_AMOUNT == p1_balance)
        assert(INITIAL_BALANCE - p2_total_fee - WAGER_AMOUNT == p2_balance)
    elif int(concat_hash, 16) & 1 == 1:
        assert(INITIAL_BALANCE - p1_total_fee + WAGER_AMOUNT == p1_balance)
        assert(INITIAL_BALANCE - p2_total_fee - WAGER_AMOUNT == p2_balance)

    assert(CONTRACT_INITIAL_FUND - inner_tx_fee == contract_balance)
