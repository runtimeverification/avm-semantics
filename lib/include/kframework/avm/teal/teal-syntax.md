TEAL Grammar
============

Derived from the [TEAL specification](https://developer.algorand.org/docs/reference/teal/specification/).

```k
requires "avm/teal/teal-constants.md"
requires "avm/teal/teal-fields.md"
```

TEAL Opcode Grammar
-------------------

```k
module TEAL-OPCODES
  import TEAL-CONSTANTS
  import TEAL-FIELDS

  syntax PseudoOpCode                              // Pseudo opcodes abstracting other TEAL opcodes
  syntax OpCode       ::= "NoOpCode"               // Opcodes shared by stateless and stateful TEAL
                        | ErrOpCode
                        | CryptoOpCode
                        | ArithOpCode
                        | BitOpCode
                        | RelationalOpCode
                        | LogicalOpCode
                        | ByteOpCode
                        | BlockchainOpCode
                        | ScratchOpCode
                        | BranchingOpCode
                        | StackOpCode
                        | BoxStorageOpCode
  syntax SigOpCode    ::= SigVerOpCode | ArgOpCode           // Opcodes used only by stateless TEAL
  syntax AppOpCode    ::= StateOpCode
                        | TxnGroupStateOpCode
                        | InnerTxOpCode                      // Opcodes used only by stateful TEAL
```

### Generic TEAL Opcodes

#### Error Handling Operations

```k
  syntax ErrOpCode ::= "err"
```

#### Cryptographic Hash Operations

```k
  syntax CryptoOpCode ::= "sha256"
                        | "keccak256"
                        | "sha512_256"
```

#### Arithmetic Operations

```k
  syntax ArithOpCode ::= UnaryArithOpCode
                       | BinaryArithOpCode

  syntax UnaryArithOpCode ::= "sqrt"

  syntax BinaryArithOpCode ::= "+"
                             | "-"
                             | "/"
                             | "*"
                             | "%"
                             | "exp"
                             | "addw"
                             | "divmodw"
                             | "divw"
                             | "mulw"
                             | "expw"
```

#### Bitwise Operations

```k
  syntax BitOpCode ::= NullaryBitOpCode
                     | BinaryBitOpCode
                     | UnaryBitOpCode

  syntax BinaryBitOpCode  ::= "|"
                            | "&"
                            | "^"
                            | "shl"
                            | "shr"
  syntax UnaryBitOpCode   ::= "~"
                            | "bitlen"
  syntax NullaryBitOpCode ::= "getbit"
                            | "setbit"
```

#### Relational Operations

```k
  syntax RelationalOpCode ::= InequalityOpCode
                            | EqualityOpCode

  syntax InequalityOpCode ::= "<"
                            | ">"
                            | "<="
                            | ">="
  syntax EqualityOpCode   ::= "=="
                            | "!="
```

#### Logical Operations

```k
  syntax LogicalOpCode ::= BinaryLogicalOpCode
                         | UnaryLogicalOpCode

  syntax BinaryLogicalOpCode ::= "&&"
                               | "||"

  syntax UnaryLogicalOpCode  ::= "!"
```

#### Byte Array Operations

```k
  syntax ByteOpCode ::= UnaryByteOpCode
                      | BinaryByteOpCode
                      | TernaryByteOpCode
                      | MathByteOpCode

  syntax UnaryByteOpCode   ::= "len"
                             | "itob"
                             | "btoi"
                             | "substring" Int Int // start position, end position
                             | "getbyte"
                             | "setbyte"
                             | "bzero"
                             | "extract" TUInt8 TUInt8 // start position, length

  syntax BinaryByteOpCode  ::= "concat"
                             | "extract_uint16"
                             | "extract_uint32"
                             | "extract_uint64"

  syntax TernaryByteOpCode ::= "substring3"
                             | "extract3"

  syntax MathByteOpCode ::= ArithmMathByteOpCode
                          | RelationalMathByteOpCode
                          | LogicalMathByteOpCode

  syntax ArithmMathByteOpCode ::= "b+"
                                | "b-"
                                | "b/"
                                | "b%"
                                | "b*"

  syntax RelationalMathByteOpCode ::= InequalityMathByteOpCode
                                    | EqualityMathByteOpCode

  syntax InequalityMathByteOpCode ::= "b<"
                                    | "b>"
                                    | "b<="
                                    | "b>="

  syntax EqualityMathByteOpCode ::= "b=="
                                  | "b!="

  syntax LogicalMathByteOpCode ::= BinaryLogicalMathByteOpCode
                                 | UnaryLogicalMathByteOpCode

  syntax BinaryLogicalMathByteOpCode ::= "b|"
                                       | "b&"
                                       | "b^"

  syntax UnaryLogicalMathByteOpCode ::= "b~"
```

#### Constant Loading Operations

```k
  syntax OpCode ::= "intcblock" TUInt64 TValueNeList
                  | "intc" Int // Int Constant Index
                  | "intc_0"
                  | "intc_1"
                  | "intc_2"
                  | "intc_3"
                  | "bytecblock" TUInt64 TValuePairNeList
                  | "bytec" Int // Byte Constant Index
                  | "bytec_0"
                  | "bytec_1"
                  | "bytec_2"
                  | "bytec_3"
```

##### Constant Loading Pseudo-Ops

```k
  syntax PseudoOpCode ::= "int" PseudoTUInt64
                        | "byte" TBytesLiteral
                        | "addr" TAddressLiteral
                        | "method" TBytesLiteral
```

#### Blockchain State Accessors

```k
  syntax BlockchainOpCode ::= "txn" TxnField            // transaction field index
                            | "txn" TxnaField Int       // transaction field index, list index
                                                        // => Note: An extended version of txn not given in the reference docs but used in examples
                            | "gtxn" Int TxnField       // transaction group index, transaction field index
                            | "gtxns" TxnField          // transaction field index
                            | "txna" TxnaField Int      // transaction field index, transaction field array index
                            | "txnas" TxnaField         // transaction field index
                            | "gtxna" Int TxnaField Int // transaction group index, transaction field index, transaction field array index
                            | "gtxnas" Int TxnaField    // transaction group index, transaction field index
                            | "gtxnsa" TxnaField Int    // transaction field index, transaction field array index
                            | "gtxnsas" TxnaField       // transaction field index
                            | "global" GlobalField      // global field index
```

#### Scratch Space Operations

```k
  syntax ScratchOpCode ::= LoadOpCode
                         | StoreOpCode
  syntax LoadOpCode    ::= "load"  Int // position in scratch space to load from
                         | "loads"     // Same as previous, but the position is on stack
  syntax StoreOpCode   ::= "store" Int // position in scratch space to store to
                         | "stores"    // Same as previous, but the position is on stack
```

#### Flow Control Operations

```k
  syntax Label [token]

  syntax BranchingOpCode ::= CondBranchOpCode
                           | JumpOpCode
                           | ReturnOpCode
                           | AssertOpCode
                           | SubroutineOpCode

  syntax CondBranchOpCode ::= "bnz" Label          // forward branch offset, big endian
                            | "bz"  Label          // forward branch offset, big endian
  syntax JumpOpCode       ::= "b"   Label          // forward branch offset, big endian
  syntax ReturnOpCode     ::= "return"
  syntax AssertOpCode     ::= "assert"
  syntax SubroutineOpCode ::= "callsub" Label
                            | "retsub"
                            | "proto" Int Int
                            | "dupn" Int
                            | "frame_dig" Int
                            | "frame_bury" Int
```

#### Stack Manipulation Operations
```k
  syntax StackOpCode      ::= NullaryStackOpCode
                            | UnaryStackOpCode
                            | BinaryStackOpCode
                            | TernaryStackOpCode
                            | NAryStackOpCode

  syntax NullaryStackOpCode ::= "pushint" PseudoTUInt64
                              | "pushbytes" TBytesLiteral

  syntax UnaryStackOpCode  ::= "pop"
                             | "dup"

  syntax BinaryStackOpCode ::= "dup2"
                             | "swap"

  syntax TernaryStackOpCode ::= "select"

  syntax NAryStackOpCode    ::= "dig" Int
                              | "cover" Int
                              | "uncover" Int
```

### Stateless TEAL Operations

#### Signature Verification Operations

```k
  syntax SigVerOpCode ::= "ed25519verify"
```

#### Logic Signature Argument Accessors

```k
  syntax ArgOpCode ::= "arg" Int // Int arg index
                     | "args"    // arg index on stack
                     | "arg_0"
                     | "arg_1"
                     | "arg_2"
                     | "arg_3"
```

### Stateful TEAL Operations

#### Application State Accessors

```k
  syntax StateOpCode ::= UnaryStateOpCode
                       | BinaryStateOpCode
                       | TernaryStateOpCode

  syntax UnaryStateOpCode   ::= "balance"
                              | "app_global_del"
                              | "app_global_get"
                              | "asset_params_get" AssetParamsField
                              | "acct_params_get" AccountParamsField
                              | "app_params_get" AppParamsField
                              | "min_balance"
                              | "log"
  syntax BinaryStateOpCode  ::= "app_opted_in"
                              | "app_local_get"
                              | "app_global_get_ex"
                              | "app_global_put"
                              | "app_local_del"
                              | "asset_holding_get" AssetHoldingField
  syntax TernaryStateOpCode ::= "app_local_get_ex"
                              | "app_local_put"
```

#### Box storage

```k
  syntax BoxStorageOpCode ::= "box_create"
                            | "box_extract"
                            | "box_replace"
                            | "box_del"
                            | "box_len"
                            | "box_get"
                            | "box_put"
```

#### Access to past transactions in the group

```k
  syntax TxnGroupStateOpCode ::= NullaryTxnGroupStateOpCode
                               | UnaryTxnGroupStateOpCode
                               | BinaryTxnGroupStateOpCode

  syntax NullaryTxnGroupStateOpCode ::= "gaid" Int // transaction index
                                      | "gload" Int Int // transaction index, scratch position

  syntax UnaryTxnGroupStateOpCode ::= "gaids"
                                    | "gloads" Int // scratch position

  syntax BinaryTxnGroupStateOpCode ::= "gloadss"

```

#### Inner transaction control

```k
  syntax InnerTxOpCode ::= "itxn_begin"
                         | "itxn_submit"
                         | "itxn_field" TxnFieldTop
                         | "itxn_next"
                         | "itxn" TxnField
                         | "itxna" TxnaField Int
                         | "itxnas" TxnaField
                         | "gitxnas" Int TxnaField
                         | "gitxn" Int TxnField
                         | "gitxna" Int TxnaField Int
```

```k
endmodule
```

TEAL Program Definition
-----------------------

```k
module TEAL-SYNTAX
  import TEAL-OPCODES
  import INT
  import STRING
  import BOOL

  syntax LabelCode ::= Label ":"

  syntax TealOpCode ::= PseudoOpCode | OpCode | SigOpCode | AppOpCode
  syntax TealOpCodeOrLabel ::= TealOpCode | LabelCode

  syntax TealPragmas ::= TealPragma TealPragmas | TealPragma
  syntax TealPragma ::= "#pragma" PragmaDirective
  syntax PragmaDirective ::= VersionPragma

  syntax TealMode ::= "stateless" | "stateful" | "undefined"

  syntax VersionPragma ::= "version" Int

  syntax TealPgm ::= TealOpCodeOrLabel
                   | TealOpCodeOrLabel TealPgm
  syntax TealInputPgm ::= TealPragmas TealPgm | TealPgm

endmodule
```

### TEAL Program Parser

This module defines the grammar used to parse TEAL programs.
Note that this module is _not_ imported by any module defining semantic rules.

It includes regular expressions that define all _token_ sorts.
A token sort is special sort that has no constructors in K; instead, token
sorts have a single built-in constructor which is essentially a wrapped
string literal.

Token sorts are needed to keep our syntactic definitions unambiguous.
Otherwise, highly generic syntactic categories in TEAL, such as TEAL labels,
would confuse the K tokenizer when parsing our core semantic rules.

```k
module TEAL-PARSER-SYNTAX
  imports TEAL-SYNTAX
```

We define the syntax of TEAL's comments (using K's built-in sort `#Layout`), along with TEAL's labels and hexadecimal byte literals.

