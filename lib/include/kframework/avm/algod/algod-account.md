```k
requires "json.md"
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-types.md"

module ALGOD-MODELS-SYNTAX
    imports STRING
    imports INT
    imports JSON
    imports AVM-CONFIGURATION
    imports TEAL-TYPES
    imports TEAL-SYNTAX

    syntax NetworkState ::= JSON
    syntax AlgorandCommand ::= NetworkState

    syntax JSON ::= TealInputPgm

endmodule
```

```k
module ALGOD-MODELS
    imports ALGOD-MODELS-SYNTAX
```

```k
    syntax KItem ::= #setup(NetworkState)
    syntax KItem ::= #panic(String)

    rule <k> INPUT:JSON => #setup(INPUT) ... </k>
```


This module defines the transalition of [`algod OpenAPI`](https://raw.githubusercontent.com/algorand/go-algorand/master/daemon/algod/api/algod.oas2.json) specification into KAVM configuration sorts.

## Network State

The Algorand network state is fully determined by the state of the accounts.

```k
    rule <k> #setup({"accounts": ACCTS:JSON}) => #setupAccounts(ACCTS) ...                 </k>
    rule <k> #setup(INPUT:JSON) => #panic("Invalid input:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Accounts

An account is identified by an address and has nested objects the define the applications and ASAs the account has created.

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
                             , "created-apps": APPS
                             }
             ) => #setupApplications(APPS) ... </k>
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
    //-----------------------------------

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
    rule <k> #addAccountJSON(INPUT:JSON) => #panic("Invalid app JSON:" +String JSON2String(INPUT)) ... </k> [owise]
```

### Assets

Test with:
```
kavm run tests/json-scenarios/app-account.json  \
         --teal-sources-dir tests/teal-sources/ \
         --output pretty
```


```k
endmodule
```
