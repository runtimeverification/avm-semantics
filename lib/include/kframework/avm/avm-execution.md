```k
requires "avm/blockchain.md"
requires "avm/constants.md"
requires "avm/txn.md"
requires "avm/itxn.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-driver.md"
requires "avm/avm-configuration.md"
requires "avm/algod/algod-models.md"
requires "avm/avm-txn-deque.md"
requires "avm/avm-initialization.md"

module AVM-EXECUTION-SYNTAX
  imports INT
  imports LIST
  imports BYTES
  imports AVM-CONSTANTS
  imports ALGO-BLOCKCHAIN
  imports ALGO-TXN
  imports ALGO-ITXN
  imports TEAL-SYNTAX
  imports TEAL-DRIVER
  imports AVM-INITIALIZATION
```

Top-level model control rules
-----------------------------

The model has a number of top-level rules that will control the configuration initialisation, trigger execution, etc.
A sequence of `AlgorandCommand`s will be supplied as `$PGM` to `krun`.

```k
  syntax AlgorandCommand

endmodule
```

```k
module AVM-EXECUTION
  imports AVM-EXECUTION-SYNTAX
  imports AVM-TXN-DEQUE
  imports ALGO-TXN
```

Transaction Group Evaluation
----------------------------

### Transaction execution pipeline

The `#evalTxs()` rule calls the `#evalTx()` rule until the transaction deque is empty.
The transactions can push new (inner) transactions into the front of `txnDeque` and they
will be executed immediately after their parent transaction, provided it has been accepted.

If one of the transactions is denied (including the inner ones), the group evaluation stops
and the current configuration is frozen for examination.

```k
  // #evalTxGroup
  //---------------------------------------
  rule <k> #evalTxGroup() => #initTxnIndexMap() ~> #evalFirstTx() ...</k>

  syntax AlgorandCommand ::= #evalFirstTx()
                           | #evalNextTx()

  rule <k> #evalFirstTx() => #getNextTxn() ~> #startTx() ~> #evalTx() ~> #popTxnFront() ~> #endTx() ~> #evalNextTx() ... </k>
       <deque> TXN_DEQUE </deque>
    requires TXN_DEQUE =/=K .List

  rule <k> #evalNextTx() => #getNextTxn() ~> #startTx() ~> #evalTx() ~> #popTxnFront() ~> #endTx() ~> #evalNextTx() ... </k>
       <deque> TXN_DEQUE </deque>
    requires TXN_DEQUE =/=K .List andBool (getTxnGroupID(getNextTxnID()) ==K getTxnGroupID(getCurrentTxn()))

  // Finish executing inner transaction group and resume next outer layer
  rule <k> #evalNextTx() => #getNextTxn() ~> #startTx() ~> #evalTx() ~> #endTx() ... </k>
       <deque> TXN_DEQUE </deque>
    requires TXN_DEQUE =/=K .List andBool (getTxnGroupID(getNextTxnID()) =/=K getTxnGroupID(getCurrentTxn()))

  // Minimum balances are only checked at the conclusion of the outer-level group.
  rule <k> #evalNextTx() => #checkSufficientBalance() ~> #endTx() ... </k>
       <returncode> _ => 0 </returncode>
       <deque> .List </deque>
```

#### Dummy service rules for `KCFG`

The the `#startTx()` and `#endTx()` rules serve as markers of the start and end of transaction execution.
We'll use them to save the node holding transaction's pre- and post-states in `KCFG`.

```k
  syntax AlgorandCommand ::= #startTx()
                           | #endTx()
  //-----------------------------------
  rule [starttx]: <k> #startTx() => .K ... </k>
  rule [endtx]:   <k> #endTx()   => .K ... </k>
```

### Executing next transaction

The execution flow of a single transaction is as follows:
* pop transaction from deque
* check signature
* (optional, **not implemented**) eval stateless TEAL, if the transaction is signed by a logic signature
* (optional) eval stateful TEAL, if the transaction is an application call
* apply effects if accepted

All transactions will be signed, either by a normal account or by a logic signature.
The signature verification process will either check the signature itself, or evaluate
the attached stateless TEAL if the transaction is logicsig-signed (**not implemented**).

#### Non-`appl` transaction

Rule for transaction that don't execute TEAL (we do not implement logic signatures yet)

```k
  syntax AlgorandCommand ::= #evalTx()
  //----------------------------------
  rule <k> #evalTx()
        => #checkTxnSignature()
        ~> #executeTxn(TXN_TYPE)
        ...
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <typeEnum> TXN_TYPE </typeEnum>
         <sender> SENDER_ADDR </sender>
         ...
       </transaction>
       <touchedAccounts> TA => addToListNoDup(SENDER_ADDR, TA) </touchedAccounts>
   requires TXN_TYPE =/=K @appl
```

#### `appl` transaction

Execute application call

