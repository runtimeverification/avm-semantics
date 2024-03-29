Algorand Blockchain Model
=========================

```k
requires "avm/teal/teal-constants.md"
requires "avm/teal/teal-fields.md"
requires "avm/teal/teal-syntax.md"
requires "avm/additional-fields.md"
requires "avm/txn.md"
requires "constants.md"
```

Global Field State Representation
---------------------------------

```k
module GLOBALS
  imports TEAL-CONSTANTS
  imports TEAL-FIELDS
  imports TEAL-TYPES
  imports AVM-CONSTANTS
```

*Global Accessors*

```k
  syntax TValue ::= getGlobalField(GlobalField) [function]
  // ----------------------------------------------------
  rule getGlobalField(MinTxnFee)       => PARAM_MIN_TXN_FEE
  rule getGlobalField(MinBalance)      => PARAM_MIN_BALANCE
  rule getGlobalField(MaxTxnLife)      => PARAM_MAX_TXN_LIFE
  rule getGlobalField(ZeroAddress)     => b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
  rule getGlobalField(LogicSigVersion) => 2
```

*Globals maintained in the state*

```k
  configuration
    <globals>
      <groupSize>                 0 </groupSize>
      <globalRound>               0 </globalRound>
      <latestTimestamp>           0 </latestTimestamp>
      <currentApplicationID>      0 </currentApplicationID>
      <currentApplicationAddress> .Bytes </currentApplicationAddress>
      <creatorAddress>            .Bytes </creatorAddress>
    </globals>
```

*State accessor functions*

```k
  rule [[ getGlobalField(GroupSize) => V ]]
       <globals>
         <groupSize> V </groupSize>
         ...
       </globals>

  rule [[ getGlobalField(Round) => V ]]
       <globals>
         <globalRound> V </globalRound>
         ...
       </globals>

  rule [[ getGlobalField(LatestTimestamp) => V ]]
       <globals>
         <latestTimestamp> V </latestTimestamp>
         ...
       </globals>

  rule [[ getGlobalField(CurrentApplicationID) => V ]]
       <globals>
         <currentApplicationID> V </currentApplicationID>
         ...
       </globals>

  rule [[ getGlobalField(CurrentApplicationAddress) => V ]]
       <globals>
         <currentApplicationAddress> V </currentApplicationAddress>
         ...
       </globals>

  rule [[ getGlobalField(CreatorAddress) => V ]]
       <globals>
         <creatorAddress> V </creatorAddress>
         ...
       </globals>
```

```k
endmodule
```

Application State Representation
--------------------------------

```k
module APPLICATIONS
  imports ALGO-TXN
  imports TEAL-SYNTAX
```

*Application Configuration*

```k
  // Note: - only 64bit keys and 64bit values may be used in the key/value storage
  //       - only up to 64 key-value pairs for global storage and 16 key-value pairs for local storage.
  configuration
    <appsCreated>
      <app multiplicity="*" type="Map">
        <appID>             NoTValue             </appID>
        <approvalPgmSrc>    (int 0):TealInputPgm </approvalPgmSrc>
        <clearStatePgmSrc>  (int 1):TealInputPgm </clearStatePgmSrc>
        <approvalPgm>       NoTValue             </approvalPgm>
        <clearStatePgm>     NoTValue             </clearStatePgm>
        <globalState>
          <globalNumInts>   NoTValue             </globalNumInts>
          <globalNumBytes>  NoTValue             </globalNumBytes>
          <globalBytes>     .Map                 </globalBytes>
          <globalInts>      .Map                 </globalInts>
        </globalState>
        <localState>
          <localNumInts>    NoTValue             </localNumInts>
          <localNumBytes>   NoTValue             </localNumBytes>
        </localState>
        <extraPages>        NoTValue             </extraPages>
      </app>
    </appsCreated>
```

*Opted-in Applications Configuration*

