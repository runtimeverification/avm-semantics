import logging
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

from algosdk.abi.contract import Contract
from algosdk.abi.method import Method
from algosdk.encoding import checksum, decode_address, encode_address
from algosdk.future.transaction import ApplicationCallTxn, PaymentTxn, StateSchema
from pyk.kast.inner import KApply, KInner, KLabel, KRewrite, KSort, KToken, KVariable, Subst, build_assoc
from pyk.kast.manip import inline_cell_maps, push_down_rewrites
from pyk.kast.outer import KClaim, read_kast_definition
from pyk.ktool.kprint import build_symbol_table, paren, pretty_print_kast
from pyk.ktool.kprove import KProve
from pyk.prelude.kint import intToken
from pyk.prelude.string import stringToken

from kavm.adaptors.algod_transaction import transaction_k_term
from kavm.algod import KAVMClient
from kavm.kavm import KAVM
from kavm.pyk_utils import algorand_addres_to_k_bytes, generate_tvalue_list, int_2_bytes, method_selector_to_k_bytes

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'

kavm = KAVM(
    definition_dir=Path("/home/geo2a/Workspace/RV/avm-semantics/.build/usr/lib/kavm/avm-llvm/avm-testing-kompiled/")
)


class SymbolicApplTxn:
    pass


class SymbolicApplication:
    def __init__(
        self,
        app_id: int,
        local_state_schema: StateSchema,
        global_state_schema: StateSchema,
        approval_pgm_path: Path,
        clear_pgm_path: Path,
    ):
        self.app_id = app_id
        self.local_state_schema = local_state_schema
        self.global_state_schema = global_state_schema
        self.approval_pgm_path = approval_pgm_path
        self.clear_pgm_path = clear_pgm_path
        self.labels: List[KInner] = []

    def preprocess_kast(self, term: KInner) -> KInner:
        def hex_token_to_k_string(ht: str) -> str:
            string = ""
            for i in range(0, len(ht), 2):
                string += "\\x"
                string += ht[i] + ht[i + 1]
            return string

        if type(term) is KApply:
            if term.label.name == "method__TEAL-OPCODES_PseudoOpCode_TBytesLiteral":
                if type(term.args[0]) is KToken:
                    selector = str(Method.from_signature(term.args[0].token[1:-1]).get_selector())[2:-1]
                    return KApply("byte__TEAL-OPCODES_PseudoOpCode_TBytesLiteral", stringToken(selector))
            if len(term.args) == 0:
                return term
            else:
                result = KApply(label=term.label, args=[self.preprocess_kast(arg) for arg in term.args])
                return result
        else:
            if type(term) is KToken:
                if term.sort == KSort(name="Label"):
                    var = KVariable(str(term.token).upper())
                    self.labels.append(var)
                    return var
                elif term.sort == KSort(name="HexToken"):
                    return stringToken(hex_token_to_k_string(term.token[2:]))

                else:
                    return term
            else:
                return term

    def get_config(self) -> KInner:
        return KApply(
            "<app>",
            [
                KApply("<appID>", KToken(str(self.app_id), "Int")),
                KApply(
                    "<approvalPgmSrc>",
                    self.preprocess_kast(kavm.kore_to_kast(kavm.parse_teal(self.approval_pgm_path))),
                ),
                KApply(
                    "<clearStatePgmSrc>",
                    self.preprocess_kast(kavm.kore_to_kast(kavm.parse_teal(self.clear_pgm_path))),
                ),
                KApply("<approvalPgm>", KToken(".Bytes", "Bytes")),
                KApply("<clearStatePgm>", KToken(".Bytes", "Bytes")),
                KApply(
                    "<globalState>",
                    [
                        KApply("<globalNumInts>", KToken(str(self.global_state_schema.num_uints), "Int")),
                        KApply("<globalNumBytes>", KToken(str(self.global_state_schema.num_byte_slices), "Int")),
                        KApply("<globalInts>", KToken(".Map", "Map")),
                        KApply("<globalBytes>", KToken(".Map", "Map")),
                    ],
                ),
                KApply(
                    "<localState>",
                    [
                        KApply("<localNumInts>", KToken(str(self.local_state_schema.num_uints), "Int")),
                        KApply("<localNumBytes>", KToken(str(self.local_state_schema.num_byte_slices), "Int")),
                    ],
                ),
                KApply("<extraPages>", KToken("0", "Int")),
            ],
        )


