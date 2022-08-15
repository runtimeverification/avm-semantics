```k
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"

module AVM-INITIALIZATION
  imports INT
  imports LIST
  imports STRING
  imports BYTES
  imports ALGO-BLOCKCHAIN
  imports AVM-CONFIGURATION
  imports AVM-TXN-DEQUE
  imports TEAL-CONSTANTS
  imports ALGO-TXN
```


This module contains the rules that will initialize AVM with the Algorand blockchain state
and the supplied transaction group.

AVM Initialization
------------------

Initialize the network state with *concrete* test data.
The ordered in which these rules are applied matters! Details TBD.
TODO: provide a default safe order.

```k
  syntax AlgorandCommand ::= #initTxGroup()
                           | #initGlobals()
```

The transaction is initialized first.

### Transaction Group Initialization
```k
  rule <k> #initTxGroup() => .K ... </k>
       <txGroup>
         <txGroupID> _ => 0 </txGroupID>
         <currentTx> _ => 0 </currentTx>
         <transactions>
           _ => .Bag
          </transactions>
       </txGroup>
```

### Transactions

By convention, we initialise the `<group>` cell, which tracks the transaction's position
withing the group, with it's `<txID>`. Transaction IDs will be assigned sequentially.

**TODO**: transaction IDs and group indices need be assigned differently for real blockchain transactions.

#### Payment Transaction

```k
  syntax AlgorandCommand ::= "submit" TransactionCell
  //-------------------------------------------------
  rule <k> submit <transaction> TXN </transaction> =>
           #pushTxnBack(<txID> getTxID(<transaction> TXN </transaction>) </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction> TXN </transaction>
         TXNS
       </transactions>
//       requires notBool (ID in_txns(<transactions> TXNS </transactions>))
```

```k
  syntax AlgorandCommand ::= "addPaymentTx" TxIDCell SenderCell ReceiverCell AmountCell
  //-----------------------------------------------------------------------------------
  rule <k> addPaymentTx <txID>     ID       </txID>
                        <sender>   SENDER   </sender>
                        <receiver> RECEIVER </receiver>
                        <amount>   AMOUNT   </amount>
       => #pushTxnBack(<txID> ID </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> ID </txID>
           <txHeader>
             <sender>      SENDER </sender>
             <txType>      "pay"  </txType>
             <typeEnum>    @ pay  </typeEnum>
             <group>       ID     </group>    // for testing, we make these the same as sequential TxIDs
             ...                              // other fields will receive default values
           </txHeader>
           <payTxFields>
             <receiver>         RECEIVER </receiver>
             <amount>           AMOUNT </amount>
             <closeRemainderTo> .Bytes </closeRemainderTo>
           </payTxFields>
         </transaction>
         TXNS
       </transactions>
       requires notBool (ID in_txns(<transactions> TXNS </transactions>))
```

#### Application Call Transaction

```k
  syntax AlgorandCommand ::= "addAppCallTx" TxIDCell SenderCell ApplicationIDCell
                                            OnCompletionCell AccountsCell
                                            ApplicationArgsCell
  //-----------------------------------------------------------
  rule <k> addAppCallTx <txID>            ID            </txID>
                        <sender>          SENDER        </sender>
                        <applicationID>   APP_ID        </applicationID>
                        <onCompletion>    ON_COMPLETION </onCompletion>
                        <accounts>        ACCOUNTS      </accounts>
                        <applicationArgs> ARGS          </applicationArgs>
       => #pushTxnBack(<txID> ID </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> ID </txID>
           <txHeader>
             <sender>      SENDER </sender>
             <txType>      "appl" </txType>
             <typeEnum>    @ appl </typeEnum>
             <group>       ID     </group> // for testing, we make these the same as sequential TxIDs
             ...                           // other fields will receive default values
           </txHeader>
          <appCallTxFields>
            <applicationID>   APP_ID        </applicationID>
            <onCompletion>    ON_COMPLETION </onCompletion>
            <accounts>        ACCOUNTS      </accounts>
            <applicationArgs> ARGS          </applicationArgs>
            ...                            // other fields will receive default values
          </appCallTxFields>
         </transaction>
         TXNS
       </transactions>
       requires notBool (ID in_txns(<transactions> TXNS </transactions>))


```

### Globals Initialization

To now the group size, we need to count the transactions in the group:

```k
  syntax Int ::= countTxns(TransactionsCell) [function, functional]
  // ---------------------------------------------------------------

  rule countTxns(<transactions> <transaction> _ </transaction> REST </transactions>)
       => 1 +Int countTxns(<transactions> REST </transactions>)
  rule countTxns(<transactions> .Bag </transactions>)
       => 0
```