```k
  rule <k> #evalTx()
        => #initContext()
        ~> #checkTxnSignature()
        ~> #executeTxn(TXN_TYPE)
        ...
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <typeEnum> TXN_TYPE </typeEnum>
         <resume> false => true </resume>
         <sender> SENDER_ADDR </sender>
         ...
       </transaction>
       <touchedAccounts> TA => addToListNoDup(SENDER_ADDR, TA) </touchedAccounts>
   requires TXN_TYPE ==K @appl
```

Resume application call after returning from an inner group

```k
  rule  <k> #evalTx()
         => #restoreContext()
         ~> #evalTeal()
         ...
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <typeEnum> TXN_TYPE </typeEnum>
         <resume> true </resume>
         <sender> SENDER_ADDR </sender>
         ...
       </transaction>
       <touchedAccounts> TA => addToListNoDup(SENDER_ADDR, TA) </touchedAccounts>
   requires TXN_TYPE ==K @appl
```

#### Check signature

The first step of transaction evaluation is to check that its signature is valid. There are several options to sign a transaction,
and we would like to address them uniformly. A transactions can by signed by:

* a regular account
* a multi-signature account
* a logic signature contract account

TODO: augment the configuration in `modules/common/txn.md` to support signed transactions.

```k
  syntax AlgorandCommand ::= #checkTxnSignature()
  //---------------------------------------------

  rule <k> #checkTxnSignature() => .K ... </k>
```

For now, we do not check signatures *here*, hence this operation is noop.
We check logic signatures in an ad-hoc way for payments and asset transfers at a later step.

#### Post-evaluation operations

Clear local state

case 1: clear state from own created app

```k
  syntax AlgorandCommand ::= #clearState( TValue, TValue )
  //------------------------------------------------------

  rule <k> #clearState(APP_ID, ADDR) => . ...</k>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           (<optInApp>
             <optInAppID> APP_ID </optInAppID>
             ...
           </optInApp>) => .Bag
           ...
         </appsOptedIn>
         <appsCreated>
           <appID> APP_ID </appID>
           <localNumInts>     LOCAL_INTS      </localNumInts>
           <localNumBytes>    LOCAL_BYTES     </localNumBytes>
           ...
         </appsCreated>
         <minBalance> MIN_BALANCE => MIN_BALANCE 
                                -Int (PARAM_APP_OPTIN_FLAT 
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE) 
                                  *Int LOCAL_INTS)
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE) 
                                  *Int LOCAL_BYTES))
         </minBalance>
         ...
       </account>
```

case 1: clear state from other's created app

```k
  rule <k> #clearState(APP_ID, ADDR) => . ...</k>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           (<optInApp>
             <optInAppID> APP_ID </optInAppID>
             ...
           </optInApp>) => .Bag
           ...
         </appsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE 
                                -Int (PARAM_APP_OPTIN_FLAT 
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE) 
                                  *Int LOCAL_INTS)
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE) 
                                  *Int LOCAL_BYTES))
         </minBalance>
         ...
       </account>
       <appsCreated>
         <appID> APP_ID </appID>
         <localNumInts>     LOCAL_INTS      </localNumInts>
         <localNumBytes>    LOCAL_BYTES     </localNumBytes>
         ...
       </appsCreated>

```

Update application programs

```k
  syntax AlgorandCommand ::= #updatePrograms( TValue, KItem, KItem )
  //----------------------------------------------------------------

  rule <k> #updatePrograms(APP_ID, APPROVAL_PGM, CLEAR_STATE_PGM) => . ...</k>
       <app>
         <appID> APP_ID </appID>
         <approvalPgmSrc> _ => APPROVAL_PGM </approvalPgmSrc>
         <clearStatePgmSrc> _ => CLEAR_STATE_PGM </clearStatePgmSrc>
         ...
       </app>
```

Delete application

```k
  syntax AlgorandCommand ::= #deleteApplication( TValue )
  //------------------------------------------------------

  rule <k> #deleteApplication(APP_ID) => . ...</k>
       <account>
         <appsCreated>
           ((<app>
             <appID> APP_ID </appID>
             <globalNumInts>    GLOBAL_INTS     </globalNumInts>
             <globalNumBytes>   GLOBAL_BYTES    </globalNumBytes>
             <extraPages>    EXTRA_PAGES     </extraPages>
             ...
           </app>) => .Bag) ...
         </appsCreated>
         <minBalance> MIN_BALANCE => MIN_BALANCE 
                                -Int (((1 +Int EXTRA_PAGES) *Int PARAM_APP_PAGE_FLAT) 
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE) 
                                  *Int GLOBAL_INTS)
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE) 
                                  *Int GLOBAL_BYTES))
         </minBalance>
         ...
       </account>
       <appCreator> (APP_ID |-> _) => .Map ... </appCreator>
```

Close asset account to

