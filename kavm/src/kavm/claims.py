import typing
from pathlib import Path
from algosdk.future.transaction import Transaction
import json
from pyk.kast.inner import KApply, KToken, KVariable, KLabel, build_assoc, KSort, KInner
from pyk.kast.outer import KClaim, KRewrite, read_kast_definition
from pyk.ktool.kprint import build_symbol_table, pretty_print_kast
from pyk.ktool.kprove import KProve
from collections import namedtuple 
from algosdk.future.transaction import ApplicationCallTxn, StateSchema
from algosdk.abi.contract import Contract
from pyk.cli_utils import run_process

from pyk.prelude.bytes import bytesToken

from pyteal import Mode
from pyteal import compileTeal
from typing import Optional

PrePost = namedtuple('PrePost', ['pre', 'post'])

def parse_program(file: Optional[Path]):
    if not(file):
        return KApply(label=KLabel(name='int__TEAL-OPCODES_PseudoOpCode_PseudoTUInt64', params=()), args=(KToken(token='1', sort=KSort(name='Int')),))

    kast_command = ["kast", "--output", "json", "--definition",
            ".build/usr/lib/kavm/avm-llvm/avm-testing-kompiled", "--sort", "TealInputPgm", "--module",
            "TEAL-PARSER-SYNTAX"]
    kast_command += [file]
    result = run_process(kast_command)
    return KInner.from_dict(json.loads(result.stdout)["term"])



#class SymbolicApplTxn(ApplicationCallTxn):
class SymbolicApplTxn:
    def __init__(
        self,
        sender: str,
        #        sp,
        index: int,
        on_complete: int,
        local_schema: StateSchema = StateSchema(0, 0),
        global_schema: StateSchema = StateSchema(0, 0),
        approval_program_path: Optional[Path] = None,
        clear_program_path: Optional[Path] = None,
#        num_app_args: int = 0,
        num_accounts: int = 0,
        num_foreign_apps: int = 0,
        num_foreign_assets: int = 0,
        note=None,
        lease=None,
        rekey_to=None,
        extra_pages: int = 0,
        boxes=None,
    ):
        self.sender = KToken("b\"" + sender + "\"", "Bytes")
        self.index = KToken(str(index), "Int")
        self.on_complete = KToken(str(on_complete), "Int")
        self.num_accounts = num_accounts
        self.approval_program_path = approval_program_path
        self.clear_program_path = clear_program_path
