import logging
import os
from base64 import b64encode
from pathlib import Path
from pprint import PrettyPrinter
from subprocess import CalledProcessError
from typing import Any, Dict, List, Optional, Iterable
import json
import tempfile

import msgpack
from algosdk import encoding
from algosdk.future.transaction import Transaction
from algosdk.v2client import algod

from pyk.kastManip import split_config_from
from pyk.kore.parser import KoreParser

# from kavm.adaptors.transaction import KAVMTransaction
from kavm import constants
from kavm.adaptors.algod_transaction import KAVMTransaction
from kavm.adaptors.algod_account import KAVMAccount
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

    def __init__(self, algod_token: str, algod_address: str, faucet_address: str) -> None:
        super().__init__(algod_token, algod_address)
        self.algodLogger = logging.getLogger(f'${__name__}.algodLogger')
        self.pretty_printer = PrettyPrinter(width=41, compact=True)
        self.set_log_level(logging.DEBUG)

        # self._apps = AppCellMap()
        self._committed_txns: Dict[str, Dict[str, Any]] = {}
        self._faucet_address = faucet_address
        self._accounts: Dict[str, KAVMAccount] = {
            self._faucet_address: KAVMAccount(address=faucet_address, amount=constants.FAUCET_ALGO_SUPPLY)
        }
        # Initialize KAVM, fetching the K definition dir from the environment
        definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
        if definition_dir is not None:
            self.kavm = KAVM(
                definition_dir=Path(definition_dir),
                logger=self.algodLogger,
                init_pyk=False,
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
        params: Optional[List[str]] = None,
        data: Optional[bytes] = None,
        headers: Optional[List[str]] = None,
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
                txid = params[1]
                return self.kavm._committed_txns[txid]
            else:
                raise NotImplementedError(f'Endpoint not implemented: {requrl}')
        elif endpoint == 'accounts':
            (config, subst) = split_config_from(self.kavm.current_config)

            address = params[0]
            return self.kavm.accounts[address].dictify()

        elif endpoint == 'applications':
            (config, subst) = split_config_from(self.kavm.current_config)

            app_id = params[0]
            return self.kavm.apps[app_id].dictify()

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
            txns = [t.transaction for t in msgpack_decode_txn_list(data)]
            txn_msg = self.pretty_printer.pformat(txns)
            algod_debug_log_msg = f'POST {requrl} {txn_msg}'
            # log decoded transaction as submitted
            self.algodLogger.debug(algod_debug_log_msg)

            # we'll need too keep track of all addresses the transactions mention to
            # make KAVM aware of the new ones, so we preprocess the transactions
            # to dicover new addresses and initialize them with 0 balance
            for txn in txns:
                if not txn.sender in self._accounts.keys():
                    self._accounts[txn.sender] = KAVMAccount(address=txn.sender, amount=0)
                if hasattr(txn, 'receiver'):
                    if not txn.receiver in self._accounts.keys():
                        self._accounts[txn.receiver] = KAVMAccount(address=txn.receiver, amount=0)

            scenario = KAVMClient._construct_scenario(
                accounts=self._accounts.values(), transactions=[t.dictify() for t in txns]
            )
            self.algodLogger.debug(self.pretty_printer.pformat(scenario))
            self.algodLogger.debug(self.pretty_printer.pformat(json.dumps(scenario)))

            try:
                proc_result = self.kavm.run_avm_json(
                    scenario=f'{json.dumps(scenario)}', teals='.TealProgramsStore', depth=0, output='pretty'
                )
            except CalledProcessError as e:
                self.algodLogger.debug(e.stdout)

            # return self.kavm.eval_transactions(kavm_txns, known_addresses)
        elif requrl == '/teal/compile':
            assert data is not None, 'attempt to compile an empty TEAL program!'
            # we do not actually compile the program since KAVM needs the source code
            return {'result': b64encode(data)}
        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')

    @staticmethod
    def _construct_scenario(accounts: Iterable[KAVMAccount], transactions: Iterable[Transaction]) -> Dict[str, Any]:
        """Construct a JSON simulation scenario to run on KAVM"""
        return {
            "stages": [
                {"stage-type": "setup-network", "data": {"accounts": [acc.dictify() for acc in accounts]}},
                {
                    "stage-type": "execute-transactions",
                    "data": {"transactions": [KAVMTransaction.sanitize_byte_fields(txn) for txn in transactions]},
                    "expected-returncode": 0,
                    "expected-paniccode": 0,
                },
            ]
        }