```k
  configuration
    <appsOptedIn>
      <optInApp multiplicity="*" type="Map">
        <optInAppID>   NoTValue </optInAppID>
        <localInts> .Map    </localInts>
        <localBytes> .Map    </localBytes>
      </optInApp>
    </appsOptedIn>

endmodule
```

Asset State Representation
--------------------------

```k
module ASSETS
  imports ALGO-TXN

```

*Asset Configuration*

```k
/*
  Note: - An account may create up to 1000 assets.
        - For every asset an account creates or owns, its minimum balance is increased by 100,000 microAlgos.
        - Before a new asset can be transferred to an account, it must opt-in to receive the asset.
 */

  configuration
    <assetsCreated>
      <asset multiplicity="*" type="Map">
        <assetID>            NoTValue </assetID>
        <assetName>          NoTValue </assetName>
        <assetUnitName>      NoTValue </assetUnitName>
        <assetTotal>         NoTValue </assetTotal>
        <assetDecimals>      NoTValue </assetDecimals>
        <assetDefaultFrozen> NoTValue </assetDefaultFrozen>
        <assetURL>           NoTValue </assetURL>
        <assetMetaDataHash>  NoTValue </assetMetaDataHash>
        <assetManagerAddr>   NoTValue </assetManagerAddr>
        <assetReserveAddr>   NoTValue </assetReserveAddr>
        <assetFreezeAddr>    NoTValue </assetFreezeAddr>
        <assetClawbackAddr>  NoTValue </assetClawbackAddr>
      </asset>
    </assetsCreated>
```

*Opted-in Assets Configuration*

```k
  configuration
    <assetsOptedIn>
      <optInAsset multiplicity="*" type="Map">
        <optInAssetID>      NoTValue </optInAssetID>
        <optInAssetBalance> NoTValue </optInAssetBalance>
        <optInAssetFrozen>  NoTValue </optInAssetFrozen>
      </optInAsset>
    </assetsOptedIn>
endmodule
```

Blockchain State Representation
-------------------------------

```k
module ALGO-BLOCKCHAIN
  imports GLOBALS
  imports APPLICATIONS
  imports ASSETS
  imports ADDITIONAL-FIELDS
  imports TEAL-TYPES-SYNTAX
  imports MAP

  // Note: An address is the base32 encoding of a {pub key + 4-byte checksum}
  // Note: There are three ways in which an account may be created:
  //       1. Creating an address (standard address)
  //       2. Produced by a compiled TEAL program (LogicSig program address)
  //       3. Created through a multisignature account (MultiSig address)
  //          -- not modeled (two more fields: Threshold, list of accounts)

  configuration
    <blockchain>
      <accountsMap>
        <account multiplicity="*" type="Map">
          <address>    "":TBytes </address>
          <balance>    0                  </balance>
          <minBalance> PARAM_MIN_BALANCE  </minBalance> // the default min balance is 0.1 Algo
          <round>      0                  </round>
          <preRewards> 0                  </preRewards>
          <rewards>    0                  </rewards>
          <status>     0                  </status>
          <key>        "":TBytes </key>
          <appsCreated/>
          <appsOptedIn/>
          <assetsCreated/>
          <assetsOptedIn/>
          <boxes>
            <box multiplicity="*" type="Map">
              <boxName> .Bytes </boxName>
              <boxData> .Bytes </boxData>
            </box>
          </boxes>
        </account>
      </accountsMap>
      <appCreator>   .Map </appCreator>   // AppID |-> Creator's address
      <assetCreator> .Map </assetCreator> // AssetID |-> Creator's address
      <blocks>       .Map </blocks>       // Int -> Block (Unused)
      <blockheight>  0    </blockheight>
      <nextAssetID>  1    </nextAssetID>
      <nextAppID>    1    </nextAppID>
      <nextTxnID>    0    </nextTxnID>
      <nextGroupID>  1    </nextGroupID>
      <txnIndexMap>
        <txnIndexMapGroup multiplicity="*" type="Map">
          <txnIndexMapGroupKey> "":String </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> .Map </txnIndexMapGroupValues> // GroupIdx (offset) |-> Transaction ID
        </txnIndexMapGroup>
      </txnIndexMap>
    </blockchain>
```