#        self.num_app_args = num_app_args
        self.num_foreign_apps = num_foreign_apps
        self.num_foreign_assets = num_foreign_assets
        self.local_schema = local_schema
        self.global_schema = global_schema
        self.extra_pages = extra_pages
        self.app_args = []

    def add_app_arg(self, arg: KInner):
        self.app_args.append(arg)

    def generate_vars(self, num: int, name: str, sort: str):
        def generate_vars_recursive(obj_id: int, next: int, num: int, name: str, sort: str):
            if next >= num:
                return KVariable(name + "_ETC_" + str(obj_id), sort=KSort("TValueNeList"))
            else:
                return KApply(
                    "___TEAL-TYPES-SYNTAX_TValueNeList_TValue_TValueNeList", 
                    [
                        KVariable(name + "_" + str(next) + "_" + str(obj_id), sort=KSort(sort)),
                        generate_vars_recursive(obj_id, next + 1, num, name, sort),
                    ]
                )
        return generate_vars_recursive(id(self), 0, num, name, sort)
    
    def generate_tvalue_list(self, tvlist):
        if len(tvlist) == 1:
            return tvlist[0]
        else:
            return KApply(
                "___TEAL-TYPES-SYNTAX_TValueNeList_TValue_TValueNeList", 
                [
                    tvlist[0],
                    self.generate_tvalue_list(tvlist[1:]),
                ]
            )

    def get_specific_field_pre(self):
        return KApply(
            "<appCallTxFields>",
            [
                KApply("<applicationID>", self.index),
                KApply("<onCompletion>", self.on_complete),
                KApply("<accounts>", self.generate_vars(num=self.num_accounts, name="ACCTS", sort="Bytes")),
                KApply("<approvalProgramSrc>", parse_program(self.approval_program_path)),
                KApply("<clearStateProgramSrc>", parse_program(self.clear_program_path)),
                KApply("<approvalProgram>", KToken(".Bytes", "Bytes")),
                KApply("<clearStateProgram>", KToken(".Bytes", "Bytes")),
                KApply("<applicationArgs>", self.generate_tvalue_list(self.app_args)),
                KApply("<foreignApps>", self.generate_vars(num=self.num_foreign_apps, name="FOREIGN_APPS",
                    sort="Int")),
                KApply("<foreignAssets>", self.generate_vars(num=self.num_foreign_assets, name="FOREIGN_ASSETS",
                    sort="Int")),
                KApply("<boxReferences>", KToken(".TValuePairList", "TValuePairList")),
                KApply(
                    "<globalStateSchema>",
                    [
                        KApply("<globalNui>", KToken(str(self.global_schema.num_uints), "Int")),
                        KApply("<globalNbs>", KToken(str(self.global_schema.num_byte_slices), "Int")),
                    ],
                ),
                KApply(
                    "<localStateSchema>",
                    [
                        KApply("<localNui>", KToken(str(self.local_schema.num_uints), "Int")),
                        KApply("<localNbs>", KToken(str(self.local_schema.num_byte_slices), "Int")),
                    ],
                ),
                KApply("<extraProgramPages>", KToken(str(self.extra_pages), "Int"))
            ],
        )

    def get_symbolic_config_pre(self):

        return KApply(
            "<transaction>",
            [
                KApply("<txID>", KToken("\"0\"", "String")),
                KApply(
                    "<txHeader>",
                    [
                        KApply("<fee>", KToken("0", "Int")),
                        KApply("<firstValid>", KToken("0", "Int")),
                        KApply("<lastValid>", KToken("0", "Int")),
                        KApply("<genesisHash>", KToken(".Bytes", "Bytes")),
                        KApply("<sender>", self.sender),
                        KApply("<txType>", KToken("\"appl\"", "String")), # TODO
                        KApply("<typeEnum>", KToken("6", "Int")),
                        KApply("<groupID>", KToken("\"\"", "String")),
                        KApply("<groupIdx>", KToken("0", "Int")),
                        KApply("<genesisID>", KToken(".Bytes", "Bytes")),
                        KApply("<lease>", KToken(".Bytes", "Bytes")),
                        KApply("<note>", KToken(".Bytes", "Bytes")),
                        KApply("<rekeyTo>", KToken(".Bytes", "Bytes")),
                    ],
                ),
                KApply("<txnTypeSpecificFields>", self.get_specific_field_pre()),
                KApply(
                    "<applyData>",
                    [
                        KApply("<txScratch>", KToken(".Map", "Map")),
                        KApply("<txConfigAsset>", KToken("0", "Int")),
                        KApply("<txApplicationID>", KToken("0", "Int")),
                        KApply(
                            "<log>",
                            [
                                KApply("<logData>", KToken(".TValueList", "TValueList")),
                                KApply("<logSize>", KToken("0", "Int")),
                            ],
                        ),
                    ],
                ),
                KApply("<txnExecutionContext>", KToken(".K", "KItem")),
                KApply("<resume>", KToken("false", "Bool")),
            ],
        )

    def get_symbolic_config_post(self):

        return KApply(
            "<transaction>",
            [
                KApply("<txID>", KToken("\"0\"", "String")),
                KApply(
                    "<txHeader>",
                    [
                        KApply("<fee>", KToken("0", "Int")),
                        KApply("<firstValid>", KToken("0", "Int")),
                        KApply("<lastValid>", KToken("0", "Int")),
                        KApply("<genesisHash>", KToken(".Bytes", "Bytes")),
                        KApply("<sender>", self.sender),
                        KApply("<txType>", KToken("\"\"", "String")), # TODO
                        KApply("<typeEnum>", KToken("0", "Int")),
                        KApply("<groupID>", KToken("\"\"", "String")),
                        KApply("<groupIdx>", KToken("0", "Int")),
                        KApply("<genesisID>", KToken(".Bytes", "Bytes")),
                        KApply("<lease>", KToken(".Bytes", "Bytes")),
                        KApply("<note>", KToken(".Bytes", "Bytes")),
                        KApply("<rekeyTo>", KToken(".Bytes", "Bytes")),
                    ],
                ),
                KApply("<txnTypeSpecificFields>", self.get_specific_field_pre()),
                KApply(
                    "<applyData>",
                    [
                        KApply("<txScratch>", KToken(".Map", "Map")),
                        KApply("<txConfigAsset>", KToken("0", "Int")),
                        KApply("<txApplicationID>", KToken("0", "Int")),
                        KApply(
                            "<log>",
                            [
                                KApply("<logData>", KVariable("LOG" + str(id(self)))),
                                KApply("<logSize>", KVariable("?_")),
                            ],
                        ),
                    ],
                ),
                KApply("<txnExecutionContext>", KToken(".K", "KItem")),
                KApply("<resume>", KToken("false", "Bool")),
            ],
        )

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
        self.labels = []

    def convert_labels_to_vars(self, term: KInner):

        def hex_token_to_k_string(ht: str):
            string = ""
            for i in range(0, len(ht), 2):
                string += "\\x"
                string += ht[i] + ht[i+1]
            return string

        if type(term) is KApply:
            if len(term.args) == 0:
                return term
            else:
                result = KApply(label=term.label, args=[self.convert_labels_to_vars(arg) for arg in term.args])
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

    def get_config(self):
        return KApply(
            "<app>",
            [
                KApply("<appID>", KToken(str(self.app_id), "Int")),
                KApply("<approvalPgmSrc>", self.convert_labels_to_vars(parse_program(self.approval_pgm_path))),
                KApply("<clearStatePgmSrc>", self.convert_labels_to_vars(parse_program(self.clear_pgm_path))),
                KApply("<approvalPgm>", KToken(".Bytes", "Bytes")),
                KApply("<clearStatePgm>", KToken(".Bytes", "Bytes")),
                KApply(
                    "<globalState>",
                    [
                        KApply("<globalNumInts>", KToken(str(self.global_state_schema.num_uints), "Int")),
                        KApply("<globalNumBytes>", KToken(str(self.global_state_schema.num_byte_slices), "Int")),
                        KApply("<globalInts>", KToken(".Map", "Map")),
                        KApply("<globalBytes>", KToken(".Map", "Map")),
                    ]
                ),
                KApply(
                    "<localState>",
                    [
                        KApply("<localNumInts>", KToken(str(self.local_state_schema.num_uints), "Int")),
                        KApply("<localNumBytes>", KToken(str(self.local_state_schema.num_byte_slices), "Int")),
                    ]
                ),
                KApply("<extraPages>", KToken("0", "Int")),
            ]
        )

