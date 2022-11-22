# type: ignore

# flake8: noqa

import logging
import sys

from client import call_burn, call_mint, initial_state

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.ERROR, stream=sys.stdout)

    client, contract, app_id, creator_addr, creator_private_key, asset_id = initial_state()

    microalgos = 100
    minted = call_mint(client, contract, app_id, creator_addr, creator_private_key, asset_id, microalgos)
    print(f"Calling 'mint' with {microalgos} microalgos => {minted}")
    got_back = call_burn(client, contract, app_id, creator_addr, creator_private_key, asset_id, minted)
    print(f"Calling 'burn' with {minted} items => {got_back} microalgos")
