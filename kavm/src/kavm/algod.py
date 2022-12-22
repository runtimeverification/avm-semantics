import json
import logging
import os
from base64 import b64encode
from pathlib import Path
from pprint import PrettyPrinter
from typing import Any, Dict, Final, Iterable, List, Optional, cast

import msgpack
from algosdk import encoding
from algosdk.atomic_transaction_composer import (
    ABI_RETURN_HASH,
    ABIResult,
    AtomicTransactionComposer,
    AtomicTransactionComposerStatus,
    AtomicTransactionResponse,
    abi,
    base64,
    error,
    transaction,
)
from algosdk.error import AlgodHTTPError
from algosdk.future.transaction import PaymentTxn, Transaction
from algosdk.v2client import algod

from kavm import constants
from kavm.adaptors.algod_account import KAVMAccount
from kavm.adaptors.algod_transaction import KAVMTransaction
from kavm.kavm import KAVM
from kavm.scenario import KAVMScenario, _sort_dict

_LOGGER: Final = logging.getLogger(__name__)


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

    def __init__(
        self,
        faucet_address: str,
        algod_token: Optional[str] = None,
        algod_address: Optional[str] = None,
        log_level: Optional[int] = None,
    ) -> None:
        super().__init__(algod_token, algod_address)
        self.pretty_printer = PrettyPrinter(width=41, compact=True)

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
            self.kavm.definition
        else:
            _LOGGER.critical('Cannot initialize KAVM: KAVM_DEFINITION_DIR env variable is not set')
            exit(1)

    def set_log_level(self, log_level: Any) -> None:
        """
        Set log level for algod requests
        """
        _LOGGER.setLevel(log_level)

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
                    try:
                        return self._committed_txns[params[1]]
                    # hack to temporarily make py-algorand-sdk happy:
                    # if the txn id is not found, return the last committed txn
                    except KeyError:
                        (_, txn) = sorted(self._committed_txns.items())[-1]
                        return txn
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
            except KeyError as e:
                raise ValueError(f'Cannot find creator of app {app_id}') from e
            try:
                result = list(filter(lambda app: app['id'] == app_id, self._accounts[creator_address].created_apps))
                return result[0]
            except (KeyError, IndexError) as e:
                raise ValueError(
                    f'Cannot find app with id {app_id} in account {self._accounts[creator_address]}'
                ) from e
        elif endpoint == 'status':
            return {
                'catchup-time': 0,
                'last-round': 1000000000000000,
                'last-version': 'kavm',
                'next-version': 'kavm',
                'next-version-round': 0,
                'next-version-supported': True,
                'stopped-at-unsupported-round': True,
                'time-since-last-round': 0,
                'last-catchpoint': 'kavm',
                'catchpoint': 'kavm',
                'catchpoint-total-accounts': 0,
                'catchpoint-processed-accounts': 0,
                'catchpoint-verified-accounts': 0,
                'catchpoint-total-blocks': 0,
                'catchpoint-acquired-blocks': 0,
            }
        else:
            _LOGGER.debug(requrl.split('/'))
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

            # _LOGGER.debug(proc_result.stdout)
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
        self._last_scenario = scenario

        try:
            final_state, kavm_stderr = self.kavm.run_avm_json(
                scenario=scenario,
                existing_decompiled_teal_dir=self._decompiled_teal_dir_path,
            )
        except RuntimeError as e:
            _LOGGER.error(f'Transaction group evaluation failed with status: {e.args[0]}')
            _LOGGER.debug(f'Last generated scenario was: {json.dumps(scenario.dictify(), indent=4)}')
            raise AlgodHTTPError(msg=f'KAVM has failed with status {e.args[0]}') from None

        try:
            # on succeful execution, the final state will be serialized and prineted to stderr
            state_dump = json.loads(kavm_stderr)
            assert type(state_dump) is dict
        except json.decoder.JSONDecodeError as e:
            _LOGGER.critical(f'Failed to parse the final state JSON: {e}')
            raise AlgodHTTPError(msg='KAVM has failed, see logs for reasons') from e

        _LOGGER.debug(f'Successfully parsed final state JSON: {json.dumps(state_dump, indent=4)}')
        # substitute the tracked accounts by KAVM's state
        self._accounts = {}
        for acc_dict in KAVMScenario.sanitize_accounts(state_dump['accounts']):
            acc_dict_translated = {KAVMAccount.inverted_attribute_map[k]: v for k, v in acc_dict.items()}
            self._accounts[acc_dict_translated['address']] = KAVMAccount(**acc_dict_translated)
            # update app creators
            for addr, acc in self._accounts.items():
                for app in acc.created_apps:
                    self._app_creators[app['id']] = addr
        # merge confirmed transactions with the ones received from KAVM
        for txn in state_dump['transactions']:
            self._committed_txns[txn['id']] = txn['params']
        return {'txId': state_dump['transactions'][0]['id']}

    def _construct_scenario(self, accounts: Iterable[KAVMAccount], transactions: Iterable[Transaction]) -> KAVMScenario:
        """Construct a JSON simulation scenario to run on KAVM"""
        scenario = KAVMScenario.from_json(
            scenario_json_str=json.dumps(
                {
                    "stages": [
                        {"stage-type": "setup-network", "data": {"accounts": [acc.dictify() for acc in accounts]}},
                        {
                            "stage-type": "submit-transactions",
                            "data": {
                                "transactions": [
                                    KAVMTransaction.sanitize_byte_fields(_sort_dict(txn.dictify()))
                                    for txn in transactions
                                ]
                            },
                            "expected-returncode": 0,
                        },
                    ]
                }
            ),
            teal_sources_dir=self._decompiled_teal_dir_path,
        )
        return scenario


