```k
requires "json.md"
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-types.md"
requires "avm/avm-txn-deque.md"
requires "avm/panics.md"
```

```k
module ALGOD-MODELS
    imports JSON
    imports ALGO-BLOCKCHAIN
    imports AVM-CONFIGURATION
    imports AVM-TXN-DEQUE
    imports AVM-PANIC
```


This module defines the transalition of [`algod OpenAPI`](https://raw.githubusercontent.com/algorand/go-algorand/master/daemon/algod/api/algod.oas2.json) specification into KAVM configuration sorts.

## Network State

### Accounts

An account is identified by an address and has nested objects the define the applications and ASAs the account has created.

TODO: if an account contains an app, the state specification must also contain the account of this app. We need to validate that somewhere here.

```k
    syntax KItem ::= #setupAccounts(JSON)
    //-----------------------------------

    rule <k> #setupAccounts([ACCT_JSON, REST]) => #addAccountJSON(ACCT_JSON) ~> #setupAccounts([REST]) ... </k>
    rule <k> #setupAccounts([.JSONs]) => .K ... </k>
```

```k
    syntax KItem ::= #addAccountJSON(JSON)
    //------------------------------------
    rule <k> #addAccountJSON({ "address": ADDR:String
                             , "amount": BALANCE:Int
                             , "created-apps": [APPS:JSONs]
                             , "created-assets": [ASSETS:JSONs]
                             }
             ) => #setupApplications([APPS]) ~> #setupAssets([ASSETS]) ... </k>
         <accountsMap>
           (.Bag =>
           <account>
             <address> DecodeAddressString(ADDR) </address>
             <balance> BALANCE    </balance>
             <key> DecodeAddressString(ADDR) </key>
             <appsCreated> .Bag </appsCreated>
             <appsOptedIn> .Bag </appsOptedIn>
             <assetsCreated> .Bag </assetsCreated>
             <assetsOptedIn> .Bag </assetsOptedIn>
             ...
           </account>)
           ...
         </accountsMap>
    rule <k> #addAccountJSON(INPUT:JSON) => panic("Invalid account JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Assets

```k
    syntax KItem ::= #setupAssets(JSON)
    //---------------------------------

    rule <k> #setupAssets([ASSET_JSON, REST]) => #addAssetJSON(ASSET_JSON) ~> #setupAssets([REST]) ... </k>
    rule <k> #setupAssets([.JSONs]) => .K ... </k>

    syntax KItem ::= #addAssetJSON(JSON)

    rule <k> #addAssetJSON({
                             "index": INDEX:Int,
                             "params": {
                               "clawback": CLAWBACK_ADDR:String,
                               "creator": CREATOR_ADDR_STR:String,
                               "decimals": DECIMALS:Int,
                               "default-frozen": DEFAULT_FROZEN:Bool,
                               "freeze": FREEZE_ADDR:String,
                               "manager": MANAGER_ADDR:String,
                               "metadata-hash": METADATA_HASH:String,
                               "name": ASSET_NAME:String,
                               "reserve": RESERVE_ADDR:String,
                               "total": TOTAL:Int,
                               "unit-name": UNIT_NAME:String,
                               "url": URL:String
                             }
                           }) => .K ... </k>
         <account>
           <address> CREATOR_ADDR </address>
           <assetsCreated>
             .Bag =>
             <asset>
               <assetID> INDEX </assetID>
               <assetName> String2Bytes(ASSET_NAME) </assetName>
               <assetUnitName> String2Bytes(UNIT_NAME) </assetUnitName>
               <assetTotal> TOTAL </assetTotal>
               <assetDecimals> DECIMALS </assetDecimals>
               <assetDefaultFrozen> bool2Int(DEFAULT_FROZEN) </assetDefaultFrozen>
               <assetURL> String2Bytes(URL) </assetURL>
               <assetMetaDataHash> String2Bytes(METADATA_HASH) </assetMetaDataHash>
               <assetManagerAddr> DecodeAddressString(MANAGER_ADDR) </assetManagerAddr>
               <assetReserveAddr> DecodeAddressString(RESERVE_ADDR) </assetReserveAddr>
               <assetFreezeAddr> DecodeAddressString(FREEZE_ADDR) </assetFreezeAddr>
               <assetClawbackAddr> DecodeAddressString(CLAWBACK_ADDR) </assetClawbackAddr>
             </asset>
             ...
           </assetsCreated>
           <assetsOptedIn>
             ASSETS_OPTED_IN =>
             <optInAsset>
               <optInAssetID>      INDEX       </optInAssetID>
               <optInAssetBalance> TOTAL          </optInAssetBalance>
               <optInAssetFrozen>  bool2Int(DEFAULT_FROZEN) </optInAssetFrozen>
             </optInAsset>
             ASSETS_OPTED_IN
           </assetsOptedIn>
           ...
         </account>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
