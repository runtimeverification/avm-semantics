TEAL Integer Constants
======================

```k
requires "teal-types.md"
```

TEAL has a set of integer constants which may be passed as arguments to the
`int` psuedo-operation.

```k
module TEAL-CONSTANTS
  import TEAL-TYPES-SYNTAX
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

  // Transaction Types
  // -----------------
  rule normalizeI(NoOp             ) => 0
  rule normalizeI(OptIn            ) => 1
  rule normalizeI(CloseOut         ) => 2
  rule normalizeI(ClearState       ) => 3
  rule normalizeI(UpdateApplication) => 4
  rule normalizeI(DeleteApplication) => 5

  // Oncompletion Action Types
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
endmodule
```
