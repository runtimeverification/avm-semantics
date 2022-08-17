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
from kavm_algod.adaptors.transaction import transaction_to_k


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
        if requrl == '/transactions':
            txns = list(
                map(lambda t: t.dictify()['txn'], msgpack_decode_txn_list(data))
            )
            txn_msg = self.pretty_printer.pformat(txns)
            algod_debug_log_msg = f'POST {requrl} {txn_msg}'
            # self.algodLogger.debug(algod_debug_log_msg)
            avm_simulation_term_str = ''

            known_addresses = set()

            txns_cells = []
            for txid, signed_txn in enumerate(msgpack_decode_txn_list(data)):
                # txid = signed_txn.transaction.get_txid()
                known_addresses.add(signed_txn.transaction.sender)
                known_addresses.add(signed_txn.transaction.receiver)
                kavm_txn = transaction_to_k(self.kavm, signed_txn.transaction, txid)
                # kavm_submit_txn = KApply('submit', [kavm_txn])
                # # self.algodLogger.debug(self.kavm.pretty_print(kavm_submit_txn))
                # avm_simulation_term = KApply(
                #     '_;__', [kavm_submit_txn, avm_simulation_term]
                # )
                # kavm_submit_txn_str = f'submit {self.kavm.pretty_print(kavm_txn)};'
                # avm_simulation_term_str += kavm_submit_txn_str
                txns_cells.append(kavm_txn)

            # avm_simulation_term_str += '#initGlobals();'
            # avm_simulation_term_str += '#evalTxGroup();'
            # avm_simulation_term_str += '.AS'

            accounts = []
            for address in known_addresses:
                accounts.append(self.kavm.account(address))

            # print(
            #     self.kavm.pretty_print(
            #         self.kavm.simulation_config(accounts, txns_cells)
            #     )
            # )
            (krun_return_code, output) = self.kavm.run_term(
                self.kavm.simulation_config(accounts, txns_cells)
            )
            if isinstance(output, KAst):
                self.algodLogger.debug(self.kavm.pretty_print(output))
            else:
                self.algodLogger.debug(output)
            exit(krun_return_code)

        #         avm_simulation_term_str = (
        #             f'addAccount <address> b"{address}" </address> <balance> 1500000 </balance>;'
        #             "" + avm_simulation_term_str
        #         )

        #     with tempfile.NamedTemporaryFile('w+t') as tmp_file:
        #         tmp_file.write(avm_simulation_term_str)
        #         tmp_file.seek(0)

        #         self.kavm.run_with_current_config()
        #         # (krun_return_code, output) = self.kavm.run(Path(tmp_file.name))
        #         # if isinstance(output, KAst):
        #         #     self.algodLogger.debug(self.kavm.pretty_print(output))
        #         # else:
        #         #     self.algodLogger.debug(output)
        #         # exit(krun_return_code)

        #     return dict({'txId': -1})
        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')
