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
    syntax KItem ::= #setupOptInAssets(Bytes, JSONs)
    //----------------------------------------------
    rule <k> #setupOptInAssets(ADDR:Bytes, (
                          {
                            "amount": AMOUNT:Int,
                            "asset-id": ASSET_ID:Int,
                            "is-frozen": FROZEN:Bool
                          }, REST:JSONs):JSONs)
            => #setupOptInAssets(ADDR, REST)
            ...
          </k>
          <account>
            <address> ADDR </address>
            <assetsOptedIn>
              (.Bag =>
              <optInAsset>
                <optInAssetID> ASSET_ID </optInAssetID>
                <optInAssetBalance> AMOUNT </optInAssetBalance>
                <optInAssetFrozen> bool2Int(FROZEN) </optInAssetFrozen>
              </optInAsset>)
              ...
            </assetsOptedIn>
            ...
          </account>

    rule <k> #setupOptInAssets(_:Bytes, .JSONs) => . ... </k>

    syntax KItem ::= #addAccountJSON(JSON)
    //------------------------------------
    rule <k> #addAccountJSON({"address": ADDR:String,
                              "amount": BALANCE:Int,
                              "amount-without-pending-rewards": null,
                              "apps-local-state": [LOCAL_STATE:JSONs],
                              "apps-total-schema": null,
                              "assets": [OPTIN_ASSETS:JSONs],
                              "auth-addr": null,
                              "created-apps": [APPS:JSONs],
                              "created-assets": [ASSETS:JSONs],
                              "participation": null,
                              "pending-rewards": null,
                              "reward-base": null,
                              "rewards": null,
                              "round": null,
                              "sig-type": null,
                              "status": null
                             })
            => #setupApplications([APPS])
            ~> #loadLocalState(DecodeAddressString(ADDR), [LOCAL_STATE])
            ~> #setupAssets([ASSETS])
            ~> #setupOptInAssets(DecodeAddressString(ADDR), OPTIN_ASSETS)
            ...
         </k>
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

    syntax JSONs ::= #dumpAccounts(AccountsMapCell)            [function]
                   | #dumpAccountsImpl(JSONs, AccountsMapCell) [function]
    //-------------------------------------------------------------------
    rule #dumpAccounts(<accountsMap> ACCTS </accountsMap>)
      => #dumpAccountsImpl((.JSONs), <accountsMap> ACCTS </accountsMap>)
    rule #dumpAccountsImpl(
         (SERIALIZED:JSONs),
         <accountsMap>
           <account> ACCT </account>
           REST
         </accountsMap>)
      => #dumpAccountsImpl((#dumpAccountJSON(<account> ACCT </account>) , SERIALIZED) , <accountsMap> REST </accountsMap>)
    rule #dumpAccountsImpl(
         (SERIALIZED:JSONs),
         <accountsMap>
           .Bag
         </accountsMap>)
      => SERIALIZED

    syntax JSON ::= #dumpAccountJSON(AccountCell) [function]
    //------------------------------------------------------
    rule #dumpAccountJSON(
             <account>
               <address> ADDR:Bytes </address>
               <balance> BALANCE:Int </balance>
               <appsCreated> APPS </appsCreated>
               ...
             </account>)
          => {"address": EncodeAddressBytes(ADDR),
              "amount": BALANCE,
              "amount-without-pending-rewards": null,
              "apps-local-state": null,
              "apps-total-schema": null,
              "assets": null,
              "created-apps": [#dumpApps(EncodeAddressBytes(ADDR),<appsCreated> APPS </appsCreated>)],
              "created-assets": [.JSONs],
              "participation": null,
              "pending-rewards": null,
              "reward-base": null,
              "rewards": null,
              "round": null,
              "status": null,
              "sig-type": null,
              "auth-addr": null
             }
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
           ...
         </account>
         <assetCreator> (.Map => (INDEX |-> CREATOR_ADDR)) ... </assetCreator>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
```

### Applications

```k
    syntax KItem ::= #loadLocalState(Bytes, JSONs)
                   | #loadLocalState(Int, Bytes, JSONs)
    //-------------------------------------------------
    rule <k> #loadLocalState(ADDR:Bytes,
                  [{
                     "id": APP_ID:Int,
                     "key-value": [LOCAL_STATE],
                     "schema": _:JSON
                   }, REST:JSONs] )
          => #loadLocalState(APP_ID, ADDR, [LOCAL_STATE]) ~> #loadLocalState(ADDR, [REST]) ... </k>
         <account>
           <address> ADDR </address>
           <appsOptedIn>
             (.Bag =>
             <optInApp>
               <optInAppID> APP_ID </optInAppID>
               <localInts> .Map </localInts>
               <localBytes> .Map </localBytes>
             </optInApp>)
             ...
           </appsOptedIn>
           ...
         </account>

    rule <k> #loadLocalState(_:Bytes, [ .JSONs ]) => . ... </k>

    rule <k> #loadLocalState(APP_ID:Int, ADDR:Bytes,
                             [{"key": K:String, "value": {"bytes": V:String, "type": 1, "uint": _} }, REST:JSONs])
          => #loadLocalState(APP_ID, ADDR, [REST]) ... </k>
         <account>
           <address> ADDR </address>
           <appsOptedIn>
             <optInApp>
               <optInAppID> APP_ID </optInAppID>
               <localInts> _ </localInts>
               <localBytes> .Map => (Base64Decode(K) |-> Base64Decode(V)) ... </localBytes>
             </optInApp>
             ...
           </appsOptedIn>
           ...
         </account>

    rule <k> #loadLocalState(APP_ID:Int, ADDR:Bytes,
                             [{"key": K:String, "value": {"bytes": _, "type": 2, "uint": V:Int} }, REST:JSONs])
          => #loadLocalState(APP_ID, ADDR, [REST]) ... </k>
         <account>
           <address> ADDR </address>
           <appsOptedIn>
             <optInApp>
               <optInAppID> APP_ID </optInAppID>
               <localInts> .Map => (Base64Decode(K) |-> V) ... </localInts>
               <localBytes> _ </localBytes>
             </optInApp>
             ...
           </appsOptedIn>
           ...
         </account>

    rule <k> #loadLocalState(_:Int, _:Bytes, [.JSONs]) => . ... </k>

    syntax KItem ::= #loadGlobalState(Int, JSONs)
    //-------------------------------------------
    rule <k> #loadGlobalState(APP_ID, [{"key": K:String, "value": {"bytes": V:String, "type": 1, "uint": _} }, REST:JSONs] )
          => #loadGlobalState(APP_ID, [REST]) ... </k>
         <app>
           <appID> APP_ID </appID>
           <globalState>
             <globalBytes> .Map => (Base64Decode(K) |-> Base64Decode(V)) ... </globalBytes>
             ...
           </globalState>
           ...
         </app>

    rule <k> #loadGlobalState(APP_ID, [{"key": K:String, "value": {"bytes": _, "type": 2, "uint": V:Int} }, REST:JSONs] )
          => #loadGlobalState(APP_ID, [REST]) ... </k>
         <app>
           <appID> APP_ID </appID>
           <globalState>
             <globalInts> .Map => (Base64Decode(K) |-> V) ... </globalInts>
             ...
           </globalState>
           ...
         </app>
    rule <k> #loadGlobalState(_, [.JSONs]) => . ... </k>

    syntax KItem ::= #setupApplications(JSON)
    //---------------------------------------

    rule <k> #setupApplications([APP_JSON, REST]) => #addApplicationJSON(APP_JSON) ~> #setupApplications([REST]) ... </k>
    rule <k> #setupApplications([.JSONs])         => .K ... </k>
    rule <k> #setupApplications(null)             => .K ... </k>

    syntax KItem ::= #addApplicationJSON(JSON)
    //----------------------------------------
    rule <k> #addApplicationJSON({ "id": APP_ID:Int
                                 , "params": { "approval-program"   : APPROVAL_NAME:String
                                             , "clear-state-program": CLEAR_STATE_NAME:String
                                             , "creator"            : CREATOR_ADDR_STR:String
                                             , "global-state"       : [GLOBAL_STATE:JSONs]
                                             , "global-state-schema": { "nbs": GLOBAL_NUM_BYTES:Int, "nui": GLOBAL_NUM_UINTS:Int }
                                             , "local-state-schema" : { "nbs": LOCAL_NUM_BYTES:Int, "nui": LOCAL_NUM_UINTS:Int }
                                             }
                                 }
             ) => #loadGlobalState(APP_ID, [GLOBAL_STATE]) ... </k>
           <account>
             <address> CREATOR_ADDR </address>
             <appsCreated>
             (.Bag => <app>
                        <appID>            APP_ID                                            </appID>
                        <approvalPgm>  APPROVAL_NAME                                     </approvalPgm>
                        <approvalPgmSrc>   {TEAL_PROGRAMS[ APPROVAL_NAME ]}:>TealInputPgm    </approvalPgmSrc>
                        <clearStatePgm> CLEAR_STATE_NAME                                 </clearStatePgm>
                        <clearStatePgmSrc> {TEAL_PROGRAMS[ CLEAR_STATE_NAME ]}:>TealInputPgm </clearStatePgmSrc>
                        <globalState>
                          <globalNumInts>   GLOBAL_NUM_UINTS      </globalNumInts>
                          <globalNumBytes>  GLOBAL_NUM_BYTES      </globalNumBytes>
                          ...
                        </globalState>
                        <localState>
                          <localNumInts>    LOCAL_NUM_UINTS       </localNumInts>
                          <localNumBytes>   LOCAL_NUM_BYTES       </localNumBytes>
                        </localState>
                          ...
                       </app>)
             ...
             </appsCreated>
             ...
           </account>
           <tealPrograms> TEAL_PROGRAMS </tealPrograms>
           <appCreator> (.Map => (APP_ID |-> DecodeAddressString(CREATOR_ADDR_STR))) ... </appCreator>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
    rule <k> #addApplicationJSON(INPUT:JSON) => panic("Invalid app JSON:" +String JSON2String(INPUT)) ... </k> [owise]

    syntax JSONs ::= #dumpApps(String, AppsCreatedCell)            [function]
                   | #dumpAppsImpl(String, JSONs, AppsCreatedCell) [function]
    //-----------------------------------------------------------------------
    rule #dumpApps((CREATOR:String), <appsCreated> APPS </appsCreated>)
      => #dumpAppsImpl((CREATOR:String), (.JSONs), <appsCreated> APPS </appsCreated>)
    rule #dumpAppsImpl(
         (CREATOR:String),
         (SERIALIZED:JSONs),
         <appsCreated>
           <app> APP </app>
           REST
         </appsCreated>)
      => #dumpAppsImpl((CREATOR:String), (#dumpAppJSON((CREATOR:String), <app> APP </app>) , SERIALIZED) , <appsCreated> REST </appsCreated>)
    rule #dumpAppsImpl(
         (_CREATOR:String),
         (SERIALIZED:JSONs),
         <appsCreated>
           .Bag
         </appsCreated>)
      => SERIALIZED


    syntax JSON ::= #dumpAppJSON(String, AppCell) [function]
    //------------------------------------------------------
    rule #dumpAppJSON(
             (CREATOR:String),
             <app>
               <appID>             APP_ID:Int              </appID>
               <approvalPgm>   APPROVAL_NAME:String           </approvalPgm>
               <clearStatePgm> CLEAR_STATE_NAME:String        </clearStatePgm>
               <globalState>
                 <globalNumInts>   GLOBAL_NUM_UINTS      </globalNumInts>
                 <globalNumBytes>  GLOBAL_NUM_BYTES      </globalNumBytes>
                 <globalBytes>     GLOBAL_UINTS:Map      </globalBytes>
                 <globalInts>      GLOBAL_BYTES:Map      </globalInts>
               </globalState>
               <localState>
                 <localNumInts>    LOCAL_NUM_UINTS       </localNumInts>
                 <localNumBytes>   LOCAL_NUM_BYTES       </localNumBytes>
               </localState>
               <extraPages>        _EXTRA_PAGES           </extraPages>
               ...
             </app>)
          => { "id": APP_ID
             , "params": { "creator"            : CREATOR
                         , "approval-program"   : APPROVAL_NAME
                         , "clear-state-program": CLEAR_STATE_NAME
                         , "local-state-schema" : { "nbs": maybeTUInt64(LOCAL_NUM_BYTES, 0)
                                                  , "nui": maybeTUInt64(LOCAL_NUM_UINTS, 0) }
                         , "global-state-schema": { "nbs": maybeTUInt64(GLOBAL_NUM_BYTES, 0)
                                                  , "nui": maybeTUInt64(GLOBAL_NUM_UINTS, 0) }
                         , "global-state"       : [ #dumpStateMap(GLOBAL_UINTS GLOBAL_BYTES) ]
                         }
             }

    syntax JSONs ::= #dumpStateMap(Map) [function]
    //--------------------------------------------
    rule #dumpStateMap((KEY:Bytes |-> VALUE:Bytes) REST)
      => {"key": Base64Encode(KEY):String, "value": {"bytes": Base64Encode(VALUE), "type": 1, "uint": 0 } }, #dumpStateMap(REST)
    rule #dumpStateMap((KEY:Bytes |-> VALUE:Int  ) REST)
      => {"key": Base64Encode(KEY):String, "value": {"bytes": "", "type": 2, "uint": VALUE} }, #dumpStateMap(REST)
    rule #dumpStateMap(.Map) => .JSONs
```

## Transactions

```k

    syntax String ::= #getTxnJSONType(JSON) [function]
    //------------------------------------------------
    rule #getTxnJSONType({ "type": TYPE:String,  _}) => TYPE
    rule #getTxnJSONType({ KEY: _, REST}) => #getTxnJSONType(REST)
      requires notBool (KEY ==String "type")
    rule #getTxnJSONType({ .JSONs }) => "undef"


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
  rule JSONList2BytesList([ S:String , REST ]) => prepend(Base64Decode(S), JSONList2BytesList( [ REST ] ))

  syntax TValueList ::= JSONIntList2TUint64List(JSON) [function]

  rule JSONIntList2TUint64List([.JSONs]) => .TValueList
  rule JSONIntList2TUint64List([I:Int, REST]) => prepend(I, JSONIntList2TUint64List([REST]))

  syntax TValueList ::= JSONAccountsList2BytesList(JSON) [function]

  rule JSONAccountsList2BytesList([.JSONs]) => .TValueList
  rule JSONAccountsList2BytesList([S:String, REST]) => prepend(DecodeAddressString(S), JSONAccountsList2BytesList([REST]))

  syntax TValuePairList ::= JSONBoxRefsList2PairList(JSONs) [function]

  rule JSONBoxRefsList2PairList([{ "i": I:Int, "n": NAME:String  }:JSON, REST:JSONs]) =>
    prepend((String2Bytes(NAME), I):TValuePair, JSONBoxRefsList2PairList([REST]))
  rule JSONBoxRefsList2PairList([{ "i": I:Int , "n": NAME:String }]) =>
    (String2Bytes(NAME), I):TValuePair
  rule JSONBoxRefsList2PairList([.JSONs]) => .TValuePairList
```

### Payment

```k
    rule <k> #addTxnJSON({ "amt": AMOUNT:Int,
                           "fee": _FEE:Int,
                           "fv": _FIRST_VALID:Int,
                           "gen": _GEN:String,
                           "gh": _,
                           "grp": GROUP_ID:String,
                           "lv": _LAST_VALID:Int,
                           "rcv": RECEIVER:String,
                           "snd": SENDER:String,
                           "type": "pay"
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
             <groupID>     GROUP_ID </groupID>
             <groupIdx>    groupSize(GROUP_ID, <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <payTxFields>
             <receiver>         DecodeAddressString(RECEIVER) </receiver>
             <amount>           AMOUNT </amount>
             <closeRemainderTo> PARAM_ZERO_ADDR </closeRemainderTo>
           </payTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Asset transfer

```k
    rule <k> #addTxnJSON({
                           "aamt": AMOUNT:Int,
                           "aclose": CLOSE_TO:JSON,
                           "arcv": RECEIVER:String,
                           "asnd": _ASSET_ASENDER,
                           "fee": _FEE:Int,
                           "fv": _FIRST_VALID:Int,
                           "gen": _GEN:String,
                           "gh": _,
                           "grp": GROUP_ID:String,
                           "lv": _LAST_VALID:Int,
                           "snd": SENDER:String,
                           "type": "axfer",
                           "xaid": ASSET_ID:Int
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
             <groupID>     GROUP_ID </groupID>
             <groupIdx>    groupSize(GROUP_ID, <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <assetTransferTxFields>
             <xferAsset> ASSET_ID </xferAsset>
             <assetAmount> AMOUNT </assetAmount>
             <assetReceiver> DecodeAddressString(RECEIVER) </assetReceiver>
             <assetASender> PARAM_ZERO_ADDR </assetASender>
             <assetCloseTo> #if isString(CLOSE_TO) #then DecodeAddressString({CLOSE_TO}:>String) #else PARAM_ZERO_ADDR #fi </assetCloseTo>
           </assetTransferTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Asset freeze

```k
    rule <k> #addTxnJSON({
                           "afrz": FROZEN:Bool,
                           "fadd": FREEZE_ADDR:String,
                           "faid": ASSET_ID:Int,
                           "fee": _FEE:Int,
                           "fv": _FIRST_VALID:Int,
                           "gen": _GEN:String,
                           "gh": _,
                           "grp": GROUP_ID:String,
                           "lv": _LAST_VALID:Int,
                           "snd": SENDER:String,
                           "type": "afrz"
                         })
          => #pushTxnBack(<txID> Int2String(ID) </txID>) ...
        </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> Int2String(ID) </txID>
           <txHeader>
             <sender>      DecodeAddressString(SENDER)   </sender>
             <txType>      "afrz"    </txType>
             <typeEnum>    @ afrz    </typeEnum>
             <groupID>     GROUP_ID </groupID>
             <groupIdx>    groupSize(GROUP_ID, <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <assetFreezeTxFields>
             <freezeAccount> DecodeAddressString(FREEZE_ADDR) </freezeAccount>
             <freezeAsset> ASSET_ID </freezeAsset>
             <assetFrozen> bool2Int(FROZEN) </assetFrozen>
           </assetFreezeTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Application Call

```k
    rule <k> #addTxnJSON({
                           "apaa": APPLICATION_ARGS:JSON,
                           "apan": ON_COMPLETION:Int,
                           "apap": APPROVAL_NAME:JSON,
                           "apas": FOREIGN_ASSETS:JSON,
                           "apat": ACCOUNTS:JSON,
                           "apbx": BOX_REFS:JSON,
                           "apep": EXTRA_PAGES:Int,
                           "apfa": FOREIGN_APPS:JSON,
                           "apgs": { "nbs": GLOBAL_NUM_BYTES:Int, "nui": GLOBAL_NUM_UINTS:Int },
                           "apid": APPLICATION_ID:Int,
                           "apls": { "nbs": LOCAL_NUM_BYTES:Int, "nui": LOCAL_NUM_UINTS:Int },
                           "apsu": CLEAR_STATE_NAME:JSON,
                           "fee": _FEE:Int,
                           "fv": _FIRST_VALID:Int,
                           "gen": _GEN:String,
                           "gh": _,
                           "grp": GROUP_ID:String,
                           "lv": _LAST_VALID:Int,
                           "snd":  SENDER:String,
                           "type": "appl"
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
             <groupID>     GROUP_ID </groupID>
             <groupIdx>    groupSize(GROUP_ID, <transactions> TXNS </transactions>) </groupIdx>
             ...           // other fields will receive default values
           </txHeader>
           <appCallTxFields>
             <applicationID> APPLICATION_ID </applicationID>
             <onCompletion> ON_COMPLETION </onCompletion>
             <approvalProgramSrc>
               #if isString(progamFromJSON(APPROVAL_NAME)) #then {TEAL_PROGRAMS[ APPROVAL_NAME ]}:>TealInputPgm #else err:TealInputPgm #fi
              </approvalProgramSrc>
             <clearStateProgramSrc>
               #if isString(progamFromJSON(CLEAR_STATE_NAME)) #then {TEAL_PROGRAMS[ CLEAR_STATE_NAME ]}:>TealInputPgm #else err:TealInputPgm #fi
             </clearStateProgramSrc>
             <approvalProgram>      progamFromJSON(APPROVAL_NAME)     </approvalProgram>
             <clearStateProgram>    progamFromJSON(CLEAR_STATE_NAME)  </clearStateProgram>
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
       <nextTxnID> ID => ID +Int 1 </nextTxnID>

    syntax MaybeTValue ::= progamFromJSON(JSON) [function, total]
    //----------------------------------------------------------------
    rule progamFromJSON(PGM:String) => PGM
    rule progamFromJSON(_)          => NoTValue [owise]
```

### Asset configure

```k
    rule <k> #addTxnJSON({
                           "apar": {
                             "am": METADATA_HASH:String,
                             "an": ASSET_NAME:String,
                             "au": URL:String,
                             "c": CLAWBACK_ADDR:String,
                             "dc": DECIMALS:Int,
                             "df": DEFAULT_FROZEN:Bool,
                             "f": FREEZE_ADDR:String,
                             "m": MANAGER_ADDR:String,
                             "r": RESERVE_ADDR:String,
                             "t": TOTAL:Int,
                             "un": UNIT_NAME:String

                           },
                           "caid": ASSET_ID:Int,
                           "fee": _FEE:Int,
                           "fv": _FIRST_VALID:Int,
                           "gen": _GEN:String,
                           "gh": _,
                           "grp": GROUP_ID:String,
                           "lv": _LAST_VALID:Int,
                           "snd":  SENDER:String,
                           "type": "acfg"
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
             <groupID>     GROUP_ID </groupID>
             <groupIdx>    groupSize(GROUP_ID, <transactions> TXNS </transactions>) </groupIdx>
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
       <tealPrograms> _TEAL_PROGRAMS </tealPrograms>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

### Invalid input

```k
    rule <k> #addTxnJSON(INPUT:JSON) => panic("Invalid transaction JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```


```k
    syntax JSONs ::= #dumpConfirmedTransactions(TransactionsCell)            [function]
                   | #dumpConfirmedTransactionsImpl(JSONs, TransactionsCell) [function]
    //-------------------------------------------------------------------
    rule #dumpConfirmedTransactions(<transactions> TXNS </transactions>)
      => #dumpConfirmedTransactionsImpl((.JSONs), <transactions> TXNS </transactions>)
    rule #dumpConfirmedTransactionsImpl(
         (SERIALIZED:JSONs),
         <transactions>
           <transaction> TXN </transaction>
           REST
         </transactions>)
      => #dumpConfirmedTransactionsImpl((#dumpConfirmedTransactionJSON(<transaction> TXN </transaction>) , SERIALIZED) , <transactions> REST </transactions>)
    rule #dumpConfirmedTransactionsImpl(
         (SERIALIZED:JSONs),
         <transactions>
           .Bag
         </transactions>)
      => SERIALIZED

    syntax JSON ::= #dumpConfirmedTransactionJSON(TransactionCell) [function]
    //-----------------------------------------------------------------------
    rule #dumpConfirmedTransactionJSON(
          <transaction>
            <txID> TX_ID:String </txID>
            <applyData>
              <txConfigAsset>   CREATED_ASSET_ID </txConfigAsset>
              <txApplicationID> CREATED_APP_ID   </txApplicationID>
              <log>
                <logData> LOG_DATA  </logData>
                <logSize> _LOG_SIZE </logSize>
              </log>
              ...
            </applyData>
            ...
          </transaction>)
          =>{ "id"     : TX_ID
            , "params" : { "asset-index": maybeTUInt64(CREATED_ASSET_ID, 0)
                       , "application-index": maybeTUInt64(CREATED_APP_ID, 0)
                       , "close-rewards": null
                       , "closing-amount": null
                       , "asset-closing-amount": null
                       , "confirmed-round": 1
                       , "receiver-rewards": null
                       , "sender-rewards": null
                       , "local-state-delta": null
                       , "global-state-delta": null
                       , "logs": BytesList2JSONList(LOG_DATA)
                       , "inner-txns": null
                       , "txn": null
                       }
            }

  syntax JSON ::= BytesList2JSONList(TValueList) [function]

  rule BytesList2JSONList(.TValueList)  => [.JSONs]
  rule BytesList2JSONList(B:Bytes)      => [Base64Encode(B)]
  rule BytesList2JSONList(B:Bytes REST) => [Base64Encode(B), BytesList2JSONList(REST)]
```

```k
endmodule
```
