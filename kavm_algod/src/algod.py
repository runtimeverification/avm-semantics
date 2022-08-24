import os
import json
import logging
import tempfile
from pathlib import Path
from pprint import PrettyPrinter
from typing import Any, Dict, List

import msgpack
from algosdk import encoding
from algosdk.future.transaction import Transaction
from algosdk.v2client import algod
from pyk.kast import KApply, KSort, KLabel, KAst
from pyk.kastManip import minimize_term
from pyk.prelude import stringToken, intToken

from kavm_algod.kavm import KAVM
from kavm_algod.adaptors.transaction import KAVMTransaction
from kavm_algod.adaptors.account import KAVMAccount


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
        data: bytes = None,
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
        if requrl == '/transactions':
            return dict({'txId': -1})
        elif requrl == '/transactions/params':
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
        raise NotImplementedError(requrl.split())

    def _handle_post_requests(self, requrl: str, data: bytes) -> Dict[str, Any]:
        """
        Handle POST requests to algod with KAVM
        """
        # handle transaction group submission
        # TODO: separate into a function
        if requrl == '/transactions':
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
            # TODO: don't fund them here! they must be explicitly funded from a faucet
            accounts = [KAVMAccount(address, 1_000_000) for address in known_addresses]

            # construct the KAVM configuration and run it via krun
            (krun_return_code, output) = self.kavm.run_term(
                self.kavm.simulation_config(accounts, kavm_txns)
            )
            if isinstance(output, KAst):
                self.algodLogger.debug(self.kavm.pretty_print(output))
                # TODO: set the new current configuration KAVM
            else:
                self.algodLogger.debug(output)
                exit(krun_return_code)

            return {'txId': -1}

        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')
