from pathlib import Path
from typing import List, Optional

from algosdk.abi.contract import Contract
from algosdk.abi.method import Method
from algosdk.account import generate_account
from algosdk.future.transaction import ApplicationCallTxn, StateSchema
from pyk.cli_utils import run_process
from pyk.kast.inner import KApply, KInner, KLabel, KRewrite, KSort, KToken, KVariable, Subst, build_assoc
from pyk.kast.manip import inline_cell_maps, push_down_rewrites
from pyk.kast.outer import KClaim, read_kast_definition
from pyk.kore.parser import KoreParser
from pyk.ktool.kprint import build_symbol_table, paren, pretty_print_kast
from pyk.ktool.kprove import KProve
from pyk.prelude.bytes import bytesToken
from pyk.prelude.kint import intToken

from kavm.adaptors.algod_transaction import transaction_k_term
from kavm.algod import KAVMClient
from kavm.kavm import KAVM
from kavm.pyk_utils import generate_tvalue_list, int_2_bytes

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
                    return KApply(
                        "byte__TEAL-OPCODES_PseudoOpCode_TBytesLiteral", KToken("\"" + str(selector) + "\"", "String")
                    )
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
                    return KToken("\"" + hex_token_to_k_string(term.token[2:]) + "\"", "String")

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
        self.address = KToken("b\"" + address + "\"", "Bytes")
        self.balance = KToken(str(balance), "Int")
        self.apps_config: List[KInner] = []
        self.apps: List[SymbolicApplication] = []

    def add_app(self, application: SymbolicApplication) -> None:
        self.apps_config.append(application.get_config())
        self.apps.append(application)

    def build_created_apps(self) -> KInner:
        return build_assoc(
            KApply(".AppCellMap"),
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
    def __init__(self, definition_dir: Path, use_directory: Path) -> None:
        self._definition_dir = definition_dir
        self._use_directory = use_directory

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

    def build_transactions(self, txns) -> KInner:
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
            [KApply("ListItem", KToken("\"" + str(i) + "\"", "Int")) for i in range(0, len(self._txns))],
        )

    def build_deque_set(self) -> KInner:
        return build_assoc(
            KApply(".Set"),
            KLabel("_Set_"),
            [KApply("SetItem", KToken("\"" + str(i) + "\"", "Int")) for i in range(0, len(self._txns))],
        )

    def prove(self) -> None:

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#evalTxGroup")),
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Failure - AVM is stuck\"", "String")),
                KApply("<returncode>", KToken("0", "Int")),
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
                                        KApply("<groupSize>", KToken("0", "Int")),
                                        KApply("<globalRound>", KToken("0", "Int")),
                                        KApply("<latestTimestamp>", KToken("0", "Int")),
                                        KApply("<currentApplicationID>", KToken("0", "Int")),
                                        KApply("<currentApplicationAddress>", KToken(".Bytes", "Bytes")),
                                        KApply("<creatorAddress>", KToken(".Bytes", "Bytes")),
                                    ],
                                ),
                                KApply(
                                    "<teal>",
                                    [
                                        KApply("<pc>", KToken("0", "Int")),
                                        KApply("<program>", KToken(".Map", "Map")),
                                        KApply("<mode>", KToken("undefined", "TealMode")),
                                        KApply("<version>", KToken("8", "Int")),
                                        KApply("<stack>", KToken(".TStack", "TStack")),
                                        KApply("<stacksize>", KToken("0", "Int")),
                                        KApply("<jumped>", KToken("false", "Bool")),
                                        KApply("<labels>", KToken(".Map", "Map")),
                                        KApply("<callStack>", KToken(".List", "List")),
                                        KApply("<scratch>", KToken(".Map", "Map")),
                                        KApply("<intcblock>", KToken(".Map", "Map")),
                                        KApply("<bytecblock>", KToken(".Map", "Map")),
                                    ],
                                ),
                                KApply("<effects>", KToken(".List", "List")),
                                KApply("<lastTxnGroupID>", KToken("\"\"", "String")),
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
                        KApply("<blockheight>", KToken("0", "Int")),
                        KApply("<nextTxnID>", KToken("0", "Int")),
                        KApply("<nextAppID>", KToken("1", "Int")),
                        KApply("<nextAssetID>", KToken("1", "Int")),
                        KApply("<nextGroupID>", KToken("0", "Int")),
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
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", KToken("0", "Int")),
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
                        KApply("<blockheight>", KToken("0", "Int")),
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
        symbol_table['_+Bytes_'] = paren(lambda a1, a2: a1 + '+Bytes' + a2)

        proof = KProve(definition_dir=self._definition_dir, use_directory=self._use_directory)
        proof._symbol_table = symbol_table

        result = proof.prove_claim(claim=claim, claim_id="test")

        if type(result) is KApply and result.label.name == "#Top":
            print("Proved claim")
        else:
            print("Failed to prove claim")
            print("counterexample:")

            print(pretty_print_kast(inline_cell_maps(result), symbol_table=symbol_table))


