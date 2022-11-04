```k
requires "json.md"
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-types.md"
requires "avm/avm-txn-deque.md"
```

```k
module ALGOD-MODELS
    imports JSON
    imports ALGO-BLOCKCHAIN
    imports AVM-CONFIGURATION
    imports AVM-TXN-DEQUE
```


This module defines the transalition of [`algod OpenAPI`](https://raw.githubusercontent.com/algorand/go-algorand/master/daemon/algod/api/algod.oas2.json) specification into KAVM configuration sorts.

```k
    syntax KItem ::= #panic(String)
```

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
    rule <k> #addAccountJSON({"address": ADDR:String,
                              "amount": BALANCE:Int,
                              "amount-without-pending-rewards": null,
                              "apps-local-state": null,
                              "apps-total-schema": null,
                              "assets": null,
                              "created-apps": APPS,
                              "created-assets": null,
                              "participation": null,
                              "pending-rewards": null,
                              "reward-base": null,
                              "rewards": null,
                              "round": null,
                              "status": null,
                              "sig-type": null,
                              "auth-addr": null
                             })
         => #setupApplications(APPS) ... </k>
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
    rule <k> #addAccountJSON(INPUT:JSON) => #panic("Invalid account JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Applications

```k
    syntax KItem ::= #setupApplications(JSON)
    //---------------------------------------

    rule <k> #setupApplications([APP_JSON, REST]) => #addApplicationJSON(APP_JSON) ~> #setupApplications([REST]) ... </k>
    rule <k> #setupApplications([.JSONs])         => .K ... </k>
    rule <k> #setupApplications(null)             => .K ... </k>

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
                        <approvalPgmSrc>   getTealByName(TEAL_PROGRAMS, APPROVAL_NAME):TealInputPgm    </approvalPgmSrc>
                        <clearStatePgmSrc> getTealByName(TEAL_PROGRAMS, CLEAR_STATE_NAME):TealInputPgm </clearStatePgmSrc>
                          ...
                       </app>)
             ...
             </appsCreated>
             ...
           </account>
           <tealPrograms> TEAL_PROGRAMS </tealPrograms>
       requires DecodeAddressString(CREATOR_ADDR_STR) ==K CREATOR_ADDR
    rule <k> #addApplicationJSON(INPUT:JSON) => #panic("Invalid app JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Assets

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
    rule <k> #setupTransactions([TXN_JSON, REST]) => #addPaymentTxnJSON(TXN_JSON) ~> #setupTransactions([REST]) ... </k>
    rule <k> #setupTransactions([.JSONs]) => .K ... </k>
```

### Payment

```k
    syntax KItem ::= #addPaymentTxnJSON(JSON)
    //----------------------------------------
    rule <k> #addPaymentTxnJSON({ "amt": AMOUNT:Int,
                                  "fee": _FEE:Int,
                                  "gh": _,
                                  "grp": GROUP_ID:String,
                                  "lv": 1,
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
             <closeRemainderTo> .Bytes </closeRemainderTo>
           </payTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <nextTxnID> ID => ID +Int 1 </nextTxnID>
```

```k
endmodule
```
