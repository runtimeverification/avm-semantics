Additional Fields
=================

We define a few more fields, in addition to the ones used by TEAL, that can
be used to index other parts of the blockchain state.

```k
module ADDITIONAL-FIELDS
  import TEAL-FIELDS
```

### `asset` Fields

```k
  syntax AssetField ::= "Creator"
```

### `Account` Fields

```k
  syntax AccountField ::= "Amount"
                        | "Round"
                        | "PendingRewards"
                        | "Rewards"
                        | "Status"
```

### `Version` Fields

```k
  syntax VersionField ::= "Versions"
                        | "GenesisID"
                        | "GenesisHash"
```

### Grouping of Field Types

```k
  syntax TealField ::= AssetHoldingField
                     | AssetParamsField
                     | AssetField
                     | AccountField
                     | VersionField
```

```k
endmodule
```