```

### Assets

```k
    syntax KItem ::= #setupAssets(JSON)
    //---------------------------------

    rule <k> #setupAssets([ASSET_JSON, REST]) => #addAssetJSON(ASSET_JSON) ~> #setupAssets([REST]) ... </k>
    rule <k> #setupAssets([.JSONs]) => .K ... </k>

    syntax KItem ::= #addAssetJSON(JSON)

    rule <k> #addAssetJSON({
                             "index": INDEX:Int,
                             "params": {
                               "clawback": CLAWBACK_ADDR:String,
                               "creator": CREATOR_ADDR_STR:String,
                               "decimals": DECIMALS:Int,
                               "default-frozen": DEFAULT_FROZEN:Bool,
                               "freeze": FREEZE_ADDR:String,
                               "manager": MANAGER_ADDR:String,
                               "metadata-hash": METADATA_HASH:String,
                               "name": ASSET_NAME:String,
                               "reserve": RESERVE_ADDR:String,
                               "total": TOTAL:Int,
                               "unit-name": UNIT_NAME:String,
                               "url": URL:String
                             }
                           }) => .K ... </k>
         <account>
           <address> CREATOR_ADDR </address>
           <assetsCreated>
             .Bag =>
             <asset>
               <assetID> INDEX </assetID>
               <assetName> String2Bytes(ASSET_NAME) </assetName>
               <assetUnitName> String2Bytes(UNIT_NAME) </assetUnitName>
               <assetTotal> TOTAL </assetTotal>
               <assetDecimals> DECIMALS </assetDecimals>
               <assetDefaultFrozen> bool2Int(DEFAULT_FROZEN) </assetDefaultFrozen>
               <assetURL> String2Bytes(URL) </assetURL>
               <assetMetaDataHash> String2Bytes(METADATA_HASH) </assetMetaDataHash>
               <assetManagerAddr> DecodeAddressString(MANAGER_ADDR) </assetManagerAddr>
               <assetReserveAddr> DecodeAddressString(RESERVE_ADDR) </assetReserveAddr>
               <assetFreezeAddr> DecodeAddressString(FREEZE_ADDR) </assetFreezeAddr>
               <assetClawbackAddr> DecodeAddressString(CLAWBACK_ADDR) </assetClawbackAddr>
             </asset>
             ...
           </assetsCreated>
           <assetsOptedIn>
             ASSETS_OPTED_IN =>
             <optInAsset>
               <optInAssetID>      INDEX       </optInAssetID>
               <optInAssetBalance> TOTAL          </optInAssetBalance>
               <optInAssetFrozen>  bool2Int(DEFAULT_FROZEN) </optInAssetFrozen>
             </optInAsset>
             ASSETS_OPTED_IN
           </assetsOptedIn>
           ...
         </account>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
