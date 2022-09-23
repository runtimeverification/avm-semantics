import re
import subprocess
import pytest


def get_k_cell(str_term: str) -> str:
    '''Extract the contects of the K cell with a regular expression'''
    pattern = re.compile(r'<k>\s*(.*)\s*</k>')
    k_cell = pattern.search(str_term).group(1)
    return k_cell


def _krun(c_pgm: str) -> str:
    '''Execute krun and return the contents of the K cell'''
    command = ['krun', f'-cPGM={c_pgm}']
    res = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
    return get_k_cell(res.stdout)


ZERO_ADDRESS = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ'
INVALID_ADDRESS_TOO_SHORT = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFK'
INVALID_ADDRESS_TOO_LONG = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQQ'


@pytest.mark.parametrize(
    'address_literal,expected',
    [
        (ZERO_ADDRESS, 'true ~> .'),
        (INVALID_ADDRESS_TOO_SHORT, 'false ~> .'),
        (INVALID_ADDRESS_TOO_LONG, 'false ~> .'),
    ],
)
def test_is_address_valid(address_literal: str, expected: bytes) -> None:
    c_pgm = f'IsAddressValid("{address_literal}")'
    assert _krun(c_pgm) == expected


@pytest.mark.parametrize('address_literal', [ZERO_ADDRESS])
def test_decode_encode_address_string(address_literal: str) -> None:
    c_pgm = f'EncodeAddressBytes(DecodeAddressString("{address_literal}"))'
    assert _krun(c_pgm) == f'"{address_literal}"' + ' ~> .'