```k
  syntax AlgorandCommand ::= #closeTo(TValue, TValue, TValue)
  //---------------------------------------------------------
  rule <k> #closeTo(ASSET_ID, FROM, CLOSE_TO) => . ...</k>
       <account>
         <address> FROM </address>
         <assetsOptedIn>
           (<optInAsset>
             <optInAssetID>      ASSET_ID </optInAssetID>
             <optInAssetBalance> BALANCE  </optInAssetBalance>
             <optInAssetFrozen>  _        </optInAssetFrozen>
           </optInAsset> => .Bag)
           ...
         </assetsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE -Int PARAM_MIN_BALANCE </minBalance>
         ...
       </account>
       <account>
         <address> CLOSE_TO </address>
         <optInAsset>
           <optInAssetID> ASSET_ID </optInAssetID>
           <optInAssetBalance> PREV_BALANCE => PREV_BALANCE +Int BALANCE </optInAssetBalance>
           ...
         </optInAsset>
           ...
       </account>
```

Add balance ot account

```k
  syntax AlgorandCommand ::= #giveAlgos(TValue, TValue)
  //-----------------------------------------------------------
  rule <k> #giveAlgos(ACCOUNT, AMOUNT) => . ...</k>
       <account>
         <address> ACCOUNT </address>
         <balance> BALANCE => BALANCE +Int AMOUNT </balance>
         ...
       </account>
       requires (BALANCE +Int AMOUNT) >=Int 0

  rule <k> #giveAlgos(ACCOUNT, AMOUNT) => #panic(INSUFFICIENT_FUNDS) ...</k>
       <account>
         <address> ACCOUNT </address>
         <balance> BALANCE </balance>
         ...
       </account>
       requires (BALANCE +Int AMOUNT) <Int 0
```

Add asset to account

```k
  syntax AlgorandCommand ::= #giveAsset(TValue, TValue, TValue)
  //-----------------------------------------------------------
  rule <k> #giveAsset(ASSET_ID, ACCOUNT, AMOUNT) => . ...</k>
       <account>
         <address> ACCOUNT </address>
         <optInAsset>
           <optInAssetID> ASSET_ID </optInAssetID>
           <optInAssetBalance> BALANCE => BALANCE +Int AMOUNT </optInAssetBalance>
           <optInAssetFrozen> 0 </optInAssetFrozen>
         </optInAsset>
         ...
       </account>
       requires (BALANCE +Int AMOUNT) >=Int 0

  rule <k> #giveAsset(ASSET_ID, ACCOUNT, AMOUNT) => #panic(INSUFFICIENT_ASSET_BALANCE) ...</k>
       <account>
         <address> ACCOUNT </address>
         <optInAsset>
           <optInAssetID> ASSET_ID </optInAssetID>
           <optInAssetBalance> BALANCE </optInAssetBalance>
           <optInAssetFrozen> 0 </optInAssetFrozen>
         </optInAsset>
         ...
       </account>
       requires (BALANCE +Int AMOUNT) <Int 0
```

```k
  syntax AlgorandCommand ::= #checkSufficientBalance()
  //--------------------------------------------------
  rule <k> #checkSufficientBalance() => (#checkSufficientBalance(ADDR) ~> #checkSufficientBalance()) ...</k>
       <touchedAccounts> (ListItem(ADDR) => .List) ...</touchedAccounts>

  rule <k> #checkSufficientBalance() => . ...</k>
       <touchedAccounts> .List </touchedAccounts>
  
  syntax AlgorandCommand ::= #checkSufficientBalance(Bytes)
  //-------------------------------------------------------
  rule <k> #checkSufficientBalance(ADDR) => . ...</k>
       <account>
         <address> ADDR </address>
         <balance> BALANCE </balance>
         <minBalance> MIN_BALANCE </minBalance>
         ...
       </account>
    requires BALANCE >=Int MIN_BALANCE

  rule <k> #checkSufficientBalance(ADDR) => #panic(MIN_BALANCE_VIOLATION) ...</k>
       <account>
         <address> ADDR </address>
         <balance> BALANCE </balance>
         <minBalance> MIN_BALANCE </minBalance>
         ...
       </account>
    requires BALANCE <Int MIN_BALANCE
```

#### (Optional) Eval TEAL

There are two types of TEAL programs:
* *Stateful*: application calls trigger evaluation of the application's approval/clear state program.
* *Stateless*: payment, asset transfer and possibly other transactions can carry a logic signature that
needs to be evaluated to approve/deny the transaction.

##### Stateful

Application call transactions trigger the execution of the contract's approval or clear state program, assuming that the contract exists.

```k
  syntax AlgorandCommand ::= #evalTeal()

  rule <k> #evalTeal() => #startExecution() ... </k>
```

##### Stateless

#### Apply transaction's effects

Alter the network state with the effects of an approved transaction. Note that payments
and asset transfers can still fail at that point.

