import logging
from pprint import PrettyPrinter
from typing import Any, List, Dict

import msgpack
from algosdk import encoding
from algosdk.v2client import algod
from algosdk.future.transaction import Transaction


def msgpack_decode_txn_list(enc: bytes) -> list[Transaction]:
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.algodLogger = logging.getLogger(f'${__name__}.algodLogger')
        self.pretty_printer = PrettyPrinter(width=41, compact=True)
        self.set_log_level(logging.DEBUG)

        # Initialize KAVM here

    def set_log_level(self, log_level: Any) -> None:
        """
        Set log level for algod requests
        """
        self.algodLogger.setLevel(log_level)

    def algod_request(
        self,
        method: str,
        requrl: str,
        params: list[str] = None,
        data: bytes = None,
        headers: list[str] = None,
        response_format: str = 'Json',
    ) -> dict[str, Any]:
        """
        Log requests made to algod, but execute local actions instead

        Need to override this method, and the more specific methods using it can remain the same.
        """
        txn_msg = ''

        if data is not None:
            txns = map(lambda t: t.dictify()['txn'], msgpack_decode_txn_list(data))
            txn_msg = self.pretty_printer.pformat(list(txns))
        algod_debug_log_msg = f'{method} {requrl} {txn_msg}'
        self.algodLogger.debug(algod_debug_log_msg)

        if method == 'GET':
            return self._handle_get_requests(requrl)
        elif method == 'POST':
            return self._handle_post_requests(requrl)
        else:
            raise NotImplementedError(f'{method} {requrl}')

    def _handle_get_requests(self, requrl: str) -> dict[str, Any]:
        """
        Handle GET requests to algod with PyTeal_eval
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

    def _handle_post_requests(self, requrl: str) -> dict[str, Any]:
        """
        Handle POST requests to algod with PyTeal_eval
        """
        if requrl == '/transactions':
            return dict({'txId': -1})
        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')