class SymbolicAccount:
    def __init__(
        self,
        address: str,
        balance: int,
    ):
        # self.address = KToken("b\"" + str(decode_address(address))[2:-1] + "\"", "Bytes")
        self.address = algorand_addres_to_k_bytes(address)
        self.balance = KToken(str(balance), "Int")
        self.apps_config: List[KInner] = []
        self.apps: List[SymbolicApplication] = []

    def add_app(self, application: SymbolicApplication) -> None:
        self.apps_config.append(application.get_config())
        self.apps.append(application)

    def build_created_apps(self) -> KInner:
        return build_assoc(
            KToken(".Bag", "AppMapCell"),
            KLabel("_AppCellMap_"),
            self.apps_config,
        )

    def get_symbolic_config_pre(self) -> KInner:
        return KApply(
            "<account>",
            [
                KApply("<address>", self.address),
                KApply("<balance>", self.balance),
                KApply("<minBalance>", KToken("10000000", "Int")),
                KApply("<round>", KToken("0", "Int")),
                KApply("<preRewards>", KToken("0", "Int")),
                KApply("<rewards>", KToken("0", "Int")),
                KApply("<status>", KToken("0", "Int")),
                KApply("<key>", KToken(".Bytes", "Bytes")),
                KApply("<appsCreated>", self.build_created_apps()),
                KApply("<appsOptedIn>", KToken(".Bag", "OptInAppMapCell")),
                KApply("<assetsCreated>", KToken(".Bag", "AssetMapCell")),
                KApply("<assetsOptedIn>", KToken(".Bag", "OptInAssetMapCell")),
                KApply("<boxes>", KToken(".Bag", "BoxMapCell")),
            ],
        )