```k
  syntax String ::= getCurrentTxn() [function]
```

Accessor functions
------------------

### Account State Accessors

```k
  syntax MaybeTValue ::= getAccountParamsField(AccountParamsField, TValue)  [function, total]
  //----------------------------------------------------------------------------------------------
  rule [[ getAccountParamsField(AcctBalance, ADDR) => BAL ]]
       <account>
         <address> ADDR </address>
         <balance> BAL </balance>
         ...
       </account>

  rule [[ getAccountParamsField(AcctMinBalance, ADDR) => MIN_BAL ]]
       <account>
         <address> ADDR </address>
         <minBalance> MIN_BAL </minBalance>
         ...
       </account>

  rule [[ getAccountParamsField(AcctAuthAddr, ADDR) => KEY ]]
       <account>
         <address> ADDR </address>
         <key> KEY </key>
         ...
       </account>

  rule getAccountParamsField(_, _) => NoTValue  [owise]

  syntax MaybeTValue ::= getAppParamsField(AppParamsField, Int) [function, total]
  //----------------------------------------------------------------------------------
  rule [[ getAppParamsField(AppApprovalProgram, APP) => X ]]
       <app>
         <appID> APP </appID>
         <approvalPgm> X </approvalPgm>
         ...
       </app>

  rule [[ getAppParamsField(AppClearStateProgram, APP) => X ]]
       <app>
         <appID> APP </appID>
         <clearStatePgm> X </clearStatePgm>
         ...
       </app>

  rule [[ getAppParamsField(AppGlobalNumUint, APP) => X ]]
       <app>
         <appID> APP </appID>
         <globalNumInts> X </globalNumInts>
         ...
       </app>

  rule [[ getAppParamsField(AppGlobalNumByteSlice, APP) => X ]]
       <app>
         <appID> APP </appID>
         <globalNumBytes> X </globalNumBytes>
         ...
       </app>

  rule [[ getAppParamsField(AppLocalNumUint, APP) => X ]]
       <app>
         <appID> APP </appID>
         <localNumInts> X </localNumInts>
         ...
       </app>

  rule [[ getAppParamsField(AppLocalNumByteSlice, APP) => X ]]
       <app>
         <appID> APP </appID>
         <localNumBytes> X </localNumBytes>
         ...
       </app>

  rule [[ getAppParamsField(AppExtraProgramPages, APP) => X ]]
       <app>
         <appID> APP </appID>
         <extraPages> X </extraPages>
         ...
       </app>

  rule [[ getAppParamsField(AppCreator, APP) => X ]]
       <account>
         <address> X </address>
         <appsCreated>
           <app>
             <appID> APP </appID>
             <extraPages> X </extraPages>
             ...
           </app>
           ...
         </appsCreated>
         ...
       </account>

  rule [[ getAppParamsField(AppAddress, APP) => getAppAddressBytes(APP) ]]
       <accountsMap> AM </accountsMap>
    requires APP in_apps(<accountsMap> AM </accountsMap>)

  rule getAppParamsField(_, _) => NoTValue [owise]

  //TODO: In all accessors below, handle the case when NoTValue is returned

  syntax MaybeTValue ::= getAccountField(AccountField, TValue) [function]
  // -----------------------------------------------------------
  rule getAccountField(Amount, ADDR) => getAccountParamsField(AcctBalance, ADDR)

  rule [[ getAccountField(Round, ADDR) => V ]]
       <account>
         <address> ADDR </address>
         <round> V </round>
         ...
       </account>

  rule [[ getAccountField(PendingRewards, ADDR) => V ]]
       <account>
         <address> ADDR </address>
         <preRewards> V </preRewards>
         ...
       </account>

  rule [[ getAccountField(Rewards, ADDR) => V ]]
       <account>
         <address> ADDR </address>
         <rewards> V </rewards>
         ...
       </account>

  rule [[ getAccountField(Status, ADDR) => V ]]
       <account>
         <address> ADDR </address>
         <status> V </status>
         ...
       </account>

  rule [[ getAccountField(_, ADDR) => -1 ]]
       <accountsMap> AMAP </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))

```

