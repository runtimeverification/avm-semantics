TEAL Integer Constants
======================

```k
requires "avm/teal/teal-types.md"
```

TEAL has a set of integer constants which may be passed as arguments to the
`int` psuedo-operation.

```k
module TEAL-CONSTANTS
  import TEAL-TYPES-SYNTAX
  import BYTES
```

A pusedo unsigned 64-bit integer is an immediate argument to an `int`
psuedo-operation.

```k
  syntax PseudoTUInt64 ::= TUInt64
                         | TUInt64Token
```

Transaction Types
-----------------

- unknown transaction type (invalid transaction)
- payment
- key registration
- asset configuration (create, configure, or destroy asset types)
- asset transfer (transfer, accept, or clawback a given asset)
- assert freeze (prevent account from send/receiving asset)
- application call (invoke stateful TEAL program)
- off-chain contract configuration (create, configure, or destory contract)
- off-chain contract call (call a contract)
- off-chain contract effects group (record effects of contract)

```k
  syntax TUInt64Token ::= "unknown"
                        | "pay"
                        | "keyreg"
                        | "acfg"
                        | "axfer"
                        | "afrz"
                        | "appl"
                        | "ccfg"
                        | "ccall"
                        | "cfx"
```

Oncompletion Action Types
-------------------------

For application call transactions (`appl`), this value defines what additional
actions occur when the transaction completes.

```k
  syntax TUInt64Token ::= "NoOp"
                        | "OptIn"
                        | "CloseOut"
                        | "ClearState"
                        | "UpdateApplication"
                        | "DeleteApplication"
```

```k
  syntax TValue ::= normalizeI(PseudoTUInt64) [function, functional]
  // ---------------------------------------------------------------
  rule normalizeI(V:TUInt64) => V

  // Oncompletion Action Types
  // -----------------
  rule normalizeI(NoOp             ) => 0
  rule normalizeI(OptIn            ) => 1
  rule normalizeI(CloseOut         ) => 2
  rule normalizeI(ClearState       ) => 3
  rule normalizeI(UpdateApplication) => 4
  rule normalizeI(DeleteApplication) => 5

  // Transaction Types
  // -------------------------
  rule normalizeI(unknown          ) => 0
  rule normalizeI(pay              ) => 1
  rule normalizeI(keyreg           ) => 2
  rule normalizeI(acfg             ) => 3
  rule normalizeI(axfer            ) => 4
  rule normalizeI(afrz             ) => 5
  rule normalizeI(appl             ) => 6
  rule normalizeI(ccfg             ) => 7
  rule normalizeI(ccall            ) => 8
  rule normalizeI(cfx              ) => 9


  syntax Int ::= "@" TUInt64Token [macro]
  // ------------------------------------
  rule @ NoOp              => 0
  rule @ OptIn             => 1
  rule @ CloseOut          => 2
  rule @ ClearState        => 3
  rule @ UpdateApplication => 4
  rule @ DeleteApplication => 5

  rule @ unknown           => 0
  rule @ pay               => 1
  rule @ keyreg            => 2
  rule @ acfg              => 3
  rule @ axfer             => 4
  rule @ afrz              => 5
  rule @ appl              => 6
  rule @ ccfg              => 7
  rule @ ccall             => 8
  rule @ cfx               => 9

  syntax Int ::= typeString2Enum(Bytes) [function]
  //----------------------------------------------
  rule typeString2Enum(b"unknown") => @ unknown
  rule typeString2Enum(b"pay")     => @ pay
  rule typeString2Enum(b"keyreg")  => @ keyreg
  rule typeString2Enum(b"acfg")    => @ acfg
  rule typeString2Enum(b"axfer")   => @ axfer
  rule typeString2Enum(b"afrz")    => @ afrz
  rule typeString2Enum(b"appl")    => @ appl
  rule typeString2Enum(b"ccfg")    => @ ccfg
  rule typeString2Enum(b"ccall")   => @ ccall
  rule typeString2Enum(b"cfx")     => @ cfx

  syntax Bytes ::= typeEnum2String(Int) [function]
  //----------------------------------------------
  rule typeEnum2String(@ unknown) => b"unknown"
  rule typeEnum2String(@ pay)     => b"pay"
  rule typeEnum2String(@ keyreg)  => b"keyreg"
  rule typeEnum2String(@ acfg)    => b"acfg"
  rule typeEnum2String(@ axfer)   => b"axfer"
  rule typeEnum2String(@ afrz)    => b"afrz"
  rule typeEnum2String(@ appl)    => b"appl"
  rule typeEnum2String(@ ccfg)    => b"ccfg"
  rule typeEnum2String(@ ccall)   => b"ccal"
  rule typeEnum2String(@ cfx)     => b"cfx"

endmodule
```
