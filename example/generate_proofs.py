import json
from pathlib import Path
from typing import List

from pyk.cli_utils import run_process
from pyk.kast.inner import KApply, KAst, KInner, KLabel, KToken, KVariable, build_assoc
from pyk.kast.outer import KClaim, KRewrite, read_kast_definition
from pyk.kore.syntax import Kore
from pyk.ktool.kprint import build_symbol_table, pretty_print_kast
from pyk.ktool.kprove import KProve


def parse_program(file: Path):
    kast_command = ["kast", "--output", "json"]
    kast_command += [file]
    result = run_process(kast_command)
    return KInner.from_dict(json.loads(result.stdout)["term"])


def python_list_to_bytes_list(bl: List[KInner]):
    if bl == []:
        return KToken(".BytesList", "BytesList")
    else:
        return KApply(
            "___KAVM-MINI_BytesList_Bytes_BytesList",
            bl[0],
            python_list_to_bytes_list(bl[1:]),
        )


class KAVMTransaction:
    def __init__(
        self,
        txn_id: KInner,
        program_file: Path,
        args: List[KInner],
        foreign_accts: List[KInner],
    ):
        self._txn_id = txn_id
        self._args = args
        self._foreign_accts = foreign_accts
        self._program = parse_program(program_file)

    def to_dict(self):
        return {
            "txn_id": self._txn_id,
            "args": self._args,
            "foreign_accts": self._foreign_accts,
            "program": self._program,
        }

    def to_kast(self):
        return KApply(
            "<transaction>",
            [
                KApply("<txID>", self._txn_id),
                KApply("<pgm>", self._program),
                KApply("<args>", python_list_to_bytes_list(self._args)),
                KApply(
                    "<foreignAccounts>", python_list_to_bytes_list(self._foreign_accts)
                ),
            ],
        )

    def to_kast_post(self):
        return KApply(
            "<transaction>",
            [
                KApply("<txID>", self._txn_id),
                KApply("<pgm>", self._program),
                KApply("<args>", python_list_to_bytes_list(self._args)),
                KApply(
                    "<foreignAccounts>", python_list_to_bytes_list(self._foreign_accts)
                ),
            ],
        )


