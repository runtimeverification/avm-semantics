from pathlib import Path
from typing import Final, List, Sequence
from unittest import TestCase

from pyk.kast import KApply, KVariable

from ..teal_to_k import KAVM


def _strip_path_suffix(path1: Path, path2: Path) -> Path:

    def strip_seq_suffix(seq1: Sequence, seq2: Sequence) -> List:
        len1 = len(seq1)
        len2 = len(seq2)

        if len1 < len2:
            raise ValueError('Length of second sequence should be at most {len1}, found: {len2}')

        expected_suffix = list(seq2)
        actual_suffix = list(seq1[-len2:])

        if expected_suffix != actual_suffix:
            raise ValueError(f'Suffix of first sequence is expected to be {expected_suffix}, found: {actual_suffix}')

        return list(seq1[:len1 - len2])

    return Path(*strip_seq_suffix(path1.parts, path2.parts))


TEST_DIR: Final = Path(__file__).parent
REL_TEST_DIR: Final = Path('kavm_pyk/src/kavm_pyk/tests')
ROOT_DIR = _strip_path_suffix(TEST_DIR, REL_TEST_DIR)
KOMPILED_DIR = ROOT_DIR / '.build/usr/lib/kavm/avm-llvm/avm-execution-kompiled'


class PrintTest(TestCase):
    TEST_DATA = (
        (KApply('_+Int_', [KVariable('x'), KVariable('y')]), '( x +Int y )'),
    )

    def setUp(self):
        self.kavm = KAVM(KOMPILED_DIR)

    def test_print(self):
        for i, [term, expected_str] in enumerate(self.TEST_DATA):
            with self.subTest(i=i):
                # Given
                expected = expected_str.split()

                # When
                actual = self.kavm.prettyPrint(term).split()

                # Then
                self.assertListEqual(expected, actual)