```k
  syntax AlgorandCommand ::= #executeTxn(TValue) // transaction type, as defined in `teal-constants.md`
  // -------------------------------------------
```

* **Payment**

Overflow on subtraction is impossible because the minimum balance is at least 0.1 Algo.

```k
  rule <k> #executeTxn(@pay) => #giveAlgos(SENDER, 0 -Int AMOUNT) ~> #giveAlgos(RECEIVER, AMOUNT) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>     TXN_ID   </txID>
         <sender>   SENDER   </sender>
         <receiver> RECEIVER </receiver>
         <amount>   AMOUNT   </amount>
         <rekeyTo>  REKEY_TO </rekeyTo>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <key>     KEY => (#if REKEY_TO ==K getGlobalField(ZeroAddress) #then KEY #else REKEY_TO #fi) </key>
         ...
       </account>
       <touchedAccounts> TA => addToListNoDup(RECEIVER, TA) </touchedAccounts>

  syntax List ::= addToListNoDup(Bytes, List) [function, total]
  rule addToListNoDup(X, L) => ListItem(X) L requires notBool(X in L)
  rule addToListNoDup(X, L) => L requires X in L

  rule <k> #executeTxn(@pay) => #panic(INSUFFICIENT_FUNDS) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>     TXN_ID   </txID>
         <sender>   SENDER   </sender>
         <amount>   AMOUNT   </amount>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <balance> SENDER_BALANCE </balance>
         ...
       </account>
    requires SENDER_BALANCE -Int AMOUNT <Int 0

  rule <k> #executeTxn(@pay) => #panic(UNKNOWN_ADDRESS) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>     TXN_ID   </txID>
         <sender>   SENDER   </sender>
         <amount>   _AMOUNT   </amount>
         <receiver> RECEIVER </receiver>
         ...
       </transaction>
       <accountsMap>
         AMAP
       </accountsMap>
    requires notBool ( SENDER in_accounts (<accountsMap> AMAP </accountsMap>) )
      orBool notBool ( RECEIVER in_accounts (<accountsMap> AMAP </accountsMap>) )
```

* **Key Registration**

Not supported.

```k
  rule <k> #executeTxn(@keyreg) => #panic(UNSUPPORTED_TXN_TYPE) ... </k>
```

* **Asset Configuration**

Create asset

```k
  rule <k> #executeTxn(@acfg) => . ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                TXN_ID         </txID>
         <sender>              SENDER         </sender>
         <configAsset>         0              </configAsset>
         <configTotal>         TOTAL          </configTotal>
         <configDecimals>      DECIMALS       </configDecimals>
         <configDefaultFrozen> DEFAULT_FROZEN </configDefaultFrozen>
         <configUnitName>      UNIT_NAME      </configUnitName>
         <configAssetName>     NAME           </configAssetName>
         <configAssetURL>      ASSET_URL      </configAssetURL>
         <configMetaDataHash>  METADATA_HASH  </configMetaDataHash>
         <configManagerAddr>   MANAGER_ADDR   </configManagerAddr>
         <configReserveAddr>   RESERVE_ADDR   </configReserveAddr>
         <configFreezeAddr>    FREEZE_ADDR    </configFreezeAddr>
         <configClawbackAddr>  CLAWB_ADDR     </configClawbackAddr>
         <txConfigAsset>       _ => ASSET_ID  </txConfigAsset>
         ...
       </transaction>

       <nextAssetID> ASSET_ID => ASSET_ID +Int 1 </nextAssetID>
       <account>
         <address> SENDER </address>
         <assetsCreated>
           ASSETS =>
           (<asset>
             <assetID>            ASSET_ID       </assetID>
             <assetName>          NAME           </assetName>
             <assetUnitName>      UNIT_NAME      </assetUnitName>
             <assetTotal>         TOTAL          </assetTotal>
             <assetDecimals>      DECIMALS       </assetDecimals>
             <assetDefaultFrozen> DEFAULT_FROZEN </assetDefaultFrozen>
             <assetURL>           ASSET_URL      </assetURL>
             <assetMetaDataHash>  METADATA_HASH  </assetMetaDataHash>
             <assetManagerAddr>   MANAGER_ADDR   </assetManagerAddr>
             <assetReserveAddr>   RESERVE_ADDR   </assetReserveAddr>
             <assetFreezeAddr>    FREEZE_ADDR    </assetFreezeAddr>
             <assetClawbackAddr>  CLAWB_ADDR     </assetClawbackAddr>
           </asset>
           ASSETS)
         </assetsCreated>
         <assetsOptedIn>
           ASSETS_OPTED_IN =>
           <optInAsset>
             <optInAssetID>      ASSET_ID       </optInAssetID>
             <optInAssetBalance> TOTAL          </optInAssetBalance>
             <optInAssetFrozen>  DEFAULT_FROZEN </optInAssetFrozen>
           </optInAsset>
           ASSETS_OPTED_IN
         </assetsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE +Int PARAM_MIN_BALANCE </minBalance>
         ...
       </account>
       <assetCreator> .Map => (ASSET_ID |-> SENDER) ...</assetCreator>
```