```k
  syntax #Layout  ::= r"\\/\\/[^\\n\\r]*" // comments
                    | r"([\\ \\n\\r\\t])" // whitespace

  syntax lexical Digit     = r"[0-9]"
  syntax lexical HexDigit  = r"[0-9a-fA-F]"
  syntax lexical Alpha     = r"[a-zA-Z]"
  syntax lexical Alnum     = r"{Alpha}|{Digit}"
  syntax lexical AlnumUbar = r"{Alnum}|_"
  syntax lexical Special   = r"[-!?+<>=/*]"

  syntax Label           ::= r"({AlnumUbar}|{Special})+" [token]
  syntax HexToken        ::= r"0x{HexDigit}+"            [prec(2),token]
  syntax TAddressLiteral ::= r"[0-9A-Z]{58}"             [prec(1),token]
```

NOTE: the following definitions are _disabled_.

```disabled
  syntax B64Encoded ::= r"[a-zA-Z0-9\\+\\/=]+" [token]
  syntax B32Encoded ::= r"[A-Z2-7=]+"          [token]
```

```k
endmodule
```

### TEAL Unparser

This module takes a `TealPgm` value and prints out a string that corresponds to
it.

The opcodes that have no immediate arguments do not require specific rules, since
they are handled by the `[owise]` rule of the `unparseTEALOp` function. The opcodes
which are not just tokens, i.e. have at least one immediate argument, need
an `unparseTEALOp` rule.