class KAVMAccount:
    def __init__(
        self,
    ):
        ...

    def address(self):
        return {
            "pre": KVariable("ADDRESS_" + str(id(self))),
            "post": KVariable("?ADDRESS_" + str(id(self))),
        }

    def balance(self):
        return {
            "pre": KVariable("BALANCE_" + str(id(self))),
            "post": KVariable("?BALANCE_" + str(id(self))),
        }

    def to_kast(self):
        return KApply(
            "<account>",
            [
                KApply("<address>", self.address()["pre"]),
                KApply("<balance>", self.balance()["pre"]),
            ],
        )

    def to_kast_post(self):
        return KApply(
            "<account>",
            [
                KApply("<address>", self.address()["post"]),
                KApply("<balance>", self.balance()["post"]),
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

    def add_txn(self, txn: KAVMTransaction):
        self._txns.append(txn.to_kast())
        self._txns_post.append(txn.to_kast_post())

    def add_acct(self, acct: KAVMAccount):
        self._accts.append(acct.to_kast())
        self._accts_post.append(acct.to_kast_post())

    def add_precondition(self, pc: KInner):
        self._preconditions.append(pc)

    def add_postcondition(self, pc: KInner):
        self._postconditions.append(pc)

    def prove(self):

        transactions_kast = KApply(
            "<transactions>",
            [
                build_assoc(
                    KApply(".TransactionCellMap"),
                    KLabel("_TransactionCellMap_"),
                    self._txns,
                )
            ],
        )

        accounts_kast = KApply(
            "<accounts>",
            [
                build_assoc(
                    KApply(".AccountCellMap"),
                    KLabel("_AccountCellMap_"),
                    self._accts,
                )
            ],
        )

        transactions_kast_post = KApply(
            "<transactions>",
            [
                build_assoc(
                    KApply(".TransactionCellMap"),
                    KLabel("_TransactionCellMap_"),
                    self._txns_post,
                )
            ],
        )

        accounts_kast_post = KApply(
            "<accounts>",
            [
                build_assoc(
                    KApply(".AccountCellMap"),
                    KLabel("_AccountCellMap_"),
                    self._accts_post,
                )
            ],
        )

        lhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KApply("#executeTxn", KVariable("TX_ID"))),
                KApply("<stack>", KToken(".TStack", "TStack")),
                KApply("<pc>", KToken("0", "Int")),
                KApply("<program>", KToken(".Map", "Map")),
                KApply("<currentTx>", KToken('""', "String")),
                transactions_kast,
                accounts_kast,
            ],
        )
        rhs = KApply(
            "<kavm>",
            [
                KApply("<k>", KToken(".K", "K")),
                KApply("<stack>", KVariable("?_")),
                KApply("<pc>", KVariable("?_")),
                KApply("<program>", KVariable("?_")),
                KApply("<currentTx>", KVariable("?_")),
                transactions_kast_post,
                accounts_kast_post,
            ],
        )

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

        proof = KProve(definition_dir="verification-kompiled/")
        result = proof.prove_claim(claim=claim, claim_id="test")

        defn = read_kast_definition("verification-kompiled/parsed.json")
        symbol_table = build_symbol_table(defn)

        if type(result) is KApply and result.label.name == "#Top":
            print("Proved claim")
        else:
            print("Failed to prove claim")
            print("counterexample:")

            for condition in flatten_conditions(result):
                print(pretty_print_kast(condition, symbol_table=symbol_table))

        # print(pretty_print_kast(result, symbol_table=symbol_table))


def flatten_conditions(term: KInner):
    if term.label.name == "#And":
        return flatten_conditions(term.args[0]) + flatten_conditions(term.args[1])
    if term.label.name == "<generatedTop>":
        return []
    else:
        return [term]


def int_2_bytes(term: KInner):
    return KApply(
        "Int2Bytes",
        [
            term,
            KToken("BE", "Endianness"),
            KToken("Unsigned", "Signedness"),
        ],
    )


def equals(a1: KInner, a2: KInner):
    return KApply("_==K_", [a1, a2])


def nequals(a1: KInner, a2: KInner):
    return KApply("_=/=K_", [a1, a2])


def gt(a1: KInner, a2: KInner):
    return KApply("_>Int_", [a1, a2])


def add(a1: KInner, a2: KInner):
    return KApply("_+Int_", [a1, a2])


def kvar(name: str):
    return KVariable(name)


def main():

    acct1 = KAVMAccount()
    acct2 = KAVMAccount()

    txn = KAVMTransaction(
        txn_id=KVariable("TX_ID"),
        program_file="test.teal",
        args=[
            int_2_bytes(kvar("ARG1")),
            int_2_bytes(kvar("ARG2")),
        ],
        foreign_accts=[acct1.address()["pre"], acct2.address()["pre"]],
    )

    kavm_proof = KAVMProof()
    kavm_proof.add_txn(txn)
    kavm_proof.add_acct(acct1)
    kavm_proof.add_acct(acct2)

    kavm_proof.add_precondition(nequals(acct1.address()["pre"], acct2.address()["pre"]))
    kavm_proof.add_precondition(
        gt(acct1.balance()["pre"], add(kvar("ARG1"), kvar("ARG2")))
    )
#    kavm_proof.add_precondition(
#        gt(KToken("MAX_UINT_64", "Int"), add(kvar("ARG1"), kvar("ARG2")))
#    )

    kavm_proof.add_postcondition(
        equals(
            acct2.balance()["post"],
            add(acct2.balance()["pre"], add(kvar("ARG1"), kvar("ARG2"))),
        )
    )
    kavm_proof.prove()


if __name__ == "__main__":
    main()