class KAVMProof:
    def __init__(self, definition_dir: Path, use_directory: Path, claim_name: str) -> None:
        self._definition_dir = definition_dir
        self._use_directory = use_directory
        self._claim_name = claim_name

        self._txns: List[KInner] = []
        self._txn_ids: List[int] = []
        self._txns_post: List[KInner] = []
        self._accts: List[SymbolicAccount] = []
        self._accts_config: List[KInner] = []
        self._accts_post: List[KInner] = []
        self._preconditions: List[KInner] = []
        self._postconditions: List[KInner] = []

    def add_txn(self, txn_pre: KInner, txn_post: KInner) -> None:
        self._txns.append(txn_pre)
        self._txns_post.append(txn_post)

    def add_acct(self, acct: SymbolicAccount) -> None:
        self._accts_config.append(acct.get_symbolic_config_pre())
        self._accts.append(acct)

    def add_precondition(self, precondition: KInner) -> None:
        self._preconditions.append(precondition)

    def add_postcondition(self, postcondition: KInner) -> None:
        self._postconditions.append(postcondition)

    def build_app_creator_map(self) -> KInner:
        creator_map = []
        for acct in self._accts:
            for app in acct.apps:
                creator_map.append(KApply("_|->_", [KToken(str(app.app_id), "Int"), acct.address]))
        return build_assoc(KApply(".Map"), KLabel("_Map_"), creator_map)

    def build_transactions(self, txns: List[KInner]) -> KInner:
        return build_assoc(
            KApply(".TransactionCellMap"),
            KLabel("_TransactionCellMap_"),
            txns,
        )

    def build_accounts(self) -> KInner:
        return build_assoc(
            KToken(".Bag", "AccountCellMap"),
            KLabel("_AccountCellMap_"),
            self._accts_config,
        )

    def build_deque(self) -> KInner:
        return build_assoc(
            KApply(".List"),
            KLabel("_List_"),
            [KApply("ListItem", stringToken(str(i))) for i in range(0, len(self._txns))],
        )

    def build_deque_set(self) -> KInner:
        return build_assoc(
            KApply(".Set"),
            KLabel("_Set_"),
            [KApply("SetItem", stringToken(str(i))) for i in range(0, len(self._txns))],
        )

    def prove(self) -> None:

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#evalTxGroup")),
                KApply("<panicstatus>", stringToken("")),
                KApply("<paniccode>", intToken(0)),
                KApply("<returnstatus>", stringToken("Failure - AVM is stuck")),
                KApply("<returncode>", intToken(0)),
                KApply("<transactions>", [self.build_transactions(self._txns)]),
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KToken("\"\"", "String")),
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", self.build_deque()),
                                KApply("<dequeIndexSet>", self.build_deque_set()),
                            ],
                        ),
                        KApply(
                            "<currentTxnExecution>",
                            [
                                KApply(
                                    "<globals>",
                                    [
                                        KApply("<groupSize>", intToken(0)),
                                        KApply("<globalRound>", intToken(0)),
                                        KApply("<latestTimestamp>", intToken(0)),
                                        KApply("<currentApplicationID>", intToken(0)),
                                        KApply("<currentApplicationAddress>", KToken(".Bytes", "Bytes")),
                                        KApply("<creatorAddress>", KToken(".Bytes", "Bytes")),
                                    ],
                                ),
                                KApply(
                                    "<teal>",
                                    [
                                        KApply("<pc>", intToken(0)),
                                        KApply("<program>", KToken(".Map", "Map")),
                                        KApply("<mode>", KToken("undefined", "TealMode")),
                                        KApply("<version>", KToken("8", "Int")),
                                        KApply("<stack>", KToken(".TStack", "TStack")),
                                        KApply("<stacksize>", intToken(0)),
                                        KApply("<jumped>", KToken("false", "Bool")),
                                        KApply("<labels>", KToken(".Map", "Map")),
                                        KApply("<callStack>", KToken(".List", "List")),
                                        KApply("<scratch>", KToken(".Map", "Map")),
                                        KApply("<intcblock>", KToken(".Map", "Map")),
                                        KApply("<bytecblock>", KToken(".Map", "Map")),
                                    ],
                                ),
                                KApply("<effects>", KToken(".List", "List")),
                                KApply("<lastTxnGroupID>", stringToken("")),
                            ],
                        ),
                        KApply("<innerTransactions>", KToken(".List", "List")),
                        KApply("<activeApps>", KToken(".Set", "Set")),
                        KApply("<touchedAccounts>", KToken(".List", "List")),
                    ],
                ),
                KApply(
                    "<blockchain>",
                    [
                        KApply("<accountsMap>", self.build_accounts()),
                        KApply("<appCreator>", self.build_app_creator_map()),
                        KApply("<assetCreator>", KToken(".Map", "Map")),
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", intToken(0)),
                        KApply("<nextTxnID>", intToken(0)),
                        KApply("<nextAppID>", intToken(1)),
                        KApply("<nextAssetID>", intToken(1)),
                        KApply("<nextGroupID>", intToken(0)),
                        KApply("<txnIndexMap>", KToken(".Bag", "TxnIndexMapGroupCell")),
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),
            ],
        )

        rhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KToken(".K", "KItem ")),
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", intToken(0)),
                KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", intToken(0)),
                KApply("<transactions>", [self.build_transactions(self._txns_post)]),
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KVariable("?_")),
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", KToken(".List", "List")),
                                KApply("<dequeIndexSet>", KVariable("?_")),
                            ],
                        ),
                        KApply(
                            "<currentTxnExecution>",
                            [
                                KApply(
                                    "<globals>",
                                    [
                                        KApply("<groupSize>", KVariable("?_")),
                                        KApply("<globalRound>", KVariable("?_")),
                                        KApply("<latestTimestamp>", KVariable("?_")),
                                        KApply("<currentApplicationID>", KVariable("?_")),
                                        KApply("<currentApplicationAddress>", KVariable("?_")),
                                        KApply("<creatorAddress>", KVariable("?_")),
                                    ],
                                ),
                                KApply(
                                    "<teal>",
                                    [
                                        KApply("<pc>", KVariable("?_")),
                                        KApply("<program>", KVariable("?_")),
                                        KApply("<mode>", KVariable("?_")),
                                        KApply("<version>", KVariable("?_")),
                                        KApply("<stack>", KVariable("?_")),
                                        KApply("<stacksize>", KVariable("?_")),
                                        KApply("<jumped>", KVariable("?_")),
                                        KApply("<labels>", KVariable("?_")),
                                        KApply("<callStack>", KVariable("?_")),
                                        KApply("<scratch>", KVariable("?_")),
                                        KApply("<intcblock>", KVariable("?_")),
                                        KApply("<bytecblock>", KVariable("?_")),
                                    ],
                                ),
                                KApply("<effects>", KToken(".List", "List")),
                                KApply("<lastTxnGroupID>", KVariable("?_")),
                            ],
                        ),
                        KApply("<innerTransactions>", KVariable("?_")),
                        KApply("<activeApps>", KToken(".Set", "Set")),
                        KApply("<touchedAccounts>", KToken(".List", "List")),
                    ],
                ),
                KApply(
                    "<blockchain>",
                    [
                        KApply("<accountsMap>", KVariable("?_")),
                        KApply("<appCreator>", KVariable("?_")),
                        KApply("<assetCreator>", KVariable("?_")),
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", intToken(0)),
                        KApply("<nextTxnID>", KVariable("?_")),
                        KApply("<nextAppID>", KVariable("?_")),
                        KApply("<nextAssetID>", KVariable("?_")),
                        KApply("<nextGroupID>", KVariable("?_")),
                        KApply("<txnIndexMap>", KVariable("?_")),
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),
            ],
        )

        def remove_duplicates(labels: List) -> List:
            return [*set(labels)]

        for account in self._accts:
            for app in account.apps:
                app.labels = remove_duplicates(app.labels)
                for i in range(len(app.labels)):
                    for j in range(len(app.labels)):
                        if i == j:
                            continue
                        self._preconditions.append(KApply("_=/=K_", [app.labels[i], app.labels[j]]))

        requires = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._preconditions)

        ensures = build_assoc(KToken("true", "Bool"), KLabel("_andBool_"), self._postconditions)

        claim = KClaim(
            body=push_down_rewrites(KRewrite(lhs, rhs)),
            requires=requires,
            ensures=ensures,
        )

        defn = read_kast_definition(self._definition_dir / 'parsed.json')
        symbol_table = build_symbol_table(defn)
        symbol_table['_+Bytes_'] = paren(lambda a1, a2: a1 + ' +Bytes ' + a2)

        proof = KProve(definition_dir=self._definition_dir, use_directory=self._use_directory)
        proof._symbol_table = symbol_table

        result = proof.prove_claim(claim=claim, claim_id=self._claim_name)

        if type(result) is KApply and result.label.name == "#Top":
            print("Proved claim")
        else:
            print("Failed to prove claim")
            print("counterexample:")

            print(pretty_print_kast(inline_cell_maps(result), symbol_table=symbol_table))