```

### Applications

```k
    syntax KItem ::= #setupApplications(JSON)
    //---------------------------------------

    rule <k> #setupApplications([APP_JSON, REST]) => #addApplicationJSON(APP_JSON) ~> #setupApplications([REST]) ... </k>
    rule <k> #setupApplications([.JSONs]) => .K ... </k>

    syntax KItem ::= #addApplicationJSON(JSON)
    //----------------------------------------
    rule <k> #addApplicationJSON({ "id": APP_ID:Int
                                 , "params": { "creator"            : CREATOR_ADDR_STR:String
                                             , "approval-program"   : APPROVAL_NAME:String
                                             , "clear-state-program": CLEAR_STATE_NAME:String
                                             , "extra-progam-pages" : EXTRA_PAGES:Int
                                             , "local-state-schema" : LOCAL_STATE_SCHEMA:String
                                             , "global-state-schema": GLOBAL_STATE_SCHEMA:String
                                             , "global-state"       : GLOBAL_STATE:Int
                                             }
                                 }
             ) => .K ... </k>
           <account>
             <address> CREATOR_ADDR </address>
             <appsCreated>
             (.Bag => <app>
                        <appID>            APP_ID                                                      </appID>
                        <approvalPgmSrc>   {TEAL_PROGRAMS[ APPROVAL_NAME ]}:>TealInputPgm </approvalPgmSrc>
                        <clearStatePgmSrc> {TEAL_PROGRAMS[ CLEAR_STATE_NAME ]}:>TealInputPgm </clearStatePgmSrc>
                          ...
                       </app>)
             ...
             </appsCreated>
             ...
           </account>
           <tealPrograms> TEAL_PROGRAMS </tealPrograms>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
    rule <k> #addApplicationJSON(INPUT:JSON) => panic("Invalid app JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Assets

## Transactions

```k
    syntax KItem ::= #setupTransactions(JSON)
    //---------------------------------------

    rule <k> #setupTransactions([TXN_JSON, REST]) => #addTxnJSON(TXN_JSON) ~> #setupTransactions([REST]) ... </k>
    rule <k> #setupTransactions([.JSONs]) => .K ... </k>

    syntax KItem ::= #addTxnJSON(JSON)
```

```k
  syntax TValueList ::= JSONList2BytesList(JSON) [function]

  rule JSONList2BytesList([.JSONs]) => .TValueList
  rule JSONList2BytesList([ I:Int , REST ]) => prepend(Int2Bytes(I, BE, Unsigned), JSONList2BytesList( [ REST ] ))
  rule JSONList2BytesList([ S:String , REST ]) => prepend(String2Bytes(S), JSONList2BytesList( [ REST ] ))

  syntax TValueList ::= JSONIntList2TUint64List(JSON) [function]

  rule JSONIntList2TUint64List([.JSONs]) => .TValueList
  rule JSONIntList2TUint64List([I:Int, REST]) => prepend(I, JSONIntList2TUint64List([REST]))

  syntax TValueList ::= JSONAccountsList2BytesList(JSON) [function]

  rule JSONAccountsList2BytesList([.JSONs]) => .TValueList
  rule JSONAccountsList2BytesList([S:String, REST]) => prepend(DecodeAddressString(S), JSONAccountsList2BytesList([REST]))

  syntax TValuePairList ::= JSONBoxRefsList2PairList(JSONs) [function]

  rule JSONBoxRefsList2PairList([{ "n": NAME:String, "i": I:Int }:JSON, REST:JSONs]) =>
    prepend((String2Bytes(NAME), I):TValuePair, JSONBoxRefsList2PairList([REST]))
  rule JSONBoxRefsList2PairList([{ "n": NAME:String, "i": I:Int }]) => 
    (String2Bytes(NAME), I):TValuePair
  rule JSONBoxRefsList2PairList([.JSONs]) => .TValuePairList
```

### Payment

