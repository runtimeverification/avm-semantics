KAVM Configuration and Predicate Macros
=======================================

```k
require "avm/blockchain.md"
```

```k
module MACROS
  imports ALGO-BLOCKCHAIN
```

Accounts data
-------------

### Asset

```k
  syntax AssetCell ::= asset(Int, Int, Int, Bytes) [alias]
  // -----------------------------------------------------
  rule asset(ASSET_ID, ASSET_TOTAL, ASSET_DECIMALS, RESERVE) =>
       <asset>
         <assetID>
           ASSET_ID
         </assetID>
         <assetName>
           b""
         </assetName>
         <assetUnitName>
           b""
         </assetUnitName>
         <assetTotal>
           ASSET_TOTAL
         </assetTotal>
         <assetDecimals>
           ASSET_DECIMALS
         </assetDecimals>
         <assetDefaultFrozen>
           0
         </assetDefaultFrozen>
         <assetURL>
           b""
         </assetURL>
         <assetMetaDataHash>
           b""
         </assetMetaDataHash>
         <assetManagerAddr>
           RESERVE
         </assetManagerAddr>
         <assetReserveAddr>
           RESERVE
         </assetReserveAddr>
         <assetFreezeAddr>
           RESERVE
         </assetFreezeAddr>
         <assetClawbackAddr>
           RESERVE
         </assetClawbackAddr>
       </asset>
```

### Asset Holdings

```k
  syntax OptInAssetCell ::= assetHolding(Int, Int) [alias]
  // -----------------------------------------------------
  rule assetHolding(ASSET_ID, ASSET_BALANCE) =>
       <optInAsset>
         <optInAssetID>
           ASSET_ID
         </optInAssetID>
         <optInAssetBalance>
           ASSET_BALANCE
         </optInAssetBalance>
         <optInAssetFrozen>
           0
         </optInAssetFrozen>
       </optInAsset>
```

Predicates
----------

### Range of types

```k
  syntax Int ::= "pow64"  [alias] /* 2 ^Int 64"  */
  // ----------------------------------------------
  rule pow64  => 18446744073709551616
  syntax Bool ::= #rangeBool    ( Int )             [alias]
                | #rangeUInt    ( Int , Int )       [alias]
  // ------------------------------------------------------
  rule #rangeBool    (            X ) => X ==Int 0 orBool X ==Int 1
  rule #rangeUInt    (  64 ,      X ) => #range ( 0 <= X < pow64 )
  syntax Bool ::= "#range" "(" Int "<"  Int "<"  Int ")" [macro]
                | "#range" "(" Int "<"  Int "<=" Int ")" [macro]
                | "#range" "(" Int "<=" Int "<"  Int ")" [macro]
                | "#range" "(" Int "<=" Int "<=" Int ")" [macro]
  // -----------------------------------------------------------
  rule #range ( LB <  X <  UB ) => LB  <Int X andBool X  <Int UB
  rule #range ( LB <  X <= UB ) => LB  <Int X andBool X <=Int UB
  rule #range ( LB <= X <  UB ) => LB <=Int X andBool X  <Int UB
  rule #range ( LB <= X <= UB ) => LB <=Int X andBool X <=Int UB
```

```k
endmodule
```
