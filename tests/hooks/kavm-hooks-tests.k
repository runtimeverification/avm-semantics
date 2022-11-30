requires "krypto.md"

module KAVM-HOOKS-TESTS
  imports INT
  imports BYTES
  imports STRING
  imports KRYPTO

  syntax Bytes  ::= DecodeAddressString(String) [function]
  syntax String ::= EncodeAddressBytes(Bytes)   [function]
  // -----------------------------------------------------
  rule DecodeAddressString(S) => DecodeAddressStringInternal(S) requires IsAddressValid(S)
  rule EncodeAddressBytes(B)  => EncodeAddressBytesInternal(B)  requires lengthBytes(B)  ==Int 32

  syntax Bytes  ::= DecodeAddressStringInternal(String) [function, hook(KAVM.address_decode)]
  syntax String ::= EncodeAddressBytesInternal(Bytes)   [function, hook(KAVM.address_encode)]
  syntax Bool   ::= IsAddressValid(String)              [function, hook(KAVM.check_address)]

  syntax Bytes  ::= Base64Decode(String) [function, hook(KAVM.b64_decode)]
  syntax String ::= Base64Encode(Bytes)  [function, hook(KAVM.b64_encode)]

endmodule