Modify asset

```k
  rule <k> #executeTxn(@acfg) => . ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                TXN_ID          </txID>
         <sender>              SENDER          </sender>
         <configAsset>         ASSET_ID:TValue </configAsset>
         <configManagerAddr>   MANAGER_ADDR    </configManagerAddr>
         <configReserveAddr>   RESERVE_ADDR    </configReserveAddr>
         <configFreezeAddr>    FREEZE_ADDR     </configFreezeAddr>
         <configClawbackAddr>  CLAWB_ADDR      </configClawbackAddr>
         ...
       </transaction>
       <asset>
         <assetID>            ASSET_ID               </assetID>
         <assetManagerAddr>   SENDER => MANAGER_ADDR </assetManagerAddr>
         <assetReserveAddr>   _ => RESERVE_ADDR      </assetReserveAddr>
         <assetFreezeAddr>    _ => FREEZE_ADDR       </assetFreezeAddr>
         <assetClawbackAddr>  _ => CLAWB_ADDR        </assetClawbackAddr>
         ...
       </asset>
    requires MANAGER_ADDR =/=K getGlobalField(ZeroAddress)
      orBool RESERVE_ADDR =/=K getGlobalField(ZeroAddress)
      orBool FREEZE_ADDR  =/=K getGlobalField(ZeroAddress)
      orBool CLAWB_ADDR   =/=K getGlobalField(ZeroAddress)
```

Destroy asset

"A Destroy Transaction is issued to remove an asset from the Algorand ledger. To destroy an existing asset on
Algorand, the original creator must be in possession of all units of the asset and the manager must send and
therefore authorize the transaction."

"This transaction differentiates itself from an Asset Creation transaction in that it contains an asset ID
(caid) pointing to the asset to be destroyed. It differentiates itself from an Asset Reconfiguration
transaction by the lack of any asset parameters.""

```k
  rule <k> #executeTxn(@acfg) => . ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                TXN_ID          </txID>
         <sender>              SENDER          </sender>
         <configAsset>         ASSET_ID:TValue </configAsset>
         <configManagerAddr>   MANAGER_ADDR    </configManagerAddr>
         <configReserveAddr>   RESERVE_ADDR    </configReserveAddr>
         <configFreezeAddr>    FREEZE_ADDR     </configFreezeAddr>
         <configClawbackAddr>  CLAWB_ADDR      </configClawbackAddr>
         ...
       </transaction>
       <account>
         <address> CREATOR </address>
         <assetsCreated>
           (<asset>
             <assetID>            ASSET_ID </assetID>
             <assetManagerAddr>   SENDER   </assetManagerAddr>
             <assetTotal>         BALANCE  </assetTotal>
             ...
           </asset>) => .Bag
           ...
         </assetsCreated>
         <assetsOptedIn>
           (<optInAsset>
             <optInAssetID>      ASSET_ID </optInAssetID>
             <optInAssetBalance> BALANCE  </optInAssetBalance>
             ...
           </optInAsset>) => .Bag
           ...
         </assetsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE -Int PARAM_MIN_BALANCE </minBalance>
         ...
       </account>
       <assetCreator> (ASSET_ID |-> CREATOR) => .Map ...</assetCreator>
    requires MANAGER_ADDR ==K getGlobalField(ZeroAddress)
     andBool RESERVE_ADDR ==K getGlobalField(ZeroAddress)
     andBool FREEZE_ADDR  ==K getGlobalField(ZeroAddress)
     andBool CLAWB_ADDR   ==K getGlobalField(ZeroAddress)
```

Modify/delete asset no permission case

TODO split into other cases?
  - user or asset doesn't exist
  - sender not manager of the asset
  - Original creator doesn't have all the funds when trying to delete
  - Maybe more?

```k
  rule <k> #executeTxn(@acfg) => #panic(ASSET_NO_PERMISSION) ...</k> [owise]
```

* **Asset Transfer**

Asset transfer goes through if:
- both sender and receiver opted into the asset
- sender has enough holdings
- sender's holdings are not frozen

```k

  rule <k> #executeTxn(@axfer) => 
                #giveAsset(ASSET_ID, SENDER, 0 -Int AMOUNT) 
             ~> #giveAsset(ASSET_ID, RECEIVER, AMOUNT) 
           ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetReceiver> RECEIVER </assetReceiver>
         <assetAmount>   AMOUNT   </assetAmount>
         <assetCloseTo>  CLOSE_TO </assetCloseTo>
         ...
       </transaction>
    requires assetCreated(ASSET_ID)
     andBool hasOptedInAsset(ASSET_ID, SENDER)
     andBool hasOptedInAsset(ASSET_ID, RECEIVER)
     andBool CLOSE_TO ==K getGlobalField(ZeroAddress)
     andBool (getOptInAssetField(AssetFrozen, RECEIVER, ASSET_ID) ==K 0)
     andBool (getOptInAssetField(AssetFrozen, SENDER,   ASSET_ID) ==K 0)
```

