from algosdk.kmd import KMDClient

KMD_ADDRESS = "http://localhost:4002"
KMD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

KMD_WALLET_NAME = "unencrypted-default-wallet"
KMD_WALLET_PASSWORD = ""


def get_accounts():
    kmd = KMDClient(KMD_TOKEN, KMD_ADDRESS)
    wallets = kmd.list_wallets()

    wallet_id = None
    for wallet in wallets:
        if wallet["name"] == KMD_WALLET_NAME:
            wallet_id = wallet["id"]
            break

    if wallet_id is None:
        raise Exception("Wallet not found: {}".format(KMD_WALLET_NAME))

    wallet_handle = kmd.init_wallet_handle(wallet_id, KMD_WALLET_PASSWORD)

    try:
        addresses = kmd.list_keys(wallet_handle)
        private_keys = [kmd.export_key(wallet_handle, KMD_WALLET_PASSWORD, addr) for addr in addresses]
        kmd_accounts = [(addresses[i], private_keys[i]) for i in range(len(private_keys))]
    finally:
        kmd.release_wallet_handle(wallet_handle)

    return kmd_accounts