class KAVMAtomicTransactionComposer(AtomicTransactionComposer):
    def execute(
        self, client: algod.AlgodClient, wait_rounds: int, override_tx_ids: Optional[List[str]] = None
    ) -> "AtomicTransactionResponse":
        """
        Send the transaction group to the network and wait until it's committed
        to a block. An error will be thrown if submission or execution fails.
        The composer's status must be SUBMITTED or lower before calling this method,
        since execution is only allowed once. If submission is successful,
        this composer's status will update to SUBMITTED.
        If the execution is also successful, this composer's status will update to COMMITTED.
        Note: a group can only be submitted again if it fails.
        Args:
            client (AlgodClient): Algod V2 client
            wait_rounds (int): maximum number of rounds to wait for transaction confirmation
        Returns:
            AtomicTransactionResponse: Object with confirmed round for this transaction,
                a list of txIDs of the submitted transactions, and an array of
                results for each method call transaction in this group. If a
                method has no return value (void), then the method results array
                will contain None for that method's return value.
        """
        if self.status > AtomicTransactionComposerStatus.SUBMITTED:  # type: ignore
            raise error.AtomicTransactionComposerError(
                "AtomicTransactionComposerStatus must be submitted or lower to execute a group"
            )

        self.submit(client)
        self.status = AtomicTransactionComposerStatus.SUBMITTED

        # HACK: override the real transaction ids with the ones KAVM gave us
        if override_tx_ids:
            self.tx_ids = override_tx_ids

        resp = transaction.wait_for_confirmation(client, self.tx_ids[0], wait_rounds)

        self.status = AtomicTransactionComposerStatus.COMMITTED

        confirmed_round = resp["confirmed-round"]
        method_results = []

        for i, tx_id in enumerate(self.tx_ids):
            raw_value = None
            return_value = None
            decode_error = None
            tx_info = None

            if i not in self.method_dict:
                continue

            # Parse log for ABI method return value
            try:
                tx_info = client.pending_transaction_info(tx_id)
                if self.method_dict[i].returns.type == abi.Returns.VOID:
                    method_results.append(
                        ABIResult(
                            tx_id=tx_id,
                            raw_value=raw_value,
                            return_value=return_value,
                            decode_error=decode_error,
                            tx_info=tx_info,
                            method=self.method_dict[i],
                        )
                    )
                    continue

                logs = tx_info["logs"] if "logs" in tx_info else []

                # Look for the last returned value in the log
                if not logs:
                    raise error.AtomicTransactionComposerError("app call transaction did not log a return value")
                result = logs[-1]
                # Check that the first four bytes is the hash of "return"
                result_bytes = base64.b64decode(result)
                if len(result_bytes) < 4 or result_bytes[:4] != ABI_RETURN_HASH:
                    raise error.AtomicTransactionComposerError("app call transaction did not log a return value")
                raw_value = result_bytes[4:]
                return_value = self.method_dict[i].returns.type.decode(raw_value)
            except Exception as e:
                decode_error = e
                raise

            abi_result = ABIResult(
                tx_id=tx_id,
                raw_value=raw_value,
                return_value=return_value,
                decode_error=decode_error,
                tx_info=tx_info,
                method=self.method_dict[i],
            )
            method_results.append(abi_result)

        return AtomicTransactionResponse(
            confirmed_round=confirmed_round,
            tx_ids=self.tx_ids,
            results=method_results,
        )