Asset transfer with a non-zero amount fails if:
- either the sender or the receiver have not opted in;
- sender's holdings are frozen

```k
  rule <k> #executeTxn(@axfer) => #panic(ASSET_NOT_OPT_IN) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetReceiver> RECEIVER </assetReceiver>
         <assetCloseTo>  CLOSE_TO </assetCloseTo>
         <assetAmount>   AMOUNT   </assetAmount>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         ...
       </account>
       <account>
         <address> RECEIVER </address>
         ...
       </account>
    requires assetCreated(ASSET_ID)
     andBool SENDER =/=K RECEIVER
     andBool CLOSE_TO ==K getGlobalField(ZeroAddress)
     andBool AMOUNT >Int 0
     andBool (notBool hasOptedInAsset(ASSET_ID, SENDER)
      orBool notBool hasOptedInAsset(ASSET_ID, RECEIVER))

  rule <k> #executeTxn(@axfer) => #panic(ASSET_NOT_FOUND) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <xferAsset>     ASSET_ID </xferAsset>
         ...
       </transaction>
    requires notBool(assetCreated(ASSET_ID))

  rule <k> #executeTxn(@axfer) => #panic(ASSET_FROZEN) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <assetReceiver> RECEIVER </assetReceiver>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetAmount>   AMOUNT   </assetAmount>
         ...
       </transaction>
    requires assetCreated(ASSET_ID)
     andBool ((AMOUNT >Int 0
     andBool (hasOptedInAsset(ASSET_ID, SENDER)
              andBool hasOptedInAsset(ASSET_ID, RECEIVER)))
     andThenBool
            ((getOptInAssetField(AssetFrozen, SENDER, ASSET_ID) ==K 1)
     orBool  (getOptInAssetField(AssetFrozen, RECEIVER, ASSET_ID) ==K 1)))
```

**Asset opt-in** is a special case of asset transfer: a transfer of zero to self.

Asset opt-in goes through if:
- asset exists
- sender has not yet opted into the asset
- amount is zero


```k
  rule <k> #executeTxn(@axfer) => .K ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetReceiver> SENDER   </assetReceiver>
         <assetAmount>   0        </assetAmount>
         <assetCloseTo>  CLOSE_TO </assetCloseTo>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <assetsOptedIn>
           ASSETS_OPTED_IN =>
           <optInAsset>
             <optInAssetID>      ASSET_ID </optInAssetID>
             <optInAssetBalance> 0 </optInAssetBalance>
             <optInAssetFrozen>
               getAssetParamsField(AssetDefaultFrozen, ASSET_ID)
             </optInAssetFrozen>
           </optInAsset>
           ASSETS_OPTED_IN
         </assetsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE +Int PARAM_MIN_BALANCE </minBalance>
         ...
       </account>
    requires assetCreated(ASSET_ID)
     andBool CLOSE_TO ==K getGlobalField(ZeroAddress)
     andBool notBool hasOptedInAsset(ASSET_ID, SENDER)
```

**Asset opt-out** is a special case of asset transfer: a transfer with the AssetCloseTo field set.

```k
  rule <k> #executeTxn(@axfer) => 
                #giveAsset(ASSET_ID, SENDER, 0 -Int AMOUNT) 
             ~> #giveAsset(ASSET_ID, RECEIVER, AMOUNT) 
             ~> #closeTo(ASSET_ID, SENDER, CLOSE_TO)
           ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID          </txID>
         <sender>        SENDER          </sender>
         <xferAsset>     ASSET_ID        </xferAsset>
         <assetReceiver> RECEIVER        </assetReceiver>
         <assetAmount>   AMOUNT          </assetAmount>
         <assetCloseTo>  CLOSE_TO        </assetCloseTo>
         ...
       </transaction>
    requires assetCreated(ASSET_ID)
     andBool CLOSE_TO =/=K getGlobalField(ZeroAddress)
```

* **Asset Freeze**

Not supported.

```k
  rule <k> #executeTxn(@afrz) => . ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                 TXN_ID              </txID>
         <sender>               SENDER              </sender>
         <freezeAccount>        FREEZE_ACCOUNT      </freezeAccount>
         <freezeAsset>          ASSET_ID            </freezeAsset>
         <assetFrozen>          FREEZE              </assetFrozen>
         ...
       </transaction>
       <account>
         <address> FREEZE_ACCOUNT </address>
         <optInAsset>
           <optInAssetID>      ASSET_ID       </optInAssetID>
           <optInAssetFrozen>  _ => FREEZE    </optInAssetFrozen>
           ...
         </optInAsset>
         ...
       </account>
    requires getAssetParamsField(AssetFreeze, ASSET_ID) ==K SENDER
```