class SymbolicAccount:
    def __init__(
        self,
        address: str,
        balance: int,
    ):
        self.address = KToken("b\"" + address + "\"", "Bytes")
        self.balance = KToken(str(balance), "Int")
        self.apps_config = []
        self.apps = []

    def add_app(self, application: SymbolicApplication):
        self.apps_config.append(application.get_config())
        self.apps.append(application)

    def build_created_apps(self):
        return build_assoc(
            KApply(".AppCellMap"),
            KLabel("_AppCellMap_"),
            self.apps_config,
        )

    def get_symbolic_config_pre(self):
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
                KApply("<boxes>", KToken(".Bag", "BoxMapCell"))
            ]
        )

class KAVMProof:
    def __init__(self):
        self._txns = []
        self._txn_ids = []
        self._txns_post = []
        self._accts = []
        self._accts_config = []
        self._accts_post = []
        self._preconditions = []
        self._postconditions = []

    def add_txn(self, txn: SymbolicApplTxn):
        self._txns.append(txn.get_symbolic_config_pre())

    def add_acct(self, acct: SymbolicAccount):
        self._accts_config.append(acct.get_symbolic_config_pre())
        self._accts.append(acct)

    def build_app_creator_map(self):
        creator_map = []
        for acct in self._accts:
            print(acct)
            for app in acct.apps:
                creator_map.append(KApply("_|->_", [KToken(str(app.app_id), "Int"), acct.address]))
        return build_assoc(
            KApply(".Map"),
            KLabel("_Map_"),
            creator_map
        )

    def build_transactions(self):
        return build_assoc(
            KApply(".TransactionCellMap"),
            KLabel("_TransactionCellMap_"),
            self._txns,
        )

    def build_accounts(self):
        return build_assoc(
            KToken(".Bag", "AccountCellMap"),
            KLabel("_AccountCellMap_"),
            self._accts_config,
        )

    def build_deque(self):
        return build_assoc(
            KApply(".List"),
            KLabel("_List_"),
            [KApply("ListItem", KToken("\"" + str(i) + "\"", "Int")) for i in range(0, len(self._txns))]
        )

    def build_deque_set(self):
        return build_assoc(
            KApply(".Set"),
            KLabel("_Set_"),
            [KApply("SetItem", KToken("\"" + str(i) + "\"", "Int")) for i in range(0, len(self._txns))]
        )

    def prove(self):

        defn = read_kast_definition("tests/specs/verification-kompiled/parsed.json")
        symbol_table = build_symbol_table(defn)

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#evalTxGroup")),  # TODO
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Failure - AVM is stuck\"", "String")),
                KApply("<returncode>", KToken("4", "Int")),
                KApply("<transactions>", [self.build_transactions()]),  # TODO
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KToken("\"\"", "String")),  # TODO
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", self.build_deque()),  # TODO
                                KApply("<dequeIndexSet>", self.build_deque_set()),  # TODO
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
                        KApply("<accountsMap>", self.build_accounts()),  # TODO
                        KApply("<appCreator>", self.build_app_creator_map()),  # TODO
                        KApply("<assetCreator>", KToken(".Map", "Map")),  # TODO
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", KToken("0", "Int")),
                        KApply("<nextTxnID>", KToken("0", "Int")),
                        KApply("<nextAppID>", KToken("1", "Int")),
                        KApply("<nextAssetID>", KToken("1", "Int")),
                        KApply("<nextGroupID>", KToken("0", "Int")),
                        KApply("<txnIndexMap>", KToken(".Bag", "TxnIndexMapGroupCell")),  # TODO
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),
            ],
        )

        rhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KToken("1", "Int")),
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", KToken("1234123", "Int")),
                KApply("<transactions>", KVariable("?_")),
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
                        KApply("<accountsMap>", KToken(".Bag", "AccountsMapCell")),  # TODO
                        KApply("<appCreator>", KToken(".Map", "Map")),  # TODO
                        KApply("<assetCreator>", KToken(".Map", "Map")),  # TODO
                        KApply("<blocks>", KToken(".Map", "Map")),
                        KApply("<blockheight>", KToken("0", "Int")),
                        KApply("<nextTxnID>", KVariable("?_")),
                        KApply("<nextAppID>", KVariable("?_")),
                        KApply("<nextAssetID>", KVariable("?_")),
                        KApply("<nextGroupID>", KVariable("?_")),
                        KApply("<txnIndexMap>", KVariable("?_")),
                    ],
                ),
                KApply("<tealPrograms>", KToken(".Map", "Map")),  # TODO
            ],
        )

        def remove_duplicates(labels):
            return [*set(labels)]

        for account in self._accts:
            for app in account.apps:
                app.labels = remove_duplicates(app.labels)
                for i in range(len(app.labels)):
                    for j in range(len(app.labels)):
                        if i == j:
                            continue
                        self._preconditions.append(KApply("_=/=K_", [app.labels[i], app.labels[j]]))

        requires = build_assoc(
            KToken("true", "Bool"), KLabel("_andBool_"), self._preconditions
        )

        ensures = build_assoc(
            KToken("true", "Bool"), KLabel("_andBool_"), self._postconditions
        )

        claim = KClaim(
            body=KRewrite(lhs, rhs),
            requires=requires,
            ensures=ensures,
        )

        print(claim)

        proof = KProve(definition_dir="tests/specs/verification-kompiled/", use_directory=Path("proofs"))
        result = proof.prove_claim(claim=claim, claim_id="test")

        if type(result) is KApply and result.label.name == "#Top":
            print("Proved claim")
        else:
            print("Failed to prove claim")
            print("counterexample:")

            print(pretty_print_kast(result, symbol_table=symbol_table))