### Asset State Accessors

```k
  syntax Bool ::= hasOptedInAsset(TValue, TValue) [function, total]
  // -----------------------------------------------------
  rule [[ hasOptedInAsset(ASSET, ADDR) => true ]]
       <account>
         <address> ADDR </address>
         <assetsOptedIn>
           <optInAsset>
             <optInAssetID> ASSET </optInAssetID> ...
           </optInAsset> ...
         </assetsOptedIn> ...
       </account>

  rule hasOptedInAsset(_, _) => false [owise]

  syntax TValue ::= getOptInAssetField(AssetHoldingField, TValue, TValue) [function]
  // ----------------------------------------------------------------------------
  rule [[ getOptInAssetField(AssetBalance, ADDR, ASSET) => V ]]
       <account>
         <address> ADDR </address>
         <assetsOptedIn>
           <optInAsset>
             <optInAssetID> ASSET </optInAssetID>
             <optInAssetBalance> V </optInAssetBalance> ...
           </optInAsset> ...
         </assetsOptedIn> ...
       </account>

  rule [[ getOptInAssetField(AssetFrozen, ADDR, ASSET) => V ]]
       <account>
         <address> ADDR </address>
         <assetsOptedIn>
           <optInAsset>
             <optInAssetID> ASSET </optInAssetID>
             <optInAssetFrozen>  V </optInAssetFrozen> ...
           </optInAsset> ...
         </assetsOptedIn> ...
       </account>

  rule [[ getOptInAssetField(_, ADDR, ASSET) => -1 ]]
       <account>
         <address> ADDR </address>
         <assetsOptedIn> OA </assetsOptedIn> ...
       </account>
    requires notBool (ASSET in_optedInAssets(<assetsOptedIn> OA </assetsOptedIn>))

  rule [[ getOptInAssetField(_, ADDR, _) => -1 ]]
       <accountsMap> AMAP </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))


  syntax Bool ::= assetCreated(TValue) [function]
  // -------------------------------------------
  rule [[ assetCreated(ASSET) => true ]]
       <assetCreator> AC </assetCreator>
    requires ASSET in_keys(AC)

  rule [[ assetCreated(ASSET) => false ]]
       <assetCreator> AC </assetCreator>
    requires notBool (ASSET in_keys(AC))

 syntax TValue ::= getAssetInfo(AssetField, TValue) [function]
  // -----------------------------------------------------------
  rule [[ getAssetInfo(Creator, ASSET) => V ]]
       <assetCreator> ASSET |-> V ... </assetCreator>

  rule [[ getAssetInfo(Creator, ASSET) => -1 ]]
       <assetCreator> AMap </assetCreator>
    requires notBool (ASSET in_keys(AMap))


  syntax TValue ::= getAssetParamsField(AssetParamsField, TValue) [function]
  // ---------------------------------------------------------------------
  rule [[ getAssetParamsField(AssetTotal, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetTotal> V </assetTotal> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetDecimals, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetDecimals> V </assetDecimals> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetDefaultFrozen, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetDefaultFrozen> V </assetDefaultFrozen> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetUnitName, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetUnitName> V </assetUnitName> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetName, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetName> V </assetName> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetURL, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetURL> V </assetURL> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetMetadataHash, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetMetaDataHash> V </assetMetaDataHash> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetManager, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetManagerAddr> V </assetManagerAddr> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetReserve, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetReserveAddr> V </assetReserveAddr> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetFreeze, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetFreezeAddr> V </assetFreezeAddr> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetClawback, ASSET) => V ]]
       <assetsCreated>
         <asset>
           <assetID> ASSET </assetID>
           <assetClawbackAddr> V </assetClawbackAddr> ...
         </asset> ...
       </assetsCreated>

  rule [[ getAssetParamsField(AssetCreator, ASSET) => V ]]
       <assetCreator> ASSET |-> V ...</assetCreator>

  rule [[ getAssetParamsField(_, ASSET) => -1 ]]
      <accountsMap> AMAP </accountsMap>
    requires notBool ( ASSET in_assets(<accountsMap> AMAP </accountsMap>) )

  // TODO: what if the asset is there but the specified field is not (for some reason)?


```

