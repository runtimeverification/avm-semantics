```k
requires "avm/blockchain.md"
requires "avm/constants.md"
requires "avm/txn.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-driver.md"
requires "avm/avm-configuration.md"
requires "avm/avm-initialization.md"
requires "avm/avm-txn-deque.md"

module AVM-EXECUTION-SYNTAX
  imports INT
  imports LIST
  imports BYTES
  imports AVM-CONSTANTS
  imports ALGO-BLOCKCHAIN
  imports ALGO-TXN
  imports AVM-CONFIGURATION
  imports AVM-INITIALIZATION
  imports TEAL-SYNTAX
  imports TEAL-DRIVER
```

Top-level model control rules
-----------------------------

The model has a number of top-level rules that will control the configuration initialisation, trigger execution, etc.
A sequence of `AlgorandCommand`s will be supplied as `$PGM` to `krun`.

```k
  syntax AVMSimulation ::= ".AS"
                         | AlgorandCommand ";" AVMSimulation
  // -------------------------------------------------------

  rule <k> .AS                  => .        ... </k>
  rule <k> AC; .AS              => AC       ... </k>
  rule <k> AC; AS:AVMSimulation => AC ~> AS ... </k>
    requires AS =/=K .AS

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
  syntax AlgorandCommand ::= #setMode(TealMode)
  //-------------------------------------------
  rule <k> #setMode(MODE) => . ...</k>
       <mode> _ => MODE </mode>
  
  syntax AlgorandCommand ::= #evalTxGroup()
  //---------------------------------------

  rule <k> #evalTxGroup() => #popTxnFront() ~> #evalTx() ~> #evalTxGroup() ... </k>
       <deque> TXN_DEQUE </deque>
    requires TXN_DEQUE =/=K .List

  // Minimum balances are only checked at the conclusion of the outer-level group.
  rule <k> #evalTxGroup() => #checkSufficientBalance() ... </k>
      <returncode> _ => 0 </returncode>
      <returnstatus> _ => "Success - transaction group accepted"
      </returnstatus>
       <deque> .List </deque>
```

### Executing next transaction

The execution flow of a single transaction is as follows:
* pop transaction from deque
* check signature
* (optional) eval stateless TEAL, if the transaction is signed by a logic signature
* (optional) eval stateful TEAL, if the transaction is an application call
* apply effects if accepted

All transactions will be signed, either by a normal account or by a logic signature.
The signature verification process will either check the signature itself, or evaluate
the attached stateless TEAL if the transaction is logicsig-signed.

```k
  syntax AlgorandCommand ::= #evalTx()
  //----------------------------------
  rule <k> #evalTx() => 
             #checkTxnSignature() 
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
       <touchedAccounts> .Set => SetItem(SENDER_ADDR) ...</touchedAccounts>

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
             <optInAssetID> ASSET_ID </optInAssetID>
             <optInAssetBalance> BALANCE </optInAssetBalance>
             ...
           </optInAsset>) => .Bag
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
```

```k
  syntax AlgorandCommand ::= #checkSufficientBalance()
  //--------------------------------------------------
  rule <k> #checkSufficientBalance() => (#checkSufficientBalance(ADDR) ~> #checkSufficientBalance()) ...</k>
       <touchedAccounts> (SetItem(ADDR) => .Set) ...</touchedAccounts>

  rule <k> #checkSufficientBalance() => . ...</k>
       <touchedAccounts> .Set </touchedAccounts>
  
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

  rule <k> #checkSufficientBalance(ADDR) => #avmPanic(TX_ID, MIN_BALANCE_VIOLATION) ...</k>
       <currentTx> TX_ID </currentTx>
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
We do not consider the special case of contract creation (deployment) here, it will be addressed in the later rules.
TODO: address contact creation.

```k
  syntax AlgorandCommand ::= #evalTeal( TealInputPgm )

  rule <k> #evalTeal( PGM ) => PGM ~> #startExecution() ~> #saveScratch() ... </k>
       <returncode>           _ => 4                           </returncode>   // (re-)initialize the code
       <returnstatus>         _ =>"Failure - program is stuck" </returnstatus> // and status with "in-progress" values
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
  rule <k> #executeTxn(@pay) => .K ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>     TXN_ID   </txID>
         <sender>   SENDER   </sender>
         <receiver> RECEIVER </receiver>
         <amount>   AMOUNT   </amount>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <balance> SENDER_BALANCE => SENDER_BALANCE -Int AMOUNT </balance>
         ...
       </account>
       <account>
         <address> RECEIVER </address>
         <balance> RECEIVER_BALANCE => RECEIVER_BALANCE +Int AMOUNT </balance>
         ...
       </account>
       <touchedAccounts> (.Set => SetItem(RECEIVER)) ...</touchedAccounts>

  rule <k> #executeTxn(@pay) => panic(INSUFFICIENT_FUNDS) ... </k>
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

  rule <k> #executeTxn(@pay) => #avmPanic(TXN_ID, UNKNOWN_ADDRESS) ... </k>
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
  rule <k> #executeTxn(@keyreg) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>
