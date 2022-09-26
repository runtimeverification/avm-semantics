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


def test_sha256() -> None:
    c_pgm = f'Sha256("")'
    assert _krun(c_pgm) == f'"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"' + ' ~> .'

def test_sha512_256() -> None:
    c_pgm = f'Sha512_256("")'
    assert _krun(c_pgm) == f'"c672b8d1ef56ed28ab87c3622c5114069bdd3ad7b8f9737498d0c01ecef0967a"' + ' ~> .'

def test_keccak256() -> None:
    c_pgm = f'Keccak256("")'
    assert _krun(c_pgm) == f'"c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"' + ' ~> .'

