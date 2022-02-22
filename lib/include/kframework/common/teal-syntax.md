TEAL Grammar
============

Derived from the [TEAL specification](https://developer.algorand.org/docs/reference/teal/specification/).

```k
requires "teal-constants.md"
requires "teal-fields.md"
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
  syntax SigOpCode    ::= SigVerOpCode | ArgOpCode // Opcodes used only by stateless TEAL
  syntax AppOpCode    ::= StateOpCode              // Opcodes used only by stateful TEAL
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
  syntax ArithOpCode ::= "+"
                       | "-"
                       | "/"
                       | "*"
                       | "%"
                       | "addw"
                       | "mulw"
```

#### Bitwise Operations

```k
  syntax BitOpCode ::= NullaryBitOpCode
                     | BinaryBitOpCode
                     | UnaryBitOpCode

  syntax BinaryBitOpCode  ::= "|"
                            | "&"
                            | "^"
  syntax UnaryBitOpCode   ::= "~"
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

  syntax UnaryByteOpCode   ::= "len"
                             | "itob"
                             | "btoi"
                             | "substring" Int Int // start position, end position
                             | "getbyte"
                             | "setbyte"

  syntax BinaryByteOpCode  ::= "concat"

  syntax TernaryByteOpCode ::= "substring3"
```

#### Constant Loading Operations

```k
  syntax OpCode ::= "intcblock" TUInt64 TValueList
                  | "intc" Int // Int Constant Index
                  | "intc_0"
                  | "intc_1"
                  | "intc_2"
                  | "intc_3"
                  | "bytecblock" TUInt64 TValuePairList
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
```

#### Blockchain State Accessors

```k
  syntax BlockchainOpCode ::= "txn" TxnField            // transaction field index
                            | "txn" TxnaField Int       // transaction field index, list index
                                                        // => Note: An extended version of txn not given in the reference docs but used in examples
                            | "gtxn" Int TxnField       // transaction group index, transaction field index
                            | "gtxns" TxnField          // transaction field index
                            | "txna" TxnaField Int      // transaction field index, transaction field array index
                            | "gtxna" Int TxnaField Int // transaction group index, transaction field index, transaction field array index
                            | "gtxnsa" TxnaField Int    // transaction field index, transaction field array index
                            | "global" GlobalField      // global field index
```

#### Scratch Space Operations

```k
  syntax ScratchOpCode ::= LoadOpCode
                         | StoreOpCode
  syntax LoadOpCode    ::= "load"  Int // position in scratch space to load from
  syntax StoreOpCode   ::= "store" Int // position in scratch space to store to
```

#### Flow Control Operations

```k
  syntax Label [token]

  syntax BranchingOpCode ::= CondBranchOpCode
                           | JumpOpCode
                           | ReturnOpCode
                           | AssertOpCode

  syntax CondBranchOpCode ::= "bnz" Label          // forward branch offset, big endian
                            | "bz"  Label          // forward branch offset, big endian
  syntax JumpOpCode       ::= "b"   Label          // forward branch offset, big endian
  syntax ReturnOpCode     ::= "return"
  syntax AssertOpCode     ::= "assert"
```

#### Stack Manipulation Operations
```k
  syntax StackOpCode      ::= NullaryStackOpCode
                            | UnaryStackOpCode
                            | BinaryStackOpCode
                            | TernaryStackOpCode

  syntax NullaryStackOpCode ::= "pushint" PseudoTUInt64
                              | "pushbytes" TBytesLiteral

  syntax UnaryStackOpCode  ::= "pop"
                             | "dup"
                             // We type `dig N` as unary, but the semantics must check
                             // that the stack is deep enough
                             | "dig" Int
  syntax BinaryStackOpCode ::= "dup2"
                             | "swap"

  syntax TernaryStackOpCode ::= "select"
```

### Stateless TEAL Operations

#### Signature Verification Operations

```k
  syntax SigVerOpCode ::= "ed25519verify"
```

#### Logic Signature Argument Accessors

```k
  syntax ArgOpCode ::= "arg" Int // Int arg index
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
                              | "asset_params_get"  AssetParamsField
  syntax BinaryStateOpCode  ::= "app_opted_in"
                              | "app_local_get"
                              | "app_global_get_ex"
                              | "app_global_put"
                              | "app_local_del"
                              | "asset_holding_get" AssetHoldingField
  syntax TernaryStateOpCode ::= "app_local_get_ex"
                              | "app_local_put"
```

```k
endmodule
```

TEAL Program Definition
-----------------------

```k
module TEAL-SYNTAX
  import TEAL-OPCODES

  syntax LabelCode ::= Label ":"

  syntax TealOpCode ::= PseudoOpCode | OpCode | SigOpCode | AppOpCode
  syntax TealOpCodeOrLabel ::= TealOpCode | LabelCode

  syntax TealPragmas ::= TealPragma TealPragmas | TealPragma
  syntax TealPragma ::= "#pragma" PragmaDirective
  syntax PragmaDirective ::= ModePragma
                           | VersionPragma
                           | TxnPragma

  syntax TealMode ::= "stateless" | "stateful"
  syntax ModePragma ::= "mode" TealMode

  syntax VersionPragma ::= "version" Int

  syntax TxnPragma ::= "txn" Int

  syntax TealPgm ::= TealOpCodeOrLabel
                   | TealOpCodeOrLabel TealPgm
  syntax TealInputPgm ::= TealPragmas TealPgm
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

  syntax Label           ::= r"[_a-zA-Z][_0-9a-zA-Z]*" [token]
  syntax HexToken        ::= r"0x[0-9a-fA-F]+"         [token]
  syntax TAddressLiteral ::= r"[0-9A-Z]{58}"           [prec(1),token]
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

This module takes a TealPgm value and prints out a string that corresponds to
it.

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
  rule unparseTEAL(addw)                          => "addw"
  rule unparseTEAL(mulw)                          => "mulw"
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
  rule unparseTEAL(substring3)                    => "substring3"
  rule unparseTEAL(intcblock Size IntConsts)      => "intcblock" +&+ Int2String(Size:Int) +&+ TValueList2String(IntConsts:TValueList)
  rule unparseTEAL(intc Idx)                      => "intc" +&+ Int2String(Idx:Int)
  rule unparseTEAL(intc_0)                        => "intc_0"
  rule unparseTEAL(intc_1)                        => "intc_1"
  rule unparseTEAL(intc_2)                        => "intc_2"
  rule unparseTEAL(intc_3)                        => "intc_3"
  rule unparseTEAL(pushint I:Int)                 => "pushint" +&+ Int2String(I)
  rule unparseTEAL(bytecblock Size ByteConsts)    => "bytecblock" +&+ Int2String(Size:Int) +&+ TValuePairList2String(ByteConsts:TValuePairList)
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
  rule unparseTEAL(txn FieldName)                 => "txn" +&+ TealField2String(FieldName:TxnField)
  rule unparseTEAL(txn FieldName ArrIdx)          => "txn" +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(gtxn TxnIdx TxnField)          => "gtxn" +&+ Int2String(TxnIdx:Int) +&+ TealField2String(TxnField:TxnField)
  rule unparseTEAL(gtxns TxnField)                => "gtxns" +&+ TealField2String(TxnField:TxnField)
  rule unparseTEAL(txna FieldName ArrIdx)         => "txna" +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(gtxna TxnIdx FieldName ArrIdx) => "gtxna" +&+ Int2String(TxnIdx:Int) +&+ TealField2String(FieldName:TxnaField) +&+ Int2String(ArrIdx:Int)
  rule unparseTEAL(global FieldName)              => "global" +&+ TealField2String(FieldName:GlobalField)
  rule unparseTEAL(load SlotIdx)                  => "load" +&+ Int2String(SlotIdx:Int)
  rule unparseTEAL(store SlotIdx)                 => "store" +&+ Int2String(SlotIdx:Int)
  rule unparseTEAL(bnz Lbl)                       => "bnz" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(bz Lbl)                        => "bz" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(b Lbl)                         => "b" +&+ Label2String(Lbl:Label)
  rule unparseTEAL(Lbl :)                         => Label2String(Lbl) +String ":"
  rule unparseTEAL(return)                        => "return"
  rule unparseTEAL(assert)                        => "assert"
  rule unparseTEAL(pop)                           => "pop"
  rule unparseTEAL(dup)                           => "dup"
  rule unparseTEAL(dup2)                          => "dup2"
  rule unparseTEAL(dig N)                         => "dup" +&+ Int2String(N)
  rule unparseTEAL(select)                        => "select"
  rule unparseTEAL(swap)                          => "swap"
  rule unparseTEAL(ed25519verify)                 => "ed25519verify"
  rule unparseTEAL(arg ArgIdx:Int)                => "arg" +&+ Int2String(ArgIdx)
  rule unparseTEAL(arg_0)                         => "arg_0"
  rule unparseTEAL(arg_1)                         => "arg_1"
  rule unparseTEAL(arg_2)                         => "arg_2"
  rule unparseTEAL(arg_3)                         => "arg_3"
  rule unparseTEAL(balance)                       => "balance"
  rule unparseTEAL(app_global_del)                => "app_global_del"
  rule unparseTEAL(app_global_get)                => "app_global_get"
  rule unparseTEAL(asset_params_get FieldName)    => "asset_params_get" +&+ TealField2String(FieldName:AssetParamsField)
  rule unparseTEAL(app_opted_in)                  => "app_opted_in"
  rule unparseTEAL(app_local_get)                 => "app_local_get"
  rule unparseTEAL(app_global_get_ex)             => "app_global_get_ex"
  rule unparseTEAL(app_global_put)                => "app_global_put"
  rule unparseTEAL(app_local_del)                 => "app_local_del"
  rule unparseTEAL(asset_holding_get FieldName)   => "asset_holding_get" +&+ TealField2String(FieldName:AssetHoldingField)
  rule unparseTEAL(app_local_get_ex)              => "app_local_get_ex"
  rule unparseTEAL(app_local_put)                 => "app_local_put"

  syntax String ::= left:
                    String "+&+" String       [function]
  // ---------------------------------------------------
  rule S:String +&+ S2:String  => S +String " " +String S2

  syntax String ::= Label2String(Label) [function, functional, hook(STRING.token2string)]

  syntax String ::= TealField2String(GlobalField)       [function]
                  | TealField2String(AssetHoldingField) [function]
                  | TealField2String(AssetParamsField)  [function]
                  | TealField2String(TxnField)          [function]
                  | TealField2String(TxnaFieldExt)      [function]
  // -------------------------------------------------------------
  rule TealField2String(MinTxnFee)                => "MinTxnFee"
  rule TealField2String(MinBalance)               => "MinBalance"
  rule TealField2String(MaxTxnLife)               => "MaxTxnLife"
  rule TealField2String(ZeroAddress)              => "ZeroAddress"
  rule TealField2String(GroupSize)                => "GroupSize"
  rule TealField2String(LogicSigVersion)          => "LogicSigVersion"
  rule TealField2String(Round)                    => "Round"
  rule TealField2String(LatestTimestamp)          => "LatestTimestamp"
  rule TealField2String(CurrentApplicationID)     => "CurrentApplicationID"

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
  rule TealField2String(Receiver)                 => "Receiver"
  rule TealField2String(Amount)                   => "Amount"
  rule TealField2String(CloseRemainderTo)         => "CloseRemainderTo"
  rule TealField2String(votePK)                   => "votePK"
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
  rule TealField2String(ForeignApps)              => "ForeignApps"
  rule TealField2String(ForeignAssets)            => "ForeignAssets"

  syntax String ::= TValue2String(TValue)         [function]
                  | TValuePair2String(TValuePair) [function]
  // -------------------------------------------------------
  rule TValue2String(I:Int)              => Int2String(I)
  rule TValue2String(S:String)           => "\"" +String S +String "\""
  rule TValue2String(H:HexToken)         => Hex2String(H)
  rule TValue2String(B:Bytes)            => "0x" +String Base2String(Bytes2Int(B,BE,Unsigned), 16)
  rule TValue2String(TA:TAddressLiteral) => TealAddress2String(TA)
  rule TValuePair2String((TV, TV2))      => "( " +String TValue2String(TV) +String ", " +String  TValue2String(TV2) +String " )"

  syntax String ::= TValueList2String(TValueList)         [function]
                  | TValuePairList2String(TValuePairList) [function]
  // ---------------------------------------------------------------
  rule TValueList2String(TV:TValue TVL:TValueList)             => TValue2String(TV) +&+ TValueList2String(TVL)
  rule TValueList2String(TV:TValue)                            => TValue2String(TV)
  rule TValuePairList2String(TV:TValuePair TVL:TValuePairList) => TValuePair2String(TV) +&+ TValuePairList2String(TVL)
  rule TValuePairList2String(TV:TValuePair)                    => TValuePair2String(TV)

  syntax String ::= IntToken2String(TUInt64Token) [function]
  // -------------------------------------------------------
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