```k
module TEAL-UNPARSER
  imports TEAL-SYNTAX
  imports TEAL-TYPES
  imports STRING

  syntax String ::= unparseTEAL(TealPgm) [function]
  // ----------------------------------------------
  rule unparseTEAL(O:TealOpCodeOrLabel TP:TealPgm)
    => unparseTEAL(O) +String "\n" +String unparseTEAL(TP)

  rule unparseTEAL(err)                           => "err"
  rule unparseTEAL(sha256)                        => "sha256"
  rule unparseTEAL(keccak256)                     => "keccak256"
  rule unparseTEAL(sha512_256)                    => "sha512_256"
  rule unparseTEAL(+)                             => "+"
  rule unparseTEAL(-)                             => "-"
  rule unparseTEAL(/)                             => "/"
  rule unparseTEAL(*)                             => "*"
  rule unparseTEAL(%)                             => "%"
  rule unparseTEAL(exp)                           => "exp"
  rule unparseTEAL(addw)                          => "addw"
  rule unparseTEAL(divmodw)                       => "divmodw"
  rule unparseTEAL(divw)                          => "divw"
  rule unparseTEAL(mulw)                          => "mulw"
  rule unparseTEAL(expw)                          => "expw"
  rule unparseTEAL(|)                             => "|"
  rule unparseTEAL(&)                             => "&"
  rule unparseTEAL(^)                             => "^"
  rule unparseTEAL(~)                             => "~"
  rule unparseTEAL(getbit)                        => "getbit"
  rule unparseTEAL(setbit)                        => "setbit"
  rule unparseTEAL(<)                             => "<"
  rule unparseTEAL(>)                             => ">"
  rule unparseTEAL(<=)                            => "<="
  rule unparseTEAL(>=)                            => ">="
  rule unparseTEAL(==)                            => "=="
  rule unparseTEAL(!=)                            => "!="
  rule unparseTEAL(&&)                            => "&&"
  rule unparseTEAL(||)                            => "||"
  rule unparseTEAL(!)                             => "!"
  rule unparseTEAL(len)                           => "len"
  rule unparseTEAL(itob)                          => "itob"
  rule unparseTEAL(btoi)                          => "btoi"
  rule unparseTEAL(substring Start End)           => "substring" +&+ Int2String(Start:Int) +&+ Int2String(End:Int)
  rule unparseTEAL(getbyte)                       => "getbyte"
  rule unparseTEAL(setbyte)                       => "setbyte"
  rule unparseTEAL(concat)                        => "concat"
  rule unparseTEAL(extract Start Length)          => "extract" +&+ Int2String(Start:Int) +&+ Int2String(Length:Int)
  rule unparseTEAL(b+)                            => "b+"
  rule unparseTEAL(b-)                            => "b-"
  rule unparseTEAL(b/)                            => "b/"
  rule unparseTEAL(b*)                            => "b*"
  rule unparseTEAL(b<)                            => "b<"
  rule unparseTEAL(b>)                            => "b>"
  rule unparseTEAL(b<=)                           => "b<="
  rule unparseTEAL(b>=)                           => "b>="
  rule unparseTEAL(b==)                           => "b=="
  rule unparseTEAL(b!=)                           => "b!="
  rule unparseTEAL(b%)                            => "b%"
  rule unparseTEAL(b|)                            => "b|"
  rule unparseTEAL(b&)                            => "b&"
  rule unparseTEAL(b^)                            => "b^"
  rule unparseTEAL(b~)                            => "b~"
  rule unparseTEAL(substring3)                    => "substring3"
  rule unparseTEAL(extract3)                      => "extract3"
  rule unparseTEAL(extract_uint16)                => "extract_uint16"
  rule unparseTEAL(extract_uint32)                => "extract_uint32"
  rule unparseTEAL(extract_uint64)                => "extract_uint64"
  rule unparseTEAL(intcblock Size IntConsts)      => "intcblock" +&+ Int2String(Size:Int) +&+ TValueList2String(IntConsts:TValueNeList)
  rule unparseTEAL(intc Idx)                      => "intc" +&+ Int2String(Idx:Int)
  rule unparseTEAL(intc_0)                        => "intc_0"
  rule unparseTEAL(intc_1)                        => "intc_1"
  rule unparseTEAL(intc_2)                        => "intc_2"
  rule unparseTEAL(intc_3)                        => "intc_3"
  rule unparseTEAL(pushint I:Int)                 => "pushint" +&+ Int2String(I)
  rule unparseTEAL(bytecblock Size ByteConsts)    => "bytecblock" +&+ Int2String(Size:Int) +&+ TValuePairList2String(ByteConsts:TValuePairNeList)
  rule unparseTEAL(bytec Idx)                     => "bytec" +&+ Int2String(Idx:Int)
  rule unparseTEAL(bytec_0)                       => "bytec_0"
  rule unparseTEAL(bytec_1)                       => "bytec_1"
  rule unparseTEAL(bytec_2)                       => "bytec_2"
  rule unparseTEAL(bytec_3)                       => "bytec_3"
  rule unparseTEAL(pushbytes ByteConst)           => "pushbytes" +&+ TValue2String(ByteConst:TBytesLiteral)
  rule unparseTEAL(int I:Int)                     => "int" +&+ Int2String(I)
  rule unparseTEAL(int I:TUInt64Token)            => "int" +&+ IntToken2String(I)
  rule unparseTEAL(byte ByteConst)                => "byte" +&+ TValue2String(ByteConst:TBytesLiteral)
  rule unparseTEAL(addr AddrConst)                => "addr" +&+ TValue2String(AddrConst:TAddressLiteral)
  rule unparseTEAL(method S:String)               => "method" +&+ S
  rule unparseTEAL(txn FieldName)                 => "txn" +&+ TealField2String(FieldName:TxnField)
  rule unparseTEAL(txn FieldName ArrIdx)          => "txn" +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(gtxn TxnIdx TxnField)          => "gtxn" +&+ Int2String(TxnIdx:Int) +&+ TealField2String(TxnField:TxnField)
  rule unparseTEAL(gtxns TxnField)                => "gtxns" +&+ TealField2String(TxnField:TxnField)
  rule unparseTEAL(txna FieldName ArrIdx)         => "txna" +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(txnas FieldName)               => "txnas" +&+ TealField2String(FieldName:TxnaField)
  rule unparseTEAL(gtxna TxnIdx FieldName ArrIdx) => "gtxna" +&+ Int2String(TxnIdx:Int) +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(gtxnas TxnIdx FieldName)       => "gtxnas" +&+ Int2String(TxnIdx:Int) +&+ TealField2String(FieldName:TxnaField)
  rule unparseTEAL(gtxnsa FieldName ArrIdx)       => "gtxnsa" +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(gtxnsas FieldName)             => "gtxnsas" +&+ TealField2String(FieldName:TxnaField)
  rule unparseTEAL(global FieldName)              => "global" +&+ TealField2String(FieldName:GlobalField)
  rule unparseTEAL(load SlotIdx)                  => "load" +&+ Int2String(SlotIdx:Int)
  rule unparseTEAL(loads)                         => "loads"
  rule unparseTEAL(store SlotIdx)                 => "store" +&+ Int2String(SlotIdx:Int)
  rule unparseTEAL(stores)                        => "stores"
  rule unparseTEAL(bnz Lbl)                       => "bnz" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(bz Lbl)                        => "bz" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(b Lbl)                         => "b" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(Lbl :)                         => Label2String(Lbl) +String ":"
  rule unparseTEAL(return)                        => "return"
  rule unparseTEAL(assert)                        => "assert"
  rule unparseTEAL(callsub)                       => "callsub"
  rule unparseTEAL(retsub)                        => "retsub"
  rule unparseTEAL(proto N M)                     => "proto" +&+ Int2String(N) +&+ Int2String(M)
  rule unparseTEAL(dupn N)                        => "dupn" +&+ Int2String(N)
  rule unparseTEAL(frame_dig N)                   => "frame_dig" +&+ Int2String(N)
  rule unparseTEAL(frame_bury N)                  => "frame_bury" +&+ Int2String(N)
  rule unparseTEAL(pop)                           => "pop"
  rule unparseTEAL(dup)                           => "dup"
  rule unparseTEAL(dup2)                          => "dup2"
  rule unparseTEAL(dig N)                         => "dig" +&+ Int2String(N)
  rule unparseTEAL(cover N)                       => "cover" +&+ Int2String(N)
  rule unparseTEAL(uncover N)                     => "uncover" +&+ Int2String(N)
  rule unparseTEAL(select)                        => "select"
  rule unparseTEAL(swap)                          => "swap"
  rule unparseTEAL(ed25519verify)                 => "ed25519verify"
  rule unparseTEAL(arg ArgIdx:Int)                => "arg" +&+ Int2String(ArgIdx)
  rule unparseTEAL(args)                          => "args"
  rule unparseTEAL(arg_0)                         => "arg_0"
  rule unparseTEAL(arg_1)                         => "arg_1"
  rule unparseTEAL(arg_2)                         => "arg_2"
  rule unparseTEAL(arg_3)                         => "arg_3"
  rule unparseTEAL(balance)                       => "balance"
  rule unparseTEAL(app_global_del)                => "app_global_del"
  rule unparseTEAL(app_global_get)                => "app_global_get"
  rule unparseTEAL(asset_params_get FieldName)    => "asset_params_get" +&+ TealField2String(FieldName:AssetParamsField)
  rule unparseTEAL(acct_params_get FieldName)     => "acct_params_get" +&+ TealField2String(FieldName:AccountParamsField)
  rule unparseTEAL(app_params_get FieldName)      => "app_params_get" +&+ TealField2String(FieldName:AppParamsField)
  rule unparseTEAL(min_balance)                   => "min_balance"
  rule unparseTEAL(log)                           => "log"
  rule unparseTEAL(app_opted_in)                  => "app_opted_in"
  rule unparseTEAL(app_local_get)                 => "app_local_get"
  rule unparseTEAL(app_global_get_ex)             => "app_global_get_ex"
  rule unparseTEAL(app_global_put)                => "app_global_put"
  rule unparseTEAL(app_local_del)                 => "app_local_del"
  rule unparseTEAL(asset_holding_get FieldName)   => "asset_holding_get" +&+ TealField2String(FieldName:AssetHoldingField)
  rule unparseTEAL(app_local_get_ex)              => "app_local_get_ex"
  rule unparseTEAL(app_local_put)                 => "app_local_put"
  rule unparseTEAL(box_create)                    => "box_create"
  rule unparseTEAL(box_extract)                   => "box_extract"
  rule unparseTEAL(box_replace)                   => "box_replace"
  rule unparseTEAL(box_del)                       => "box_del"
  rule unparseTEAL(box_len)                       => "box_len"
  rule unparseTEAL(box_get)                       => "box_get"
  rule unparseTEAL(box_put)                       => "box_put"
  rule unparseTEAL(gaid N)                        => "gaid" +&+ Int2String(N)
  rule unparseTEAL(gload N M)                     => "gload" +&+ Int2String(N) +&+ Int2String(M)
  rule unparseTEAL(gaids)                         => "gaids"
  rule unparseTEAL(gloads N)                      => "gloads" +&+ Int2String(N)
  rule unparseTEAL(gloadss)                       => "gloadss"
  rule unparseTEAL(itxn_begin)                    => "itxn_begin"
  rule unparseTEAL(itxn_submit)                   => "itxn_submit"
  rule unparseTEAL(itxn_field FieldName)          => "itxn_field" +&+ TealField2String(FieldName:TxnField)
  rule unparseTEAL(itxn_next)                     => "itxn_next"
  rule unparseTEAL(itxn FieldName)                => "itxn" +&+ TealField2String(FieldName:TxnField)
  rule unparseTEAL(itxna FieldName N)             => "itxna" +&+ TealField2String(FieldName:TxnField) +&+ Int2String(N)
  rule unparseTEAL(gitxn T FieldName)             => "itxn" +&+ Int2String(T) +&+ TealField2String(FieldName:TxnField)
  rule unparseTEAL(gitxna T FieldName N)          => "itxna" +&+ Int2String(T) +&+ TealField2String(FieldName:TxnField) +&+ Int2String(N)
  rule unparseTEAL(itxnas FieldName)              => "itxnas" +&+ TealField2String(FieldName:TxnaField)
  rule unparseTEAL(gitxnas T FieldName)           => "gitxnas" +&+ Int2String(T) +&+ TealField2String(FieldName:TxnaField)

  syntax String ::= left:
                    String "+&+" String       [function]
  // ---------------------------------------------------
  rule S:String +&+ S2:String  => S +String " " +String S2

  syntax String ::= Label2String(Label) [function, functional, hook(STRING.token2string)]

  syntax String ::= TealField2String(GlobalField)        [function]
                  | TealField2String(AssetHoldingField)  [function]
                  | TealField2String(AssetParamsField)   [function]
                  | TealField2String(AppParamsField)     [function]
                  | TealField2String(TxnField)           [function]
                  | TealField2String(TxnaField)          [function]
                  | TealField2String(AccountParamsField) [function]
  // ---------------------------------------------------------------------------------------
  rule TealField2String(MinTxnFee)                => "MinTxnFee"
  rule TealField2String(MinBalance)               => "MinBalance"
  rule TealField2String(MaxTxnLife)               => "MaxTxnLife"
  rule TealField2String(ZeroAddress)              => "ZeroAddress"
  rule TealField2String(GroupSize)                => "GroupSize"
  rule TealField2String(LogicSigVersion)          => "LogicSigVersion"
  rule TealField2String(Round)                    => "Round"
  rule TealField2String(LatestTimestamp)          => "LatestTimestamp"
  rule TealField2String(CurrentApplicationID)     => "CurrentApplicationID"
  rule TealField2String(CreatorAddress)           => "CreatorAddress"
  rule TealField2String(AssetBalance)             => "AssetBalance"
  rule TealField2String(AssetFrozen)              => "AssetFrozen"
  rule TealField2String(AssetTotal)               => "AssetTotal"
  rule TealField2String(AssetDecimals)            => "AssetDecimals"
  rule TealField2String(AssetDefaultFrozen)       => "AssetDefaultFrozen"
  rule TealField2String(AssetUnitName)            => "AssetUnitName"
  rule TealField2String(AssetName)                => "AssetName"
  rule TealField2String(AssetURL)                 => "AssetURL"
  rule TealField2String(AssetMetadataHash)        => "AssetMetadataHash"
  rule TealField2String(AssetManager)             => "AssetManager"
  rule TealField2String(AssetReserve)             => "AssetReserve"
  rule TealField2String(AssetFreeze)              => "AssetFreeze"
  rule TealField2String(AssetClawback)            => "AssetClawback"

  rule TealField2String(AppApprovalProgram)       => "AppApprovalProgram"
  rule TealField2String(AppClearStateProgram)     => "AppClearStateProgram"
  rule TealField2String(AppGlobalNumUint)         => "AppGlobalNumUint"
  rule TealField2String(AppGlobalNumByteSlice)    => "AppGlobalNumByteSlice"
  rule TealField2String(AppLocalNumUint)          => "AppLocalNumUint"
  rule TealField2String(AppLocalNumByteSlice)     => "AppLocalNumByteSlice"
  rule TealField2String(AppExtraProgramPages)     => "AppExtraProgramPages"
  rule TealField2String(AppCreator)               => "AppCreator"
  rule TealField2String(AppAddress)               => "AppAddress"

  rule TealField2String(TxID)                     => "TxID"
  rule TealField2String(Sender)                   => "Sender"
  rule TealField2String(Fee)                      => "Fee"
  rule TealField2String(FirstValid)               => "FirstValid"
  rule TealField2String(FirstValidTime)           => "FirstValidTime"
  rule TealField2String(LastValid)                => "LastValid"
  rule TealField2String(Note)                     => "Note"
  rule TealField2String(Lease)                    => "Lease"
  rule TealField2String(RekeyTo)                  => "RekeyTo"
  rule TealField2String(TxType)                   => "TxType"
  rule TealField2String(TypeEnum)                 => "TypeEnum"
  rule TealField2String(GroupIndex)               => "GroupIndex"
  rule TealField2String(LastLog)                  => "LastLog"
  rule TealField2String(NumLogs)                  => "NumLogs"
  rule TealField2String(Logs)                     => "Logs"
  rule TealField2String(Receiver)                 => "Receiver"
  rule TealField2String(Amount)                   => "Amount"
  rule TealField2String(CloseRemainderTo)         => "CloseRemainderTo"
  rule TealField2String(VotePK)                   => "VotePK"
  rule TealField2String(SelectionPK)              => "SelectionPK"
  rule TealField2String(VoteFirst)                => "VoteFirst"
  rule TealField2String(VoteLast)                 => "VoteLast"
  rule TealField2String(VoteKeyDilution)          => "VoteKeyDilution"
  rule TealField2String(ConfigAsset)              => "ConfigAsset"
  rule TealField2String(ConfigAssetTotal)         => "ConfigAssetTotal"
  rule TealField2String(ConfigAssetDecimals)      => "ConfigAssetDecimals"
  rule TealField2String(ConfigAssetDefaultFrozen) => "ConfigAssetDefaultFrozen"
  rule TealField2String(ConfigAssetUnitName)      => "ConfigAssetUnitName"
  rule TealField2String(ConfigAssetName)          => "ConfigAssetName"
  rule TealField2String(ConfigAssetURL)           => "ConfigAssetURL"
  rule TealField2String(ConfigAssetMetaDataHash)  => "ConfigAssetMetaDataHash"
  rule TealField2String(ConfigAssetManager)       => "ConfigAssetManager"
  rule TealField2String(ConfigAssetReserve)       => "ConfigAssetReserve"
  rule TealField2String(ConfigAssetFreeze)        => "ConfigAssetFreeze"
  rule TealField2String(ConfigAssetClawback)      => "ConfigAssetClawback"
  rule TealField2String(XferAsset)                => "XferAsset"
  rule TealField2String(AssetAmount)              => "AssetAmount"
  rule TealField2String(AssetASender)             => "AssetASender"
  rule TealField2String(AssetReceiver)            => "AssetReceiver"
  rule TealField2String(AssetCloseTo)             => "AssetCloseTo"
  rule TealField2String(FreezeAsset)              => "FreezeAsset"
  rule TealField2String(FreezeAssetAccount)       => "FreezeAssetAccount"
  rule TealField2String(FreezeAssetFrozen)        => "FreezeAssetFrozen"
  rule TealField2String(ApplicationID)            => "ApplicationID"
  rule TealField2String(OnCompletion)             => "OnCompletion"
  rule TealField2String(NumAppArgs)               => "NumAppArgs"
  rule TealField2String(NumAccounts)              => "NumAccounts"
  rule TealField2String(ApprovalProgram)          => "ApprovalProgram"
  rule TealField2String(ClearStateProgram)        => "ClearStateProgram"
  rule TealField2String(ApplicationArgs)          => "ApplicationArgs"
  rule TealField2String(Accounts)                 => "Accounts"
  rule TealField2String(Applications)             => "Applications"
  rule TealField2String(Assets)                   => "Assets"
  rule TealField2String(AcctBalance)              => "AcctBalance"
  rule TealField2String(AcctMinBalance)           => "AcctMinBalance"
  rule TealField2String(AcctAuthAddr)             => "AcctAuthAddr"


  syntax String ::= TValue2String(TValue)         [function]
                  | TValuePair2String(TValuePair) [function]
  // -------------------------------------------------------
  rule TValue2String(I:Int)              => Int2String(I)
  rule TValue2String(S:String)           => "\"" +String S +String "\""
  rule TValue2String(H:HexToken)         => Hex2String(H)
  rule TValue2String(B:Bytes)            => "0x" +String Base2String(Bytes2Int(B,BE,Unsigned), 16)
  rule TValue2String(TA:TAddressLiteral) => TealAddress2String(TA)
  rule TValuePair2String((TV, TV2))      => "( " +String TValue2String(TV) +String ", " +String  TValue2String(TV2) +String " )"

  syntax String ::= TValueList2String(TValueNeList)         [function]
                  | TValuePairList2String(TValuePairList)   [function]
  // ---------------------------------------------------------------
  rule TValueList2String(TV:TValue TVL:TValueNeList)           => TValue2String(TV) +&+ TValueList2String(TVL)
  rule TValueList2String(TV:TValue)                            => TValue2String(TV)
  rule TValuePairList2String(TV:TValuePair TVL:TValuePairNeList) => TValuePair2String(TV) +&+ TValuePairList2String(TVL)
  rule TValuePairList2String(TV:TValuePair)                    => TValuePair2String(TV)

  syntax String ::= IntToken2String(TUInt64Token) [function, hook(STRING.token2string)]
  // ----------------------------------------------------------------------------------
  rule IntToken2String(unknown)           => "unknown"
  rule IntToken2String(pay)               => "pay"
  rule IntToken2String(keyreg)            => "keyreg"
  rule IntToken2String(acfg)              => "acfg"
  rule IntToken2String(axfer)             => "axfer"
  rule IntToken2String(afrz)              => "afrz"
  rule IntToken2String(appl)              => "appl"
  rule IntToken2String(NoOp)              => "NoOp"
  rule IntToken2String(OptIn)             => "OptIn"
  rule IntToken2String(CloseOut)          => "CloseOut"
  rule IntToken2String(ClearState)        => "ClearState"
  rule IntToken2String(UpdateApplication) => "UpdateApplication"
  rule IntToken2String(DeleteApplication) => "DeleteApplication"

endmodule
```
