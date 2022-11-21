import json
import logging
import os
from base64 import b64encode
from pathlib import Path
from pprint import PrettyPrinter
from subprocess import CalledProcessError
from typing import Any, Dict, Iterable, List, Optional, cast

import msgpack
from algosdk import encoding
from algosdk.future.transaction import PaymentTxn, Transaction
from algosdk.v2client import algod

from kavm import constants
from kavm.adaptors.algod_account import KAVMAccount
from kavm.adaptors.algod_transaction import KAVMTransaction
from kavm.kavm import KAVM
from kavm.scenario import KAVMScenario


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
        self._decompiled_teal_dir_path = Path('./.decompiled-teal').resolve()
        self._decompiled_teal_dir_path.mkdir(exist_ok=True)

        self._app_creators: Dict[int, str] = {}
        # Initialize KAVM, fetching the K definition dir from the environment
        definition_dir = os.environ.get('KAVM_DEFINITION_DIR')
        if definition_dir is not None:
            self.kavm = KAVM(definition_dir=Path(definition_dir))
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
                if len(params) >= 2:
                    return self._committed_txns[params[1]]
                else:
                    raise NotImplementedError(f'Endpoint not implemented: {requrl}')
            else:
                raise NotImplementedError(f'Endpoint not implemented: {requrl}')
        elif endpoint == 'accounts':
            if len(params) == 1:
                address = params[0]
                return self._accounts[address].dictify()
            else:
                raise NotImplementedError(f'Endpoint not implemented: {requrl}')

        elif endpoint == 'applications':
            app_id = int(params[0])
            try:
                creator_address = self._app_creators[app_id]
                return self._accounts[creator_address].created_apps[app_id]
            except KeyError as e:
                raise ValueError(f'Cannot find app with id {app_id}') from e

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
            f'POST {requrl} {txn_msg}'
            # log decoded transaction as submitted

            return self._eval_transactions(txns)

            # self.algodLogger.debug(proc_result.stdout)
            # assert False

            # return self.kavm.eval_transactions(kavm_txns, known_addresses)
        elif requrl == '/teal/compile':
            assert data is not None, 'attempt to compile an empty TEAL program!'
            # we do not actually compile the program since KAVM needs the source code
            return {'result': b64encode(data)}
        else:
            raise NotImplementedError(f'Endpoint not implemented: {requrl}')

    def _eval_transactions(self, txns: List[Transaction]) -> Dict[str, str]:
        """
        Evaluate a transaction group
        Parameters
        ----------
        txns
            List[Transaction]

        Construct a simulation scenario, serialize it into JSON and submit to KAVM.
        Parse KAVM's resulting configuration and update the account state in KAVMClient.
        """

        # we'll need too keep track of all addresses the transactions mention to
        # make KAVM aware of the new ones, so we preprocess the transactions
        # to dicover new addresses and initialize them with 0 balance
        for txn in txns:
            if not txn.sender in self._accounts.keys():
                self._accounts[txn.sender] = KAVMAccount(address=txn.sender, amount=0)
            if hasattr(txn, 'receiver'):
                txn = cast(PaymentTxn, txn)
                if not txn.receiver in self._accounts.keys():
                    self._accounts[txn.receiver] = KAVMAccount(address=txn.receiver, amount=0)

        scenario = self._construct_scenario(accounts=self._accounts.values(), transactions=txns)

        try:
            self.algodLogger.debug(f'Executing scenario: {json.dumps(scenario.dictify(), indent=4)}')
            proc_result = self.kavm.run_avm_json(
                scenario=scenario.to_json(),
                teals=self.kavm.parse_teals(scenario._teal_files, self._decompiled_teal_dir_path),
                depth=0,
                output='final-state-json',
            )
        except CalledProcessError as e:
            self.algodLogger.critical(
                f'Transaction group evaluation failed, last generated scenario was: {json.dumps(scenario.dictify(), indent=4)}'
            )
            raise e

        final_state = {}
        try:
            # on succeful execution, the final state will be serialized and prineted to stderr
            final_state = json.loads(proc_result.stderr)
        except json.decoder.JSONDecodeError as e:
            self.algodLogger.critical(f'Failed to parse the final state JSON: {e}')
            raise

        self.algodLogger.debug(f'Successfully parsed final state JSON: {json.dumps(final_state, indent=4)}')
        # substitute the tracked accounts by KAVM's state
        self._accounts = {}
        for acc_dict in KAVMScenario.sanitize_accounts(final_state['accounts']):
            acc_dict_translated = {KAVMAccount.inverted_attribute_map[k]: v for k, v in acc_dict.items()}
            self._accounts[acc_dict_translated['address']] = KAVMAccount(**acc_dict_translated)
        # merge confirmed transactions with the ones received from KAVM
        for txn in final_state['transactions']:
            self._committed_txns[txn['id']] = txn['params']
        return {'txId': final_state['transactions'][0]['id']}

    def _construct_scenario(self, accounts: Iterable[KAVMAccount], transactions: Iterable[Transaction]) -> KAVMScenario:
        """Construct a JSON simulation scenario to run on KAVM"""
        scenario = KAVMScenario.from_json(
            json.dumps(
                {
                    "stages": [
                        {"stage-type": "setup-network", "data": {"accounts": [acc.dictify() for acc in accounts]}},
                        {
                            "stage-type": "execute-transactions",
                            "data": {
                                "transactions": [
                                    KAVMTransaction.sanitize_byte_fields(txn.dictify()) for txn in transactions
                                ]
                            },
                            "expected-returncode": 0,
                            "expected-paniccode": 0,
                        },
                    ]
                }
            )
        )
        scenario.decompile_teal_programs(self._decompiled_teal_dir_path)
        return scenario