### Application State Accessors

```k
  syntax Bool ::= hasOptedInApp(TValue, TValue) [function]
  // ---------------------------------------------------
  rule [[ hasOptedInApp(APP, ADDR) => APP in_optedInApps( <appsOptedIn> O </appsOptedIn> ) ]]
       <account>
         <address> ADDR </address>
         <appsOptedIn> O </appsOptedIn> ...
       </account>

  // if the account doesn't exist, return false
  rule [[ hasOptedInApp(_, ADDR) => false ]]
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))


  syntax MaybeTValue ::= getAppLocal(TValue, TValue, TValue) [function, total]
  // ---------------------------------------------------------
  rule [[ getAppLocal(ADDR, APP, KEY) => V ]]
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> KEY |-> V ... </localInts>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>

  rule [[ getAppLocal(ADDR, APP, KEY) => V ]]
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localBytes> KEY |-> V ... </localBytes>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>

  // If the key isn't set, return -1
  rule [[ getAppLocal(ADDR, APP, KEY) => -1 ]]
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> MI </localInts>
             <localBytes> MB </localBytes>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>
    requires notBool ((KEY in_keys(MI)) orBool (KEY in_keys(MB)))

  // if the account exists but is not opted in, or does not exist, return NoTValue
  rule getAppLocal(_, _, _) => NoTValue [owise]

  syntax TValue ::= getAppGlobal(AppCell, TValue) [function, total]
  // ---------------------------------------------------

  rule getAppGlobal(<app>
                      <globalState>
                        <globalInts> GI:Map </globalInts>
                        <globalBytes> GB:Map </globalBytes>
                        ...
                      </globalState>
                      ...
                    </app>, KEY) =>
          {GI[KEY]}:>Int
    requires ((KEY in_keys(GI)) andThenBool (isInt(GI[KEY])))
     andBool notBool (KEY in_keys(GB)) 

  rule getAppGlobal(<app>
                      <globalState>
                        <globalInts> GI:Map </globalInts>
                        <globalBytes> GB:Map </globalBytes>
                        ...
                      </globalState>
                      ...
                    </app>, KEY) =>
          {GB[KEY]}:>Bytes
    requires ((KEY in_keys(GB)) andThenBool (isBytes(GB[KEY])))
     andBool notBool (KEY in_keys(GI)) 

  // if the app or key doesn't exist, return -1
  rule getAppGlobal(_, _) => -1 [owise]

  syntax Bool ::= appCreated(TValue) [function]
  // -----------------------------------------
  rule [[ appCreated(APP) => true ]]
       <appCreator> APP |-> _ ... </appCreator>

  rule [[ appCreated(APP) => false ]]
       <appCreator> AMap </appCreator>
    requires notBool (APP in_keys(AMap))


```

### Auxiliary Functions

