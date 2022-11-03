TEAL Type Specification
=======================

```k
module TEAL-TYPES-SYNTAX
  import INT-SYNTAX
  import STRING-SYNTAX
```

TEAL Literal Representation
---------------------------

There are only two types in TEAL:

1.  `uint64`, i.e., 64-bit unsigned integers, represented using K's `Int` type:

    ```k
    syntax TUInt64 ::= Int
    ```

2. `uint8`, i.e., 8-bit unsigned integers, represented using K's `Int` type:

    ```k
    syntax TUInt8 ::= Int
    ```

3.  `bytes`, i.e., byte arrays, represented using K's `Bytes` type. Note there
    are several representations of byte constants in TEAL:

    - base64 and base32 encoded sequences,
    - `0x`-prefixed hexadecimal values,
    - and string literals.

    ```k
    syntax B64Encoded      [token]
    syntax B32Encoded      [token]
    syntax HexToken        [token]
    syntax TAddressLiteral [token]

    syntax TBytes ::= TBytesLiteral
                    | TAddressLiteral

    syntax TBytesLiteral ::= "base64" B64Encoded
                           | "b64"    B64Encoded
                           | "base64" "(" B64Encoded ")"
                           | "b64"    "(" B64Encoded ")"
                           | "base32" B32Encoded
                           | "b32"    B32Encoded
                           | "base32" "(" B32Encoded ")"
                           | "b32"    "(" B32Encoded ")"
                           | HexToken
                           | String
    ```

TEAL TValue Representation
--------------------------

The `TValue` sort represents all possible TEAL values.

```k
  syntax TValue ::= TUInt64 | TBytes
  syntax TValueNeList ::= TValue | TValue TValueNeList
  syntax TValueList ::= ".TValueList" [klabel(.TValueList), symbol] | TValueNeList
  syntax MaybeTValue ::= "NoTValue" [klabel(NoTValue), symbol] | TValue

  syntax TValuePair ::= "(" TValue "," TValue ")"
  syntax TValuePairNeList ::= TValuePair | TValuePair TValuePairNeList
  syntax TValuePairList ::= ".TValuePairList" | TValuePairNeList
  syntax MaybeTValuePair ::= "NoTValuePair" | TValuePair
```

```k
endmodule
```

TEAL Type Processing
--------------------

```k
module TEAL-TYPES
  import TEAL-TYPES-SYNTAX
  import BOOL
  import K-EQUAL
  import BYTES
  import INT
  import STRING
  import KRYPTO
```

### Type Representation

Here we define our internal type representations.

Our unsigned integers have maximum values.

```k
  syntax Int ::= "MAX_UINT8"   [macro]
               | "MAX_UINT64"  [macro]
               | "MAX_UINT128" [macro]
  // ---------------------------------
  rule MAX_UINT8   => 255                                     // 2 ^Int 8   -Int 1
  rule MAX_UINT64  => 18446744073709551615                    // 2 ^Int 64  -Int 1
  rule MAX_UINT128 => 340282366920938463463374607431768211455 // 2 ^Int 128 -Int 1
```

Longer 128-bit Integers may need to be broken down into two 64-bit integers (to be able to store
them on the stack). This is facilitated by two operations:

1.  Computing the lower 64-bit segment of an unsigned 128-bit integer

    ```k
      syntax Int ::= lowerU64(Int) [function]
      rule lowerU64(I) => I &Int MAX_UINT64
    ```

2.  Computing the upper 64-bit segment of an unsigned 128-bit integer

    ```k
      syntax Int ::= upperU64(Int) [function]
      rule upperU64(I) => I >>Int 64
    ```


All `TBytes` literals are interpreted into the K `Bytes` type.

```k
  syntax TBytes ::= Bytes

  syntax Bytes ::= normalizeB(TBytes) [function]
  // -------------------------------------------
  rule normalizeB(B:Bytes)  => B
  rule normalizeB(S:String) => String2Bytes(S)
  rule normalizeB(H:HexToken) => prepBytesString(Hex2String(H))
  rule normalizeB(TA:TAddressLiteral) => DecodeAddressString(TealAddress2String(TA))

  syntax Bytes ::= prepBytesString(String) [function]
  // ------------------------------------------------
  rule prepBytesString(S:String) => #ParseBytes(substrString(S, 2, lengthString(S)), .Bytes)

  syntax Bytes ::= #ParseBytes(String, Bytes) [function]
  // ---------------------------------------------------
  rule #ParseBytes("", ByteStr) => ByteStr
  rule #ParseBytes(Hex, ByteStr)
    => #ParseBytes(substrString(Hex, 2, lengthString(Hex)),
                   ByteStr
            +Bytes Int2Bytes(1, String2Base(substrString(Hex, 0, 2), 16), BE))
    requires Hex =/=String ""
```

It is sometimes useful to go from the byte representation back to the token.

```k
  syntax TAddressLiteral ::= Bytes2TAddressLiteral(Bytes) [function]
  // ---------------------------------------------------------------
  rule Bytes2TAddressLiteral(B) => String2TealAddress(EncodeAddressBytes(B))

  syntax HexToken ::= Bytes2HexToken(Bytes) [function]
  // -------------------------------------------------
  rule Bytes2HexToken(B) => String2Hex("0x" +String Base2String(Bytes2Int(B, BE, Unsigned), 16))
```

We use several hooks which convert between token and string representations.

