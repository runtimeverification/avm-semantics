import typing

from algosdk.future.transaction import Transaction
from pyk.kast.inner import KApply, KToken, KVariable
from pyk.kast.outer import KClaim, KRewrite, read_kast_definition
from pyk.ktool.kprint import build_symbol_table, pretty_print_kast
from pyk.ktool.kprove import KProve
from collections import namedtuple 

PrePost = namedtuple('PrePost', ['pre', 'post'])

class SymbolicTransaction:

    def __init__(self, on_completion: int):
        self.tx_id = PrePost(
            KVariable("TX_ID_" + id(self)),
            KVariable("?TX_ID_" + id(self)),
        )
        self.sender = PrePost(
            KVariable("SENDER_" + id(self)),
            KVariable("?SENDER_" + id(self)),
        )
        self.type_enum = KToken("6", "Int")
        self.application_id = KVariable("APPLICATION_ID_" + id(self))
        self.on_completion = KToken(str(on_completion), "Int")

    def get_specific_field_pre(self):
        # if txn type is appl:
        return KApply(
            "<appCallTxFields>",
            [
                KApply("<applicationID>", self.application_id),
                KApply("<onCompletion>", self.on_completion),
            ],
        )

    def get_symbolic_config_pre(self):

        self._startconfig = KApply(
            "<transaction>",
            [
                KApply("<txID>", self.tx_id.pre),
                KApply(
                    "<txHeader>",
                    [
                        KApply("<fee>", KToken("0", "Int")),
                        KApply("<firstValid>", KToken("0", "Int")),
                        KApply("<lastValid>", KToken("0", "Int")),
                        KApply("<genesisHash>", KToken(".Bytes", "Bytes")),
                        KApply("<sender>", self.sender.pre),
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


class KAVMProof:
    def __init__(self):
        self._txns = []
        self._txns_post = []
        self._accts = []
        self._accts_post = []
        self._preconditions = []
        self._postconditions = []

    def add_txn(self, txn: SymbolicTransaction):
        self._txns.append(txn)

    def prove(self):
        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KToken(".K", "KItem")),  # TODO
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Failure - AVM is stuck\"", "String")),
                KApply("<returncode>", KToken("4", "Int")),
                KApply("<transactions>", KToken(".Bag", "TransactionCellMap")),  # TODO
                KApply(
                    "<avmExecution>",
                    [
                        KApply("<currentTx>", KToken("\"\"", "String")),  # TODO
                        KApply(
                            "<txnDeque>",
                            [
                                KApply("<deque>", KToken(".List", "List")),  # TODO
                                KApply("<dequeIndexSet>", KToken(".Set", "Set")),  # TODO
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
                        KApply("<accountsMap>", KToken(".Bag", "AccountsMapCell")),  # TODO
                        KApply("<appCreator>", KToken(".Map", "Map")),  # TODO
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
                KApply("<k>", KToken(".K", "KItem")),
                KApply("<panicstatus>", KToken("\"\"", "String")),
                KApply("<paniccode>", KToken("0", "Int")),
                KApply("<returnstatus>", KToken("\"Success - transaction group accepted\"", "String")),
                KApply("<returncode>", KToken("0", "Int")),
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

        requires = KToken("true", "Bool")
        ensures = KToken("true", "Bool")

        claim = KClaim(
            body=KRewrite(lhs, rhs),
            requires=requires,
            ensures=ensures,
        )

        #        print(claim)

        proof = KProve(definition_dir="tests/specs/verification-kompiled/")
        result = proof.prove_claim(claim=claim, claim_id="test")

        defn = read_kast_definition("tests/specs/verification-kompiled/parsed.json")
        symbol_table = build_symbol_table(defn)

        if type(result) is KApply and result.label.name == "#Top":
            print("Proved claim")
        else:
            print("Failed to prove claim")
            print("counterexample:")

            print(pretty_print_kast(result, symbol_table=symbol_table))


def main():

    proof = KAVMProof()
    proof.prove()


if __name__ == "__main__":
    main()
