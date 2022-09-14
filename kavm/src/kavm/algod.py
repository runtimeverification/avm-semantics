import logging
import os
from base64 import b64encode
from pathlib import Path
from pprint import PrettyPrinter
from typing import Any, Dict, List, Optional

import msgpack
from algosdk import encoding
from algosdk.future.transaction import Transaction
from algosdk.v2client import algod
from pyk.kastManip import split_config_from

from kavm.adaptors.account import KAVMAccount, get_account
from kavm.adaptors.transaction import KAVMTransaction
from kavm.kavm import KAVM


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

    def __init__(self, algod_token: str, algod_address: str, faucet_address: Optional[str]) -> None:
        super().__init__(algod_token, algod_address)
        self.algodLogger = logging.getLogger(f'${__name__}.algodLogger')
        self.pretty_printer = PrettyPrinter(width=41, compact=True)
        self.set_log_level(logging.DEBUG)

        # Initialize KAVM, fetching the K definition dir from the environment
        definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
        if definition_dir is not None:
            self.kavm = KAVM(
                definition_dir=Path(definition_dir),
                faucet_address=faucet_address,
                logger=self.algodLogger,
            )
        else:
            self.algodLogger.critical('Cannot initialize KAVM: KAVM_DEFINITION_DIR env variable is not set')
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
            elif params[0] == 'pending':
                txid = int(params[1])
                return self.kavm._committed_txns[txid]
            else:
                raise NotImplementedError(f'Endpoint not implemented: {requrl}')
        elif endpoint == 'accounts':
            (config, subst) = split_config_from(self.kavm.current_config)

            address = params[0]
            return KAVMAccount.from_account_cell(get_account(address, subst['ACCOUNTSMAP_CELL'])).dictify()

        else:
            self.algodLogger.debug(requrl.split('/'))
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')

    def _pending_transaction_info(self, txid: int) -> Dict[str, Any]:
        """
        Fetch info about a pending transaction from KAVM

        Fow now, we return any transction as confirmed

        returns:
            PendingTransactionResponse https://github.com/algorand/go-algorand/tree/master/daemon/algod/api/algod.oas2.json#L2600

        """
        return {'confirmed-round': 1}

    def _handle_post_requests(self, requrl: str, data: Optional[bytes]) -> Dict[str, Any]:
        """
        Handle POST requests to algod with KAVM
        """
        # handle transaction group submission
        if requrl == '/transactions':
            assert data is not None, 'attempt to submit an empty transaction group!'
            # decode signed transactions from binary into py-algorand-sdk objects
            txns = [t.dictify()['txn'] for t in msgpack_decode_txn_list(data)]
            txn_msg = self.pretty_printer.pformat(txns)
            algod_debug_log_msg = f'POST {requrl} {txn_msg}'
            # log decoded transaction as submitted
            self.algodLogger.debug(algod_debug_log_msg)

            # we'll need tpo keep track of all addresses the transactions mention to
            # make KAVM aware of the new ones
            known_addresses = set()
            # kavm_txns will hold the KAst terms of the transactions
            kavm_txns = []
            # TODO: make txid more smart than just the counter
            for txid_offset, signed_txn in enumerate(msgpack_decode_txn_list(data)):
                known_addresses.add(signed_txn.transaction.sender)
                if hasattr(signed_txn.transaction, 'receiver'):
                    known_addresses.add(signed_txn.transaction.receiver)
                txid = self.kavm.next_valid_txid + txid_offset
                kavm_txn = KAVMTransaction(self.kavm, signed_txn.transaction, txid)
                self.algodLogger.debug(f'Submitting txn with id: {kavm_txn.txid}')
                kavm_txns.append(kavm_txn)

            return self.kavm.eval_transactions(kavm_txns, known_addresses)
        elif requrl == '/teal/compile':
            assert data is not None, 'attempt to compile an empty TEAL program!'
            # we do not actually compile therogram since KAVM needs the source code
            return {'result': b64encode(data)}
        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')