* **Application Call**

App create

```k
  rule <k> #executeTxn(@appl) => #executeAppl(APP_ID) ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                 TXN_ID              </txID>
         <sender>               SENDER              </sender>
         <applicationID>        0                   </applicationID>
         <approvalProgramSrc>   APPROVAL_PGM_SRC    </approvalProgramSrc>
         <clearStateProgramSrc> CLEAR_STATE_PGM_SRC </clearStateProgramSrc>
         <approvalProgram>      APPROVAL_PGM        </approvalProgram>
         <clearStateProgram>    CLEAR_STATE_PGM     </clearStateProgram>
         <globalNui>            GLOBAL_INTS         </globalNui>
         <globalNbs>            GLOBAL_BYTES        </globalNbs>
         <localNui>             LOCAL_INTS          </localNui>
         <localNbs>             LOCAL_BYTES         </localNbs>
         <extraProgramPages>    EXTRA_PAGES         </extraProgramPages>
         <txApplicationID>      _ => APP_ID         </txApplicationID>
         ...
       </transaction>
       <accountsMap>
         <account>
           <address> SENDER </address>
           <minBalance> MIN_BALANCE => MIN_BALANCE 
                                  +Int ((1 +Int EXTRA_PAGES) *Int PARAM_APP_PAGE_FLAT) 
                                  +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE) 
                                    *Int GLOBAL_INTS)
                                  +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE)
                                    *Int GLOBAL_BYTES)
           </minBalance>
           <appsCreated>
             APPS =>
             <app>
               <appID>            APP_ID              </appID>
               <approvalPgmSrc>   APPROVAL_PGM_SRC    </approvalPgmSrc>
               <clearStatePgmSrc> CLEAR_STATE_PGM_SRC </clearStatePgmSrc>
               <approvalPgm>      APPROVAL_PGM        </approvalPgm>
               <clearStatePgm>    CLEAR_STATE_PGM     </clearStatePgm>
               <globalNumInts>       GLOBAL_INTS         </globalNumInts>
               <globalNumBytes>      GLOBAL_BYTES        </globalNumBytes>
               <localNumInts>        LOCAL_INTS          </localNumInts>
               <localNumBytes>       LOCAL_BYTES         </localNumBytes>
               <extraPages>       EXTRA_PAGES         </extraPages>
               ...
             </app>
             APPS
           </appsCreated>
           ...
         </account>
         (.Bag =>
         (<account>
           <address> getAppAddressBytes(APP_ID) </address>
           ...
         </account>))
         ...
       </accountsMap>
       <appCreator> (.Map => (APP_ID |-> SENDER)) ... </appCreator>
       <nextAppID> APP_ID => APP_ID +Int 1 </nextAppID>
    requires notBool(APP_ID in_apps(<appsCreated> APPS </appsCreated>))
     andBool GLOBAL_INTS +Int GLOBAL_BYTES <=Int PARAM_MAX_GLOBAL_KEYS
     andBool LOCAL_INTS  +Int LOCAL_BYTES  <=Int PARAM_MAX_LOCAL_KEYS

  rule <k> #executeTxn(@appl) => #executeAppl(APP_ID) ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                 TXN_ID              </txID>
         <applicationID>        APP_ID:TValue       </applicationID>
         ...
       </transaction>
  requires APP_ID =/=K 0
```

NoOp

```k
  syntax AlgorandCommand ::= #executeAppl(TValue)

  rule <k> #executeAppl(APP_ID) => 
               #initApp(APP_ID) 
            ~> #loadInputPgm(APPROVAL_PGM) 
            ~> #evalTeal() 
            ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID        </txID>
         <onCompletion>  @ NoOp        </onCompletion>
         ...
       </transaction>
       <app>
         <appID>          APP_ID       </appID>
         <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
         ...
       </app>
```

OptIn