class AutoProver:
    def __init__(
        self,
        definition_dir: Path,
        approval_pgm: Path,
        clear_pgm: Path,
        contract: Contract,
    ):

        faucet_pk, faucet_addr = generate_account()
        algod = KAVMClient(faucet_address=str(faucet_addr))
        pk1, addr1 = generate_account()
        pk2, addr2 = generate_account()
        sp = algod.suggested_params()

        for method in contract.methods:
            proof = KAVMProof(definition_dir=definition_dir, use_directory=Path("proofs"))
            sdk_txn = ApplicationCallTxn(sender=addr1, index=1, on_complete=0, sp=sp)

            app_args: List[KInner] = [KToken("b\"" + str(method.get_selector())[2:-1] + "\"", "Bytes")]
            for arg in method.args:
                if str(arg.type) == 'uint64':
                    app_args.append(int_2_bytes(KVariable(str(arg.name).upper(), sort=KSort("Int"))))
                else:
                    print("Not yet supported.")
                    exit(1)

            app1 = SymbolicApplication(
                app_id=1,
                local_state_schema=StateSchema(0, 0),
                global_state_schema=StateSchema(0, 0),
                approval_pgm_path=approval_pgm,
                clear_pgm_path=clear_pgm,
            )
            account1 = SymbolicAccount(address=str(addr1), balance=1000000000)
            account1.add_app(app1)
            proof.add_acct(account1)
            proof.add_precondition(
                KApply("_<=Int_", [KApply("_+Int_", [KVariable("A"), KVariable("B")]), KToken("MAX_UINT64", "Int")])
            )
            txn_pre = transaction_k_term(
                kavm=algod.kavm,
                txn=sdk_txn,
                txid='0',
                symbolic_fileds_subst=Subst(
                    {'APPLICATIONARGS_CELL': generate_tvalue_list(app_args), 'GROUPIDX_CELL': intToken(0)}
                ),
            )
            txn_post = transaction_k_term(
                kavm=algod.kavm,
                txn=sdk_txn,
                txid='0',
                symbolic_fileds_subst=Subst(
                    {
                        'APPLICATIONARGS_CELL': generate_tvalue_list(app_args),
                        'GROUPIDX_CELL': intToken(0),
                        'TXSCRATCH_CELL': KVariable('?_'),
                        'LOGDATA_CELL': KVariable('?FINAL_LOGDATA_CELL'),
                        'LOGSIZE_CELL': KVariable('?_'),
                        'RESUME_CELL': KVariable('?_'),
                    }
                ),
            )
            proof.add_txn(txn_pre, txn_post)
            # ensures ?FINAL_LOGDATA ==K b"\x15\x1f|u" +Bytes  padLeftBytes(Int2Bytes(A +Int B, BE, Unsigned), 8, 0)
            ensures = KApply(
                "_==K_",
                [
                    KVariable('?FINAL_LOGDATA_CELL'),
                    KApply(
                        '_+Bytes_',
                        [
                            bytesToken("\\x15\\x1f|u"),
                            KApply(
                                'padLeftBytes',
                                [
                                    KApply(
                                        'Int2Bytes',
                                        [
                                            KApply("_+Int_", [KVariable("A"), KVariable("B")]),
                                            KToken('BE', KSort('Endianness')),
                                            KToken('Unsigned', KSort('Signedness')),
                                        ],
                                    ),
                                    intToken(8),
                                    intToken(0),
                                ],
                            ),
                        ],
                    ),
                ],
            )
            proof.add_postcondition(ensures)
            proof.prove()