def int_2_bytes(term: KInner):
    return KApply(
        "Int2Bytes",
        [
            term,
            KToken("BE", "Endianness"),
            KToken("Unsigned", "Signedness"),
        ],
    )


class AutoProver:
    def __init__(
        self,
        approval_pgm: Path,
        clear_pgm: Path,
        contract: Contract,
    ):

        for method in contract.methods:
            proof = KAVMProof()
            txn = SymbolicApplTxn(sender="test", index=1, on_complete=0)
            app1 = SymbolicApplication(
                app_id = 1,
                local_state_schema = StateSchema(0, 0),
                global_state_schema = StateSchema(0, 0),
                approval_pgm_path=approval_pgm,
                clear_pgm_path=clear_pgm,
            )
            account1 = SymbolicAccount(
                address="acct1_addr",
                balance=1000000000
            )
            account1.add_app(app1)
            proof.add_acct(account1)
            txn.add_app_arg(KToken("b\"" + str(method.get_selector()) + "\"", "Bytes"))
            for arg in method.args:
                print("test")
                print(arg.type)
                print(type(arg.type))
                if str(arg.type) == 'uint64':
                    txn.add_app_arg(int_2_bytes(KVariable(str(arg.name).upper(), sort=KSort("Int"))))
                else:
                    print("Not yet supported.")
                    exit(1)
            proof.add_txn(txn)
            proof.prove()


def main():

    txn = SymbolicApplTxn(
        sender = "test",
        index = 1,
        on_complete = 0,
        local_schema = StateSchema(0, 0),
        global_schema = StateSchema(0, 0),
        approval_program_path="tests/teal-sources/test.teal",
        clear_program_path="tests/teal-sources/test.teal",
#        num_app_args=2
    )

    app1 = SymbolicApplication(
        app_id = 1,
        local_state_schema = StateSchema(0, 0),
        global_state_schema = StateSchema(0, 0),
        approval_pgm_path="tests/teal-sources/test.teal",
        clear_pgm_path="tests/teal-sources/test.teal",
    )

    account1 = SymbolicAccount(
        address="acct1_addr",
        balance=1000000000
    )
    account1.add_app(app1)

    print(account1.get_symbolic_config_pre())

    proof = KAVMProof()
    proof.add_acct(account1)
    proof.add_txn(txn)

    proof.prove()

if __name__ == "__main__":
    main()