```k

// Case 1: user different from app creator is opting in

  rule <k> #executeAppl(APP_ID) => 
               #initApp(APP_ID) 
            ~> #loadInputPgm(APPROVAL_PGM)
            ~> #evalTeal()
            ...
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID  </txID>
         <sender>        SENDER  </sender>
         <onCompletion>  @ OptIn </onCompletion>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <appsOptedIn>
           OPTED_IN_APPS =>
           <optInApp>
             <optInAppID>   APP_ID </optInAppID>
             <localInts> .Map   </localInts>
             <localBytes> .Map   </localBytes>
           </optInApp>
           OPTED_IN_APPS
         </appsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE 
                                +Int PARAM_APP_OPTIN_FLAT
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE)
                                      *Int LOCAL_INTS)
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE)
                                      *Int LOCAL_BYTES)
         </minBalance>
         ...
       </account>
       <app>
         <appID>          APP_ID       </appID>
         <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
         <localNumInts>      LOCAL_INTS   </localNumInts>
         <localNumBytes>     LOCAL_BYTES  </localNumBytes>
         ...
       </app>
     requires notBool hasOptedInApp(APP_ID, SENDER)

// Case 2: app creator is opting in to their own app

  rule <k> #executeAppl(APP_ID) => 
               #initApp(APP_ID) 
            ~> #loadInputPgm(APPROVAL_PGM) 
            ~> #evalTeal()
            ...
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID  </txID>
         <sender>        SENDER  </sender>
         <onCompletion>  @ OptIn </onCompletion>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <appsCreated>
           <app>
             <appID>          APP_ID       </appID>
             <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
             <localNumInts>      LOCAL_INTS   </localNumInts>
             <localNumBytes>     LOCAL_BYTES  </localNumBytes>
             ...
           </app>
           ...
         </appsCreated>
         <appsOptedIn>
           OPTED_IN_APPS =>
           <optInApp>
             <optInAppID>   APP_ID </optInAppID>
             <localInts> .Map        </localInts>
             <localBytes> .Map        </localBytes>
           </optInApp>
           OPTED_IN_APPS
         </appsOptedIn>
         <minBalance> MIN_BALANCE => MIN_BALANCE 
                                +Int PARAM_APP_OPTIN_FLAT 
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_UINT_MIN_BALANCE) 
                                  *Int LOCAL_INTS)
                                +Int ((PARAM_MIN_BALANCE_PER_ENTRY +Int PARAM_BYTES_MIN_BALANCE) 
                                  *Int LOCAL_BYTES)
         </minBalance>
         ...
       </account>
     requires notBool hasOptedInApp(APP_ID, SENDER)


```


CloseOut

```k
  rule <k>
         #executeAppl(APP_ID) => 
              #initApp(APP_ID)
           ~> #loadInputPgm(APPROVAL_PGM)
           ~> #evalTeal() 
           ~> #clearState(APP_ID, SENDER)
         ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID        </txID>
         <sender>        SENDER        </sender>
         <onCompletion>  @ CloseOut    </onCompletion>
         ...
       </transaction>
       <app>
         <appID>          APP_ID       </appID>
         <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
         ...
       </app>
```

ClearState

TODO make sure `#clearState` runs even when a panic is generated

```k
  rule <k>
         #executeAppl(APP_ID) => 
              #initApp(APP_ID)
           ~> #loadInputPgm(CLEAR_STATE_PGM)
           ~> #evalTeal() 
           ~> #clearState(APP_ID, SENDER)
         ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID        </txID>
         <sender>        SENDER        </sender>
         <onCompletion> @ ClearState   </onCompletion>
         ...
       </transaction>
       <app>
         <appID>            APP_ID          </appID>
         <clearStatePgmSrc> CLEAR_STATE_PGM </clearStatePgmSrc>
         ...
       </app>
```

UpdateApplication

```k
  rule <k>
         #executeAppl(APP_ID) => 
              #initApp(APP_ID)
           ~> #loadInputPgm(APPROVAL_PGM)
           ~> #evalTeal() 
           ~> #updatePrograms(APP_ID, NEW_APPROVAL_PGM, NEW_CLEAR_STATE_PGM)
         ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                 TXN_ID              </txID>
         <onCompletion>         @ UpdateApplication </onCompletion>
         <approvalProgramSrc>   NEW_APPROVAL_PGM    </approvalProgramSrc>
         <clearStateProgramSrc> NEW_CLEAR_STATE_PGM </clearStateProgramSrc>
         ...
       </transaction>
       <app>
         <appID>          APP_ID       </appID>
         <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
         ...
       </app>
```

DeleteApplication

```k
  rule <k>
         #executeAppl(APP_ID) => 
              #initApp(APP_ID)
           ~> #loadInputPgm(APPROVAL_PGM)
           ~> #evalTeal() 
           ~> #deleteApplication(APP_ID)
         ... 
       </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID              </txID>
         <onCompletion>  @ DeleteApplication </onCompletion>
         ...
       </transaction>
       <app>
         <appID>          APP_ID       </appID>
         <approvalPgmSrc> APPROVAL_PGM </approvalPgmSrc>
         ...
       </app>
```

* **Layer-2 transactions**

Not supported.
TODO: determine if we need to support them an all.

```k
  rule <k> #executeTxn(@ccfg) => #panic(UNSUPPORTED_TXN_TYPE) ... </k>

  rule <k> #executeTxn(@ccall) => #panic(UNSUPPORTED_TXN_TYPE) ... </k>

  rule <k> #executeTxn(@cfx) => #panic(UNSUPPORTED_TXN_TYPE) ... </k>
```

```k
endmodule
```