```k
  syntax String          ::= TealAddress2String(TAddressLiteral) [function, functional, hook(STRING.token2string)]
  syntax String          ::= Hex2String(HexToken)                [function, functional, hook(STRING.token2string)]
  syntax TAddressLiteral ::= String2TealAddress(String)          [function, hook(STRING.string2token)]
  syntax HexToken        ::= String2Hex(String)                  [function, hook(STRING.string2token)]
```

We also need hooks which convert between the string and byte representations of TEAL addresses.

```k
  syntax Bytes  ::= DecodeAddressString(String) [function]
  syntax String ::= EncodeAddressBytes(Bytes)   [function]
  // -----------------------------------------------------
  rule DecodeAddressString(S) => DecodeAddressStringInternal(S) requires IsAddressValid(S)
  rule EncodeAddressBytes(B)  => EncodeAddressBytesInternal(B)  requires lengthBytes(B)  ==Int 32

  syntax Bytes  ::= DecodeAddressStringInternal(String) [function, hook(KAVM.address_decode)]
  syntax String ::= EncodeAddressBytesInternal(Bytes)   [function, hook(KAVM.address_encode)]
```

We also have a hook just for checking whether an address is valid.

```k
  syntax Bool ::= IsAddressValid(String) [function, hook(KAVM.check_address)]
```

Finally, application addresses are constructed by hashing the application ID in a specail way.
See also [this section](https://developer.algorand.org/docs/get-details/dapps/smart-contracts/apps/#issuing-transactions-from-an-application) of the Algorand documentation.

```k
  syntax Bytes ::= getAppAddressBytes(Int) [function, functional]
  //-------------------------------------------------------------
  rule getAppAddressBytes(APP_ID) => String2Bytes(Sha512_256raw(Bytes2String(b"appID" +Bytes Int2Bytes(8, APP_ID, BE))))

  syntax TAddressLiteral ::= getAppAddress(Int) [function, functional]
  //------------------------------------------------------------------
  rule getAppAddress(APP_ID) => String2TealAddress(EncodeAddressBytes(getAppAddressBytes(APP_ID)))
```

### TEAL Value Processing

We expose several functions for working with lists.

```k
  syntax TValue ::= getTValueAt(Int, TValueNeList) [function]
  //---------------------------------------------------------
  rule getTValueAt(I, _ VL) => getTValueAt(I -Int 1, VL)
    requires I >Int 0
  rule getTValueAt(0, V _) => V
  rule getTValueAt(0, V  ) => V

  syntax Int ::= size(TValueList) [function, smtlib(tvlistsize)]
  // ---------------------------------------
  rule size(_ VL:TValueNeList) => 1 +Int size(VL)
  rule size(_:TValue       ) => 1
  rule size(.TValueList    ) => 0

  syntax Bool ::= contains(TValueList, TValue) [function, functional]
  // ----------------------------------------------------------------
  rule contains(V1:TValue  _:TValueNeList, V1:TValue) => true
  rule contains(V1:TValue VL:TValueNeList, V2:TValue) => contains(VL, V2) requires V1 =/=K V2
  rule contains(V1:TValue                , V2:TValue) => V1 ==K V2
  rule contains(              .TValueList,  _:TValue) => false 

  syntax TValueNeList ::= reverse(TValueNeList) [function]
  // -----------------------------------------------------
  rule reverse(V:TValue VL) => append(V, reverse(VL))
  rule reverse(V:TValue   ) => V

  syntax TValueNeList ::= append(TValue, TValueList) [function]
  // ----------------------------------------------------------
  rule append(V, V':TValue VL) => V' append(V, VL)
  rule append(V, V':TValue   ) => V' V
  rule append(V, .TValueList ) => V

  syntax TValuePairList ::= reverse(TValuePairList) [function]
  // ---------------------------------------------------------
  rule reverse(V:TValuePair VL) => append(V, reverse(VL))
  rule reverse(V:TValuePair   ) => V

  syntax TValuePairNeList ::= append(TValuePair, TValuePairList) [function]
  // ----------------------------------------------------------------------
  rule append(V, V':TValuePair VL) => V' append(V, VL)
  rule append(V, V':TValuePair   ) => V' V

  syntax TValueList ::= convertToBytes(TValueList) [function, functional]
  //---------------------------------------------------------------------
  rule convertToBytes(.TValueList) => .TValueList
  rule convertToBytes(B:TBytes) => B
  rule convertToBytes(I:TUInt64) => Int2Bytes({I}:>Int, BE, Unsigned)
  rule convertToBytes(B:TBytes L:TValueNeList) => (B {convertToBytes(L)}:>TValueNeList)
  rule convertToBytes(I:TUInt64 L:TValueNeList) => (Int2Bytes({I}:>Int, BE, Unsigned) {convertToBytes(L)}:>TValueNeList)

  syntax Int ::= sizeInBytes(TValue) [function, functional]
  //--------------------------------
  rule sizeInBytes(_:TUInt64) => 64
  rule sizeInBytes(B:TBytes) => lengthBytes({B}:>Bytes)
```

TValue normaliziation converts higher-level type representations in TEAL into
our internal K representation:

```k
  syntax TValue ::= normalize(TValue) [function]
  // -------------------------------------------
  rule normalize(V:TUInt64) => V
  rule normalize(V:TBytes) => normalizeB(V)
```

### Boolean conversions

```k
  syntax Bool ::= int2Bool(Int) [function, functional]
  rule int2Bool(0) => false
  rule int2Bool(A) => true requires A =/=Int 0

  syntax Int ::= bool2Int(Bool)  [function, functional, smtlib(bool2Int)]
  rule bool2Int(true ) => 1
  rule bool2Int(false) => 0
```


```k
endmodule
```