class MethodWithSpec(Method):
    def __init__(
        self,
        sdk_method: Method,
        preconditions: Optional[List[KInner]] = None,
        postconditions: Optional[List[KInner]] = None,
    ):
        super().__init__(name=sdk_method.name, args=sdk_method.args, returns=sdk_method.returns, desc=sdk_method.desc)
        self._preconditions = preconditions if preconditions else []
        self._postconditions = postconditions if postconditions else []

    @property
    def preconditions(self) -> List[KInner]:
        return self._preconditions

    @property
    def postconditions(self) -> List[KInner]:
        return self._postconditions


class AutoProver:
    @staticmethod
    def _in_bounds_uint64(term: KInner) -> KInner:
        return KApply(
            '_andBool_',
            [
                KApply("_>=Int_", [term, intToken(0)]),
                KApply("_<=Int_", [term, KToken("MAX_UINT64", "Int")]),
            ],
        )

    @classmethod
    def _faucet_account(cls) -> Tuple[str, str]:
        """
        Return a pre-generatd pair of private key and Algorand adress for the faucet account
        """
        return (
            'cz+FBjUbtcM8bkMHCZfs/L9WnZVx7VSEa6KwRk9BQIQVVR6aLOAyPc66Z0b6PMC2TmX2ZEBlyNvG/XhtQmK04g==',
            'CVKR5GRM4AZD3TV2M5DPUPGAWZHGL5TEIBS4RW6G7V4G2QTCWTRIGNDVXQ',
        )

    @classmethod
    def _creator_account(cls) -> Tuple[str, str]:
        """
        Return a pre-generatd pair of private key and Algorand adress for the app creator account
        """
        return (
            '/3LVAqbrt+sxF+tXe4KGKBhAPGPtqHAOyLTe6PhTXIz+C+kwBB+NS6fftG8gZ2Norh5VBrNoivQ2CE0M4hhfHQ==',
            '7YF6SMAED6GUXJ67WRXSAZ3DNCXB4VIGWNUIV5BWBBGQZYQYL4ORSSFRIY',
        )

    def prove(self, method_name: str) -> None:
        self._proofs[method_name].prove()

    def __init__(
        self,
        definition_dir: Path,
        approval_pgm: Path,
        clear_pgm: Path,
        contract: Contract,
    ):

        self._proofs: Dict[str, KAVMProof] = {}

        _, faucet_addr = AutoProver._faucet_account()
        algod = KAVMClient(faucet_address=str(faucet_addr))
        _, creator_addr = AutoProver._creator_account()
        sp = algod.suggested_params()

        _LOGGER.info(f'Initializing proofs for contract {contract.name}')

        creator_account = SymbolicAccount(address=str(creator_addr), balance=1000000000)
        app_id = 42
        app = SymbolicApplication(
            app_id=app_id,
            local_state_schema=StateSchema(0, 0),
            global_state_schema=StateSchema(0, 0),
            approval_pgm_path=approval_pgm,
            clear_pgm_path=clear_pgm,
        )
        app_addr = str(encode_address(checksum(b'appID' + (app_id).to_bytes(8, 'big'))))
        app_account = SymbolicAccount(address=app_addr, balance=42424242424242)
        creator_account.add_app(app)

        for method in contract.methods:
            proof = KAVMProof(
                definition_dir=definition_dir,
                use_directory=Path("proofs"),
                claim_name=f'{contract.name}-{method.name}',
            )
            proof.add_acct(creator_account)
            proof.add_acct(app_account)

            _LOGGER.info(f'Generating K claim for method {method.name}')
            assert isinstance(method, MethodWithSpec)

            app_args: List[KInner] = [method_selector_to_k_bytes(method.get_selector())]
            for i, arg in enumerate(method.args):
                _LOGGER.info(f'Analyzing method argument {i} with name {arg.name} of type {arg.type}')
                if str(arg.type) == 'uint64':
                    arg_k_var = KVariable(str(arg.name).upper(), sort=KSort("Int"))
                    app_args.append(int_2_bytes(arg_k_var))
                    arg_pre = AutoProver._in_bounds_uint64(arg_k_var)
                    _LOGGER.info(f'Adding precondiotion on argument {arg.name}: {algod.kavm.pretty_print(arg_pre)}')
                    method.preconditions.append(arg_pre)
                elif str(arg.type) == 'pay':
                    sdk_txn = PaymentTxn(sender=creator_addr, receiver=app_addr, sp=sp, amt=0)
                    amount_k_var = KVariable(str(arg.name).upper(), sort=KSort("Int"))
                    txn_pre = transaction_k_term(
                        kavm=algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fileds_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': algorand_addres_to_k_bytes(sdk_txn.sender),
                                'RECEIVER_CELL': algorand_addres_to_k_bytes(sdk_txn.receiver),
                            }
                        ),
                    )
                    txn_post = transaction_k_term(
                        kavm=algod.kavm,
                        txn=sdk_txn,
                        txid='0',
                        symbolic_fileds_subst=Subst(
                            {
                                'AMOUNT_CELL': amount_k_var,
                                'GROUPIDX_CELL': intToken(0),
                                'SENDER_CELL': KToken(
                                    "b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"
                                ),
                                'RECEIVER_CELL': KToken(
                                    "b\"" + str(decode_address(sdk_txn.receiver))[2:-1] + "\"", "Bytes"
                                ),
                                'RESUME_CELL': KVariable('?_'),
                            }
                        ),
                    )
                    amount_pre = AutoProver._in_bounds_uint64(amount_k_var)
                    _LOGGER.info(f'Adding precondiotion on argument {arg.name}: {algod.kavm.pretty_print(amount_pre)}')
                    method.preconditions.append(amount_pre)
                    proof.add_txn(txn_pre, txn_post)
                else:
                    _LOGGER.critical(f"Not yet supported: method argument of type {arg.type}")
                    exit(1)

            for pre in method.preconditions:
                proof.add_precondition(pre)
            for post in method.postconditions:
                proof.add_postcondition(post)

            # for method_txn in method.txn_calls:
            sdk_txn = ApplicationCallTxn(sender=creator_addr, index=app_id, on_complete=0, sp=sp)
            txn_pre = transaction_k_term(
                kavm=algod.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fileds_subst=Subst(
                    {
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'SENDER_CELL': KToken("b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"),
                    }
                ),
            )
            txn_post = transaction_k_term(
                kavm=algod.kavm,
                txn=sdk_txn,
                txid='1',
                symbolic_fileds_subst=Subst(
                    {
                        'SENDER_CELL': KToken("b\"" + str(decode_address(sdk_txn.sender))[2:-1] + "\"", "Bytes"),
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(1),
                        'TXSCRATCH_CELL': KVariable('?_'),
                        'LOGDATA_CELL': KVariable('?FINAL_LOGDATA_CELL'),
                        'LOGSIZE_CELL': KVariable('?_'),
                        'RESUME_CELL': KVariable('?_'),
                    }
                ),
            )
            proof.add_txn(txn_pre, txn_post)
            self._proofs[method.name] = proof

        _LOGGER.info(
            f'Initialized K proofs for methods: {[contract.name + "-" + proof_name for proof_name in self._proofs.keys()]}'
        )
