# Teal program assembly


This implementation operates directly on the Teal human-readable syntax. However, applications have access to
their and other apps bytecode through the `txn` `ApprovalProgram` and `ClearStateProgram` fields, and the
`app_params_get` `AppApprovalProgram` and `AppClearStateProgram` fields, so we still need to have a teal ->
bytecode step for these fields to behave correctly.

This is unimplemented for now, but the `compileTeal` function is useful for passing the type checker.

```k
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-types.md"

module TEAL-ASSEMBLER
  import TEAL-SYNTAX
  import TEAL-TYPES
```

```k
  syntax TBytes ::= compileTeal(TealInputPgm) [function]
  //----------------------------------------------------

  rule compileTeal(_) => .Bytes
```

```k
endmodule
```
