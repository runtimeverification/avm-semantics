TEAL Fields
===========

TEAL fields refer to names of TEAL opcode immediate arguments. Unlike TEAL
constants, TEAL fields cannot appear as arguments to the `int` psuedo-op;
rather, they can only appear as arguments to their corresponding opcode.

```k
module TEAL-FIELDS
  import TEAL-TYPES-SYNTAX
```

## `global` Fields

```k
  syntax GlobalField ::= "MinTxnFee"
                       | "MinBalance"
                       | "MaxTxnLife"
                       | "ZeroAddress"
                       | "GroupSize"
                       | "LogicSigVersion"
                       | "Round"
                       | "LatestTimestamp"
                       | "CurrentApplicationID"
                       | "CreatorAddress"
                       | "CurrentApplicationAddress"
                       | "OpcodeBudget"
                       | "CreatorAddress"
```

## Asset Fields

### `asset_holding_get` Fields

```k
  syntax AssetHoldingField ::= "AssetBalance"
                             | "AssetFrozen"
```

### `asset_params_get` Fields

```k
  syntax AssetParamsField ::= "AssetTotal" [klabel(AssetTotal), symbol]
                            | "AssetDecimals" [klabel(AssetDecimals), symbol]
                            | "AssetDefaultFrozen" [klabel(AssetDefaultFrozen), symbol]
                            | "AssetUnitName" [klabel(AssetUnitName), symbol]
                            | "AssetName" [klabel(AssetName), symbol]
                            | "AssetURL" [klabel(AssetURL), symbol]
                            | "AssetMetadataHash" [klabel(AssetMetadataHash), symbol]
                            | "AssetManager" [klabel(AssetManager), symbol]
                            | "AssetReserve" [klabel(AssetReserve), symbol]
                            | "AssetFreeze" [klabel(AssetFreeze), symbol]
                            | "AssetClawback" [klabel(AssetClawback), symbol]
                            | "AssetCreator" [klabel(AssetCreator), symbol]
```

### `app_params_get` Fields

```k
  syntax AppParamsField ::= "AppApprovalProgram" [klabel(AppApprovalProgram), symbol]
                          | "AppClearStateProgram" [klabel(AppClearStateProgram), symbol]
                          | "AppGlobalNumUint" [klabel(AppGlobalNumUint), symbol]
                          | "AppGlobalNumByteSlice" [klabel(AppGlobalNumByteSlice), symbol]
                          | "AppLocalNumUint" [klabel(AppLocalNumUint), symbol]
                          | "AppLocalNumByteSlice" [klabel(AppLocalNumByteSlice), symbol]
                          | "AppExtraProgramPages" [klabel(AppExtraProgramPages), symbol]
                          | "AppCreator" [klabel(AppCreator), symbol]
                          | "AppAddress" [klabel(AppAddress), symbol]
```

## Transaction Fields

### `txn`/`gtxn` fields

```k
// Needed because itxn_field accepts both singular and array fields as arguments
  syntax TxnFieldTop ::= TxnField
                       | TxnaField

  syntax TxnField ::= TxnStaticField
                    | TxnDynamicField

  syntax TxnStaticField ::= TxnHeaderField
                    | TxnPayField
                    | TxnKeyregField
                    | TxnAcfgField
                    | TxnAxferField
                    | TxnAfrzField
                    | TxnApplField

  syntax TxnHeaderField ::= "TxID"
                          | "Sender"
                          | "Fee"
                          | "FirstValid"
                          | "FirstValidTime"
                          | "LastValid"
                          | "Note"
                          | "Lease"
                          | "RekeyTo"
                          | "Type"
                          | "TypeEnum"
                          | "GroupIndex"
                          | "StateProofPK"

  // Dynamic fields can only be accessed after the transaction has finished, by subsequent transactions in the
  // group.
  syntax TxnDynamicField ::= "LastLog"
                           | "NumLogs"
                           | "CreatedApplicationID"
                           | "CreatedAssetID"

  syntax TxnPayField    ::= "Receiver"
                          | "Amount"
                          | "CloseRemainderTo"

  syntax TxnKeyregField ::= "VotePK"
                          | "SelectionPK"
                          | "VoteFirst"
                          | "VoteLast"
                          | "VoteKeyDilution"
                          | "Nonparticipation"

  syntax TxnAcfgField   ::= "ConfigAsset"
                          | "ConfigAssetTotal"
                          | "ConfigAssetDecimals"
                          | "ConfigAssetDefaultFrozen"
                          | "ConfigAssetUnitName"
                          | "ConfigAssetName"
                          | "ConfigAssetURL"
                          | "ConfigAssetMetaDataHash"
                          | "ConfigAssetManager"
                          | "ConfigAssetReserve"
                          | "ConfigAssetFreeze"
                          | "ConfigAssetClawback"

  syntax TxnAxferField  ::= "XferAsset"
                          | "AssetAmount"
                          | "AssetSender"
                          | "AssetReceiver"
                          | "AssetCloseTo"

  syntax TxnAfrzField   ::= "FreezeAsset"
                          | "FreezeAssetAccount"
                          | "FreezeAssetFrozen"

  syntax TxnApplField   ::= "ApplicationID"
                          | "OnCompletion"
                          | "NumAppArgs"
                          | "NumAccounts"
                          | "NumAssets"
                          | "NumApplications"
                          | "ApprovalProgram"
                          | "ClearStateProgram"
                          | "ExtraProgramPages"
                          | "NumApprovalProgramPages"
                          | "NumClearStateProgramPages"
                          | "LocalNumByteSlice"
                          | "LocalNumUint"
                          | "GlobalNumByteSlice"
                          | "GlobalNumUint"
```

### `txna`/`gtxna` fields

```k
  syntax TxnaField ::= TxnaStaticField 
                     | TxnaDynamicField

  syntax TxnaStaticField ::= "ApplicationArgs"
                           | "Accounts"
                           | "Applications"
                           | "Assets"

  syntax TxnaDynamicField ::= "Logs"
```

### `acct_params` fields

```k
  syntax AccountParamsField ::= "AcctBalance"
                              | "AcctMinBalance"
                              | "AcctAuthAddr"
```

```k
endmodule
```