The semantics does not currently care about block production, therefore the `<globalRound> `
and ` <latestTimestamp>` are initialized with somewhat arbitrary values.

```k
  rule <k> #initGlobals() => .K ... </k>
       <globals>
         <groupSize>            _ => countTxns(<transactions> TXNS </transactions>) </groupSize>
         <globalRound>          _ => 6 </globalRound>
         <latestTimestamp>      _ => 50  </latestTimestamp>
         <currentApplicationID> _ => 0 </currentApplicationID>
         <currentApplicationAddress> _ => .Bytes </currentApplicationAddress>
       </globals>
       <txGroup>
         <transactions> TXNS </transactions>
          ...
       </txGroup>
```

### Blockchain Initialization

The Algorand network state comprises accounts, apps (smart contracts) and assets.
In the configuration, we store the apps' and assets' data in the account of their creator;
hence we initialize the accounts first, leaving their created and opted-in apps and assets empty,
and then initialize them with separate rules.

#### Accounts Initialization

We do not currently model rewards, hence we initilize the network participation-related cells with arbitrary values.

```k
  syntax AlgorandCommand ::= "addAccount" AddressCell BalanceCell
  //--------------------------------------------------------

  rule <k> addAccount <address> ADDR </address>
                      <balance> BALANCE </balance>
       => .K ... </k>
       <accountsMap>
         ACCOUNTS =>
         <account>
           <address> ADDR </address>
           <balance> BALANCE    </balance>
           <key> ADDR </key>
           <appsCreated> .Bag </appsCreated>
           <appsOptedIn> .Bag </appsOptedIn>
           <assetsCreated> .Bag </assetsCreated>
           <assetsOptedIn> .Bag </assetsOptedIn>
           ...
         </account>
         ACCOUNTS
       </accountsMap>
      requires notBool (ADDR in_accounts(<accountsMap> ACCOUNTS </accountsMap>))
```

#### Apps Initialization

The app initialization rules must be used *after* initializing accounts.
TODO: initialize an account for the app to receive/send funds.
      the address should be derived from AppID as in https://developer.algorand.org/docs/get-details/dapps/smart-contracts/apps/#using-a-smart-contract-as-an-escrow

```python
# app ID of 1’s address
python3 -c "import algosdk.encoding as e; print(e.encode_address(e.checksum(b'appID'+(1).to_bytes(8, 'big'))))"
WCS6TVPJRBSARHLN2326LRU5BYVJZUKI2VJ53CAWKYYHDE455ZGKANWMGM
```

```k
  syntax AlgorandCommand ::= "addApp" AppIDCell AddressCell Int
  //-----------------------------------------------------------

  rule <k> addApp <appID>       APP_ID            </appID>
                  <address>     CREATOR           </address>
                  PGM_IDX
       => .K ... </k>
       <tealPrograms> TEAL_PGMS_LIST </tealPrograms>
       <accountsMap>
         <account>
           <address>     CREATOR </address>
           <appsCreated>
             APPS =>
             <app>
               <appID>           APP_ID </appID>
               <approvalPgm>     getTealByIndex(TEAL_PGMS_LIST, PGM_IDX) </approvalPgm>
               ...
             </app>
             APPS
           </appsCreated>
           ...
         </account>
         ACCOUNTS
       </accountsMap>
       <appCreator> M => M[APP_ID <- CREATOR] </appCreator>
      requires notBool (APP_ID in_apps(<accountsMap> ACCOUNTS </accountsMap>))
       andBool notBool (APP_ID in_apps(<appsCreated> APPS     </appsCreated>))
```

Accounts can opt into apps to allocate local state for them:

```k
  syntax AlgorandCommand ::= "optinApp" AppIDCell AddressCell
  //---------------------------------------------------------
  rule <k> optinApp <appID>       APP_ID  </appID>
                    <address>     USER    </address>
       => .K ... </k>
       <accountsMap>
         <account>
           <address>     USER </address>
           <appsOptedIn>
             OPTED_IN_APPS =>
             <optInApp>
               <optInAppID> APP_ID </optInAppID>
               <localStorage> .Map </localStorage>
             </optInApp>
             OPTED_IN_APPS
           </appsOptedIn>
           ...
         </account>
         ...
       </accountsMap>
      requires appCreated(APP_ID)
       andBool notBool hasOptedInApp(APP_ID, USER)
```

#### Assets Initialization

The asset initialization rule must be used *after* initializing accounts.

### Teal Programs Declaration

```k
  syntax AlgorandCommand ::= "declareTealSource" String
  //------------------------------------------------
  rule <k> declareTealSource _ => .K ... </k>
```

```k
endmodule
```