```k
  syntax Bool ::= TValue "in_accounts" "(" AccountsMapCell ")" [function]
  // -------------------------------------------------------------------
  rule ADDR in_accounts( <accountsMap>
                           <account>
                             <address> ADDR </address> ...
                           </account> ...
                         </accountsMap> )
       => true

  rule ADDR in_accounts( <accountsMap>
                           <account>
                             <address> ADDR' </address> ...
                           </account> REST
                         </accountsMap> )
       => ADDR in_accounts (<accountsMap> REST </accountsMap>)
    requires ADDR =/=K ADDR'

  rule _ in_accounts( <accountsMap> .Bag </accountsMap> ) => false

  syntax Bool ::= Bytes "in_boxes" "(" BoxesCell ")" [function]
  //-----------------------------------------------------------
  rule NAME in_boxes(
              <boxes>
                <box>
                  <boxName> NAME </boxName>
                  ...
                </box>
                ...
              </boxes>
            ) => true

  rule NAME in_boxes(
              <boxes>
                <box>
                  <boxName> NAME' </boxName>
                  ...
                </box>
                REST
              </boxes>
            ) => NAME in_boxes(<boxes> REST </boxes>)
    requires NAME =/=K NAME'

  rule _ in_boxes(<boxes> .Bag </boxes>) => false


  syntax Bool ::= TValue "in_optedInApps" "(" AppsOptedInCell ")" [function]
  //-----------------------------------------------------------------------
  rule APP in_optedInApps(
             <appsOptedIn>
               <optInApp>
                 <optInAppID> APP </optInAppID> ...
               </optInApp> ...
             </appsOptedIn>) => true

  rule APP in_optedInApps(
             <appsOptedIn>
               <optInApp>
                 <optInAppID> APP' </optInAppID> ...
               </optInApp> REST
             </appsOptedIn>) => APP in_optedInApps(<appsOptedIn> REST </appsOptedIn>)
    requires APP =/=K APP'

  rule _ in_optedInApps(<appsOptedIn> .Bag </appsOptedIn>) => false

  syntax Bool ::= TValue "in_optedInAssets" "(" AssetsOptedInCell ")" [function]
  // -----------------------------------------------------------------
  rule ASSET in_optedInAssets(<assetsOptedIn>
                       <optInAsset>
                         <optInAssetID> ASSET </optInAssetID> ...
                       </optInAsset> ...
                     </assetsOptedIn>) => true

  rule ASSET in_optedInAssets(<assetsOptedIn>
                       <optInAsset>
                         <optInAssetID> ASSET' </optInAssetID> ...
                       </optInAsset> REST
                     </assetsOptedIn>)
       => ASSET in_optedInAssets(<assetsOptedIn> REST </assetsOptedIn>)
    requires ASSET =/=K ASSET'

  rule _ in_optedInAssets(<assetsOptedIn> .Bag </assetsOptedIn>) => false

  syntax Bool ::= TValue "in_assets" "(" AccountsMapCell ")" [function]
  // -----------------------------------------------------------------
  rule ASSET in_assets(<accountsMap>
                         <account>
                           <assetsCreated> ASSETS </assetsCreated> ...
                         </account> REST
                       </accountsMap> )
       => ASSET in_assets (<assetsCreated> ASSETS </assetsCreated>)
          orBool ASSET in_assets ( <accountsMap> REST </accountsMap> )

  rule _ in_assets( <accountsMap> .Bag </accountsMap> ) => false

  syntax Bool ::= TValue "in_assets" "(" AssetsCreatedCell ")" [function]
  // -----------------------------------------------------------------
  rule ASSET in_assets(<assetsCreated>
                         <asset>
                           <assetID> ASSET </assetID> ...
                         </asset> ...
                       </assetsCreated> ) => true

  rule ASSET in_assets(<assetsCreated>
                         <asset>
                           <assetID> ASSET' </assetID> ...
                         </asset> REST
                       </assetsCreated> )
       => ASSET in_assets(<assetsCreated> REST </assetsCreated>)
    requires ASSET =/=K ASSET'

  rule _ in_assets(<assetsCreated> .Bag </assetsCreated>) => false

  syntax Bool ::= TValue "in_apps" "(" AccountsMapCell ")" [function, total]
  // ----------------------------------------------------------------------------
  rule APP in_apps(<accountsMap>
                     <account>
                       <appsCreated> APPS </appsCreated> ...
                     </account> REST
                   </accountsMap> )
       => APP in_apps (<appsCreated> APPS </appsCreated>)
          orBool APP in_apps ( <accountsMap> REST </accountsMap> )

  rule _ in_apps( <accountsMap> .Bag </accountsMap> ) => false

  syntax Bool ::= TValue "in_apps" "(" AppsCreatedCell ")" [function, total]
  // ----------------------------------------------------------------------------
  rule APP in_apps(<appsCreated>
                     <app>
                       <appID> APP </appID> ...
                     </app> ...
                   </appsCreated> ) => true

  rule APP in_apps(<appsCreated>
                     <app>
                       <appID> APP' </appID> ...
                     </app> REST
                   </appsCreated> )
       => APP in_apps(<appsCreated> REST </appsCreated>)
    requires APP =/=K APP'

  rule _ in_apps(<appsCreated> .Bag </appsCreated>) => false

  syntax Bool ::= String "in_transactions" "(" TransactionsCell ")" [function, total]
  // --------------------------------------------------------------------------------
  rule TXN_ID in_transactions(<transactions>
                                <transaction>
                                  <txID> TXN_ID </txID> ...
                                </transaction> ...
                              </transactions> ) => true

  rule TXN_ID in_transactions(<transactions>
                                <transaction>
                                  <txID> TXN_ID' </txID> ...
                                </transaction> REST
                              </transactions>)
       => TXN_ID in_transactions(<transactions> REST </transactions>)
    requires TXN_ID =/=K TXN_ID'

  rule _ in_transactions(<transactions> .Bag </transactions>) => false
```