```

* **Asset Configuration**

Create asset

```k
  rule <k> #executeTxn(@acfg) => . ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>                TXN_ID         </txID>
         <sender>              SENDER         </sender>
         <configAsset>         NoTValue       </configAsset>
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
           <asset>
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
           ASSETS
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
    requires isTValue(MANAGER_ADDR) 
      orBool isTValue(RESERVE_ADDR) 
      orBool isTValue(FREEZE_ADDR) 
      orBool isTValue(CLAWB_ADDR)
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
         <configManagerAddr>   NoTValue        </configManagerAddr>
         <configReserveAddr>   NoTValue        </configReserveAddr>
         <configFreezeAddr>    NoTValue        </configFreezeAddr>
         <configClawbackAddr>  NoTValue        </configClawbackAddr>
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
```

Modify/delete asset no permission case

TODO split into other cases?
  - user or asset doesn't exist
  - sender not manager of the asset
  - Original creator doesn't have all the funds when trying to delete
  - Maybe more?

```k
  rule <k> #executeTxn(@acfg) => #avmPanic(TXN_ID, ASSET_NO_PERMISSION) ...</k>
       <currentTx> TXN_ID </currentTx> [owise]
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
         <assetCloseTo>  NoTValue </assetCloseTo>
         ...
       </transaction>
    requires hasOptedInAsset(ASSET_ID, SENDER)
```

Asset transfer with a non-zero amount fails if:
- either the sender or the receiver have not opted in;
- sender's holdings are frozen

```k
  rule <k> #executeTxn(@axfer) => #avmPanic(TXN_ID, ASSET_NOT_OPT_IN) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetCloseTo>  NoTValue </assetCloseTo>
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
    requires SENDER =/=K RECEIVER
      andBool (notBool hasOptedInAsset(ASSET_ID, SENDER)
        orBool notBool hasOptedInAsset(ASSET_ID, RECEIVER))

  rule <k> #executeTxn(@axfer) => #avmPanic(TXN_ID, ASSET_FROZEN_FOR_SENDER) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <optInAsset>
           <optInAssetID>      ASSET_ID       </optInAssetID>
           ...
         </optInAsset>
         ...
       </account>
    requires hasOptedInAsset(ASSET_ID, SENDER)
     andBool (getOptInAssetField(AssetFrozen, SENDER, ASSET_ID) ==K 1)
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
         <assetCloseTo>  NoTValue </assetCloseTo>
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
         <assetCloseTo>  CLOSE_TO:TValue </assetCloseTo>
         ...
       </transaction>
```

* **Asset Freeze**

Not supported.

```k
  rule <k> #executeTxn(@afrz) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>
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
           <address> getAppAddress(APP_ID) </address>
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

  rule <k> #executeAppl(APP_ID) => #initApp(APP_ID) ~> #evalTeal(APPROVAL_PGM) ... </k>
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

  rule <k> #executeAppl(APP_ID) => #initApp(APP_ID) ~> #evalTeal(APPROVAL_PGM) ... </k>
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

  rule <k> #executeAppl(APP_ID) => #initApp(APP_ID) ~> #evalTeal(APPROVAL_PGM) ... </k>
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

// Case 3: needed because of bug?

  rule <k> #executeAppl(APP_ID) => #initApp(APP_ID) ~> #evalTeal(APPROVAL_PGM) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID  </txID>
         <sender>        SENDER  </sender>
         <onCompletion>  @ OptIn </onCompletion>
         ...
       </transaction>
         <accountsMap>
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
       </accountsMap>
     requires notBool hasOptedInApp(APP_ID, SENDER)

```


CloseOut

```k
  rule <k>
         #executeAppl(APP_ID) => 
              #initApp(APP_ID)
           ~> #evalTeal(APPROVAL_PGM) 
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
           ~> #evalTeal(CLEAR_STATE_PGM) 
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
           ~> #evalTeal(APPROVAL_PGM) 
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
           ~> #evalTeal(APPROVAL_PGM) 
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
       <appCreator> (APP_ID |-> _) => .Map ... </appCreator>
```

* **Layer-2 transactions**

Not supported.
TODO: determine if we need to support them an all.

```k
  rule <k> #executeTxn(@ccfg) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>

  rule <k> #executeTxn(@ccall) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>

  rule <k> #executeTxn(@cfx) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>
```

* **Future transaction types**


```k
endmodule
```
