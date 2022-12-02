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


class KAVMTransaction:
    def __init__(
        self,
        txn_id: KInner,
        program_file: Path,
        args: List[str],
        foreign_accts: List[str],
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
                KApply("<args>", KToken(".BytesList", "BytesList")),
                KApply("<foreignAccounts>", KToken(".BytesList", "BytesList")),
            ],
        )


class KAVMAccount:
    def __init__(
        self,
        address: KInner,
        balance: KInner,
    ):
        self._address = address
        self._balance = balance

    def to_kast(self):
        return KApply(
            "<account>",
            [
                KApply("<address>", self._address),
                KApply("<balance>", self._balance),
            ],
        )


class KAVMProof:
    def __init__(self):
        print("__init__")
        self._txns = []
        self._accts = []

    def add_txn(self, txn: KAVMTransaction):
        print("add_txn")
        self._txns.append(txn.to_kast())

    def add_acct(self, acct: KAVMAccount):
        print("add_acct")
        self._accts.append(acct.to_kast())

    def add_postcondition(self):
        print("not implemented.")

    def prove(self):
        print("prove")

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
                KApply("<k>", KToken(".", "K")),
                KApply("<stack>", KToken(".TStack", "TStack")),
                KApply("<pc>", KToken("0", "Int")),
                KApply("<program>", KToken(".Map", "Map")),
                KApply("<currentTx>", KToken('""', "String")),
                transactions_kast,
                accounts_kast,
            ],
        )

        claim = KClaim(
            body=KRewrite(lhs, rhs),
            #            requires=requires,
            #            ensures=ensures
        )

        proof = KProve(definition_dir="verification-kompiled/")
        result = proof.prove_claim(claim=claim, claim_id="test")

        defn = read_kast_definition("verification-kompiled/parsed.json")
        symbol_table = build_symbol_table(defn)
        print(pretty_print_kast(result, symbol_table=symbol_table))


def main():

    txn = KAVMTransaction(
        txn_id=KVariable("TX_ID"),
        program_file="test.teal",
        args=[],
        foreign_accts=[],
    )

    acct1 = KAVMAccount(
        address=KVariable("ACCT1_ADDR"),
        balance=KVariable("ACCT1_BAL"),
    )
    acct2 = KAVMAccount(
        address=KVariable("ACCT2_ADDR"),
        balance=KVariable("ACCT2_BAL"),
    )

    kavm_proof = KAVMProof()
    kavm_proof.add_txn(txn)
    kavm_proof.add_acct(acct1)
    kavm_proof.add_acct(acct2)
    kavm_proof.add_postcondition()
    kavm_proof.prove()


if __name__ == "__main__":
    main()