### Resource referencing

When referring to accounts, applications, and ASAs, certain opcodes allow not just offsets in the foreign array
fields and addresses (in the case of accounts), application/ASA IDs (in the case of applications and ASAs).
The purpose of `accountReference()`, `appReference()`, and `asaReference()` is to disambiguate these types of
references and also to check that a resource is available.

```k
  syntax MaybeTValue ::= accountReference(TValue) [function, total]
  //--------------------------------------------------------------------
  rule accountReference(A:TBytes ) => A requires accountAvailable(A)
  rule accountReference(I:Int    ) => getTxnField(getCurrentTxn(), Accounts, I)
  rule accountReference(_        ) => NoTValue  [owise]

  syntax MaybeTValue ::= appReference(TUInt64)  [function, total]
  //-----------------------------------------------------------------
  rule appReference(I) => I requires applicationAvailable(I)
  rule appReference(I) => getTxnField(getCurrentTxn(), Applications, I)  [owise]

  syntax MaybeTValue ::= asaReference(TUInt64)  [function, total]
  //------------------------------------------------------------------
  rule asaReference(I) => I requires assetAvailable(I)
  rule asaReference(I) => getTxnField(getCurrentTxn(), Assets, I)  [owise]
```

### Resource Availability

```k
// TODO the associated account of a contract that was created earlier in the group should be available (v 6)
// TODO the associated account of a contract present in the txn.ForeignApplications field should be available (v7)

  syntax Bool ::= accountAvailable(TBytes) [function, total]
  //---------------------------------------------------------------

  rule accountAvailable(A) => true
    requires contains(getTxnField(getCurrentTxn(), Accounts), A)

  rule accountAvailable(A) => true
    requires A ==K getTxnField(getCurrentTxn(), Sender)

  rule accountAvailable(A) => true
    requires A ==K getGlobalField(CurrentApplicationAddress)

  rule accountAvailable(_) => false [owise]

  
// TODO any contract that was created earlier in the same transaction group should be available (v6)

  syntax Bool ::= applicationAvailable(TUInt64) [function, total]
  //------------------------------------------------------------------

  rule applicationAvailable(A) => true
    requires contains(getTxnField(getCurrentTxn(), Applications), A)

  rule applicationAvailable(A) => true
    requires A ==K getGlobalField(CurrentApplicationID)

  rule applicationAvailable(_) => false [owise]


// TODO any asset that was created earlier in the same transaction group should be available (v6)

  syntax Bool ::= assetAvailable(TUInt64) [function, total]
  //------------------------------------------------------------

  rule assetAvailable(A) => true
    requires contains(getTxnField(getCurrentTxn(), Assets), A)

  rule assetAvailable(_) => false [owise]

  syntax Map ::= TValuePairList2Map(TValuePairList, TValueList, Bytes) [function, total]
  //----------------------------------------------------------------------
  rule TValuePairList2Map((A, B):TValuePair REST, APPS, DEFAULT) => ((A |-> getAppAddressBytes({getTValueAt(B -Int 1, APPS)}:>Int)) TValuePairList2Map(REST, APPS, DEFAULT))
    requires B >=Int 1
  rule TValuePairList2Map((A, B):TValuePair, APPS, _) => (A |-> getAppAddressBytes({getTValueAt(B -Int 1, APPS)}:>Int))
    requires B >=Int 1
  rule TValuePairList2Map((A, 0):TValuePair REST, APPS, DEFAULT) => ((A |-> DEFAULT) TValuePairList2Map(REST, APPS, DEFAULT))
  rule TValuePairList2Map((A, 0):TValuePair, _, DEFAULT) => (A |-> DEFAULT)
  rule TValuePairList2Map(.TValuePairList, _, _) => .Map

  syntax Map ::= getBoxRefs(String) [function, total]
  syntax Map ::= getGroupBoxRefs(String) [function, total]
  syntax Map ::= getGroupBoxRefs(Map) [function, total]
  //--------------------------------------------------------

  rule [[ getGroupBoxRefs(GROUP_ID) => getGroupBoxRefs(VALS) ]]
       <txnIndexMapGroup>
         <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
         <txnIndexMapGroupValues> VALS </txnIndexMapGroupValues>
       </txnIndexMapGroup>

  rule getGroupBoxRefs( (_ |-> TXN_ID) REST) => getGroupBoxRefs(REST) getBoxRefs(TXN_ID)
  rule getGroupBoxRefs( .Map) => .Map

  rule [[ getBoxRefs(TXN_ID) => TValuePairList2Map(REFS, FA, getAppAddressBytes({getGlobalField(CurrentApplicationID)}:>Int)) ]]
       <transaction>
         <txID> TXN_ID </txID>
         <foreignApps> FA </foreignApps>
         <boxReferences> REFS </boxReferences>
         ...
       </transaction>

  rule [[ getBoxRefs(TXN_ID) => .Map ]]
       <transaction>
         <txID> TXN_ID </txID>
         <txnTypeSpecificFields>
           .AppCallTxFieldsCell
           ...
         </txnTypeSpecificFields>
         ...
       </transaction>

  syntax MaybeTValue ::= boxAcct(Bytes) [function, total]
  //--------------------------------------------------------------------
  rule boxAcct(NAME) => {getGroupBoxRefs(getTxnGroupID(getCurrentTxn()))[NAME]}:>Bytes
    requires NAME in_keys(getGroupBoxRefs(getTxnGroupID(getCurrentTxn())))

  rule boxAcct(_) => NoTValue [owise]


```

### Transaction Index Accessors

The transaction index connects a transaction groups ID to the transaction IDs comprising the group

```k

  syntax MaybeTValue ::= getGroupFieldByIdx(String, Int, TxnField) [function]
  syntax MaybeTValue ::= getGroupFieldByIdx(String, Int, TxnaField, Int) [function]

  rule [[ getGroupFieldByIdx(GROUP_ID, GROUP_INDEX, FIELD) => getTxnField({MV[GROUP_INDEX]}:>String, FIELD) ]]
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> MV </txnIndexMapGroupValues>
        </txnIndexMapGroup>

  rule [[ getGroupFieldByIdx(GROUP_ID, GROUP_INDEX, FIELD, FIELD_INDEX) => getTxnField( {MV[GROUP_INDEX]}:>String, FIELD, FIELD_INDEX) ]]
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> MV </txnIndexMapGroupValues>
        </txnIndexMapGroup>

  rule getGroupFieldByIdx(_, _, _) => NoTValue [owise]

endmodule
```
