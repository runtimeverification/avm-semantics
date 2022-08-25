import logging
import os
from pprint import PrettyPrinter
from typing import Any, Dict, List, Optional

import msgpack
from algosdk import encoding
from algosdk.future.transaction import Transaction
from algosdk.v2client import algod
from kavm_algod.adaptors.account import KAVMAccount, get_account
from kavm_algod.adaptors.transaction import KAVMTransaction
from kavm_algod.kavm import KAVM
from pyk.kast import KAst
from pyk.kastManip import splitConfigFrom


def msgpack_decode_txn_list(enc: bytes) -> List[Transaction]:
    """
    Decode a msgpack encoded object from a string.
    Args:
        enc (str): string to be decoded
    Returns:
        []Transaction, []SignedTransaction, []Multisig, []Bid, or []SignedBid:\
            decoded object

    Note: This is the missing list decoder from py-algorand-sdk
    """
    unpacker = msgpack.Unpacker()
    unpacker.feed(enc)
    deserialized = []
    while unpacker.tell() < len(enc):
        decoded = encoding.future_msgpack_decode(unpacker.unpack())
        deserialized.append(decoded)
    return deserialized


class KAVMClient(algod.AlgodClient):
    """
    Mock class for algod. Forwards all requests to KAVM

    Instead of establishing a connection with algod:
    * initialize KAVM,
    * pretend it is algod.
    """

    def __init__(self, algod_token: str, algod_address: str) -> None:
        super().__init__(algod_token, algod_address)
        self.algodLogger = logging.getLogger(f'${__name__}.algodLogger')
        self.pretty_printer = PrettyPrinter(width=41, compact=True)
        self.set_log_level(logging.DEBUG)

        self.accounts: Dict[str, KAVMAccount] = {}

        # Initialize KAVM, fetching the K definition dir from the environment
        try:
            self.kavm = KAVM(definition_dir=os.environ.get('KAVM_DEFINITION_DIR'))
        except KeyError:
            self.algodLogger.critical(
                'Cannot initialize KAVM: KAVM_DEFINITION_DIR env variable is not set'
            )
            exit(1)

    def set_log_level(self, log_level: Any) -> None:
        """
        Set log level for algod requests
        """
        self.algodLogger.setLevel(log_level)

    def algod_request(
        self,
        method: str,
        requrl: str,
        params: List[str] = None,
        data: Optional[bytes] = None,
        headers: List[str] = None,
        response_format: str = 'Json',
    ) -> Dict[str, Any]:
        """
        Log requests made to algod, but execute local actions instead

        Need to override this method, and the more specific methods using it can remain the same.
        """

        if method == 'GET':
            return self._handle_get_requests(requrl)
        elif method == 'POST':
            return self._handle_post_requests(requrl, data)
        else:
            raise NotImplementedError(f'{method} {requrl}')

    def _handle_get_requests(self, requrl: str) -> Dict[str, Any]:
        """
        Handle GET requests to algod with KAVM
        """
        _, endpoint, *params = requrl.split('/')

        if endpoint == 'transactions':
            if len(params) == 0:
                return dict({'txId': -1})
            if params[0] == 'params':
                return {
                    'consensus-version': 31,
                    'fee': 1000,
                    'genesis-id': 'pyteal-eval',
                    'genesis-hash': 'pyteal-evalpyteal-evalpyteal-evalpyteal-eval',
                    'last-round': 1,
                    'min-fee': 1000,
                }
            else:
                raise NotImplementedError(f'Endpoint not implemented: {requrl}')
        elif endpoint == 'accounts':
            (config, subst) = splitConfigFrom(self.kavm.current_config)
            address = params[0]
            return KAVMAccount.from_account_cell(
                get_account(address, subst['ACCOUNTSMAP_CELL'])
            ).dictify()

        else:
            self.algodLogger.debug(requrl.split('/'))
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')

    def _handle_post_requests(
        self, requrl: str, data: Optional[bytes]
    ) -> Dict[str, Any]:
        """
        Handle POST requests to algod with KAVM
        """
        # handle transaction group submission
        # TODO: separate into a function
        if requrl == '/transactions':
            assert data is not None, 'attempt to submit an empty transaction group!'
            # decode signed transactions from binary into py-algorand-sdk objects
            txns = list(
                map(lambda t: t.dictify()['txn'], msgpack_decode_txn_list(data))
            )
            txn_msg = self.pretty_printer.pformat(txns)
            algod_debug_log_msg = f'POST {requrl} {txn_msg}'
            # log decoded transaction as submitted
            self.algodLogger.debug(algod_debug_log_msg)

            # we'll need tpo keep track pf all addresses the transactions mention to
            # make KAVM aware of them
            # TODO: probably need to store them in the KAVM instance
            known_addresses = set()
            # kavm_txns will hold the KAst terms of the transactions
            kavm_txns = []
            # TODO: make txid more smart than just the counter
            for txid, signed_txn in enumerate(msgpack_decode_txn_list(data)):
                known_addresses.add(signed_txn.transaction.sender)
                known_addresses.add(signed_txn.transaction.receiver)
                kavm_txns.append(
                    KAVMTransaction(self.kavm, signed_txn.transaction, txid)
                )

            # construct account cells from the discovered addresses
            accounts = {address: KAVMAccount(address) for address in known_addresses}
            # TODO: handle faucet in a less ad-hoc way, in the KAVM class
            if self.kavm.faucet.address in accounts.keys():
                accounts[self.kavm.faucet.address] = KAVMAccount(
                    self.kavm.faucet.address, 1_000_000_000
                )

            # print(
            #     self.kavm.pretty_print(
            #         self.kavm.simulation_config(accounts.values(), kavm_txns)
            #     )
            # )
            # assert False

            # construct the KAVM configuration and run it via krun
            (krun_return_code, output) = self.kavm.run_term(
                self.kavm.simulation_config(accounts.values(), kavm_txns)
            )
            if isinstance(output, KAst) and krun_return_code == 0:
                # commit the new configuration
                self.kavm.current_config = output
            else:
                # something went wrong: show the last configuration as a pretty term
                self.algodLogger.critical(self.kavm.pretty_print(output))
                exit(krun_return_code)

            return {'txId': -1}

        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')