```k
    rule <k> #addTxnJSON({
                           "type": "pay",
                           "snd": SENDER:String,
                           "rcv": RECEIVER:String,
                           "amt": AMOUNT:Int
                         })
          => #pushTxnBack(<txID> Int2String(ID) </txID>) ...
        </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> Int2String(ID) </txID>
           <txHeader>
             <sender>      DecodeAddressString(SENDER)   </sender>
             <txType>      "pay"    </txType>
             <typeEnum>    @ pay    </typeEnum>
             <groupID>     Int2String(GROUP_ID) </groupID>
             <groupIdx>    groupSize(Int2String(GROUP_ID), <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <payTxFields>
             <receiver>         DecodeAddressString(RECEIVER) </receiver>
             <amount>           AMOUNT </amount>
             <closeRemainderTo> .Bytes </closeRemainderTo>
           </payTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextGroupID> GROUP_ID </nextGroupID>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Asset transfer

```k
    rule <k> #addTxnJSON({
                           "snd": SENDER:String,
                           "type": "axfer",
                           "xaid": ASSET_ID:Int,
                           "aamt": AMOUNT:Int,
                           "asnd": ASSET_SENDER:String,
                           "arcv": RECEIVER:String,
                           "aclose": CLOSE_TO:String
                         })
          => #pushTxnBack(<txID> Int2String(ID) </txID>) ...
        </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> Int2String(ID) </txID>
           <txHeader>
             <sender>      DecodeAddressString(SENDER)   </sender>
             <txType>      "axfer"    </txType>
             <typeEnum>    @ axfer    </typeEnum>
             <groupID>     Int2String(GROUP_ID) </groupID>
             <groupIdx>    groupSize(Int2String(GROUP_ID), <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <assetTransferTxFields>
             <xferAsset> ASSET_ID </xferAsset>
             <assetAmount> AMOUNT </assetAmount>
             <assetReceiver> DecodeAddressString(RECEIVER) </assetReceiver>
             <assetASender> DecodeAddressString(ASSET_SENDER) </assetASender>
             <assetCloseTo> DecodeAddressString(CLOSE_TO) </assetCloseTo>
           </assetTransferTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextGroupID> GROUP_ID </nextGroupID>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Application Call

```k
    rule <k> #addTxnJSON({
                           "snd":  SENDER:String,
                           "type": "appl",
                           "apid": APPLICATION_ID:Int,
                           "apan": ON_COMPLETION:Int,
                           "apat": ACCOUNTS:JSON,
                           "apaa": APPLICATION_ARGS:JSON,
                           "apfa": FOREIGN_APPS:JSON,
                           "apas": FOREIGN_ASSETS:JSON,
                           "apbx": BOX_REFS:JSON,
                           "apgs": { "nui": GLOBAL_NUM_UINTS:Int, "nbs": GLOBAL_NUM_BYTES:Int },
                           "apls": { "nui": LOCAL_NUM_UINTS:Int, "nbs": LOCAL_NUM_BYTES:Int },
                           "apep": EXTRA_PAGES:Int,
                           "apap": APPROVAL_NAME:String,
                           "apsu": CLEAR_STATE_NAME:String
                         })
          => #pushTxnBack(<txID> Int2String(ID) </txID>) ...
        </k>
        <transactions>
         (.Bag =>
         <transaction>
           <txID> Int2String(ID) </txID>
           <txHeader>
             <sender>      DecodeAddressString(SENDER)   </sender>
             <txType>      "appl"    </txType>
             <typeEnum>    @ appl    </typeEnum>
             <groupID>     Int2String(GROUP_ID) </groupID>
             <groupIdx>    groupSize(Int2String(GROUP_ID), <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <appCallTxFields>
             <applicationID> APPLICATION_ID </applicationID>
             <onCompletion> ON_COMPLETION </onCompletion>
             <approvalProgramSrc> {TEAL_PROGRAMS[ APPROVAL_NAME ]}:>TealInputPgm </approvalProgramSrc>
             <clearStateProgramSrc> {TEAL_PROGRAMS[ CLEAR_STATE_NAME ]}:>TealInputPgm </clearStateProgramSrc>
             <accounts> JSONAccountsList2BytesList(ACCOUNTS) </accounts>
             <applicationArgs> JSONList2BytesList(APPLICATION_ARGS) </applicationArgs>
             <foreignApps> JSONIntList2TUint64List(FOREIGN_APPS) </foreignApps>
             <foreignAssets> JSONIntList2TUint64List(FOREIGN_ASSETS) </foreignAssets>
             <boxReferences> JSONBoxRefsList2PairList(BOX_REFS) </boxReferences>
             <globalStateSchema>
               <globalNui> GLOBAL_NUM_UINTS </globalNui>
               <globalNbs> GLOBAL_NUM_BYTES </globalNbs>
             </globalStateSchema>
             <localStateSchema>
               <localNui> LOCAL_NUM_UINTS </localNui>
               <localNbs> LOCAL_NUM_BYTES </localNbs>
             </localStateSchema>
             <extraProgramPages> EXTRA_PAGES </extraProgramPages>
             ...
           </appCallTxFields>
           ...
         </transaction>)
         TXNS
       </transactions>
       <tealPrograms> TEAL_PROGRAMS </tealPrograms>
       <nextGroupID> GROUP_ID </nextGroupID>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Asset configure

```k
    rule <k> #addTxnJSON({
                           "snd":  SENDER:String,
                           "type": "acfg",
                           "caid": ASSET_ID:Int,
                           "apar": {
                             "t": TOTAL:Int,
                             "dc": DECIMALS:Int,
                             "df": DEFAULT_FROZEN:Bool,
                             "un": UNIT_NAME:String,
                             "an": ASSET_NAME:String,
                             "au": URL:String,
                             "am": METADATA_HASH:String,
                             "m": MANAGER_ADDR:String,
                             "r": RESERVE_ADDR:String,
                             "f": FREEZE_ADDR:String,
                             "c": CLAWBACK_ADDR:String
                           }
                         })
          => #pushTxnBack(<txID> Int2String(ID) </txID>) ...
        </k>
        <transactions>
         (.Bag =>
         <transaction>
           <txID> Int2String(ID) </txID>
           <txHeader>
             <sender>      DecodeAddressString(SENDER)   </sender>
             <txType>      "acfg"    </txType>
             <typeEnum>    @ acfg    </typeEnum>
             <groupID>     Int2String(GROUP_ID) </groupID>
             <groupIdx>    groupSize(Int2String(GROUP_ID), <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <assetConfigTxFields>
             <configAsset> ASSET_ID </configAsset>
             <assetParams>
               <configTotal> TOTAL </configTotal>
               <configDecimals> DECIMALS </configDecimals>
               <configDefaultFrozen> bool2Int(DEFAULT_FROZEN) </configDefaultFrozen>
               <configUnitName> String2Bytes(UNIT_NAME) </configUnitName>
               <configAssetName> String2Bytes(ASSET_NAME) </configAssetName>
               <configAssetURL> String2Bytes(URL) </configAssetURL>
               <configMetaDataHash> String2Bytes(METADATA_HASH) </configMetaDataHash>
               <configManagerAddr> DecodeAddressString(MANAGER_ADDR) </configManagerAddr>
               <configReserveAddr> DecodeAddressString(RESERVE_ADDR) </configReserveAddr>
               <configFreezeAddr> DecodeAddressString(FREEZE_ADDR) </configFreezeAddr>
               <configClawbackAddr> DecodeAddressString(CLAWBACK_ADDR) </configClawbackAddr>
             </assetParams>
           </assetConfigTxFields>
           ...
         </transaction>)
         TXNS
       </transactions>
       <tealPrograms> TEAL_PROGRAMS </tealPrograms>
       <nextGroupID> GROUP_ID </nextGroupID>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```


```k
endmodule
```
