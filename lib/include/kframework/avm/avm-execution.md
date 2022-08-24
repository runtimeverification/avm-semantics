```k
requires "avm/blockchain.md"
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
  imports ALGO-BLOCKCHAIN
  imports ALGO-TXN
  imports AVM-CONFIGURATION
  imports AVM-INITIALIZATION
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
```

Transaction Group Evaluation
----------------------------

### Transaction execution pipeline

The `#evalTxGroup()` rule calls the `#evalTx()` rule until the transaction deque is empty.
The transactions can push new (inner) transactions into the front of `txnDeque` and they
will be executed immediately after their parent transaction, provided it has been accepted.

If one of the transactions is denied (including the inner ones), the group evaluation stops
and the current configuration is frozen for examination.

```k
  syntax AlgorandCommand ::= #evalTxGroup()
  //---------------------------------------

  rule <k> #evalTxGroup() => #popTxnFront() ~> #evalTx() ~> #evalTxGroup() ... </k>
       <deque> TXN_DEQUE </deque>
    requires TXN_DEQUE =/=K .List

  rule <k> #evalTxGroup() => .K ... </k>
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
  rule <k> #evalTx() => #checkTxnSignature() ~> #executeTxn(TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <typeEnum> TXN_TYPE </typeEnum>
         ...
       </transaction>

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
  syntax AlgorandCommand ::= #evalTeal()

  rule <k> #evalTeal() => #cleanUp() ~> APPROVAL_PGM ~> #startExecution() ... </k>
       <returncode>           _ => 4                           </returncode>   // (re-)initialize the code
       <returnstatus>         _ =>"Failure - program is stuck" </returnstatus> // and status with "in-progress" values
       <currentTx>           TXN_ID                            </currentTx>
       <currentApplicationID> _ => APP_ID                    </currentApplicationID>
       <app>
         <appID>       APP_ID       </appID>
         <approvalPgm> APPROVAL_PGM </approvalPgm>
         ...
       </app>
   requires APP_ID ==K getTxnField(TXN_ID, ApplicationID)
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
         <minBalance> SENDER_MIN_BALANCE </minBalance>
         ...
       </account>
       <account>
         <address> RECEIVER </address>
         <balance> RECEIVER_BALANCE => RECEIVER_BALANCE +Int AMOUNT </balance>
         ...
       </account>
    requires SENDER_BALANCE -Int AMOUNT >=Int SENDER_MIN_BALANCE

  rule <k> #executeTxn(@pay) => #avmPanic(TXN_ID, MIN_BALANCE_VIOLATION) ... </k>
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
         <minBalance> SENDER_MIN_BALANCE </minBalance>
         ...
       </account>
    requires SENDER_BALANCE -Int AMOUNT <Int SENDER_MIN_BALANCE

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
         ...
       </transaction>

       <nextAssetId> ASSET_ID => ASSET_ID +Int 1 </nextAssetId>
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
         ...
       </account>
       <assetCreator> .Map => (ASSET_ID |-> SENDER) ...</assetCreator>
    requires notBool (assetCreated(ASSET_ID))
     andBool notBool (hasOptedInAsset(ASSET_ID, SENDER))
```

* **Asset Transfer**

Asset transfer goes through if:
- both sender and receiver opted into the asset
- sender has enough holdings
- sender's holdings are not frozen

```k

  rule <k> #executeTxn(@axfer) => .K ... </k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID>          TXN_ID   </txID>
         <sender>        SENDER   </sender>
         <xferAsset>     ASSET_ID </xferAsset>
         <assetReceiver> RECEIVER </assetReceiver>
         <assetAmount>   AMOUNT   </assetAmount>
         ...
       </transaction>
       <account>
         <address> SENDER </address>
         <optInAsset>
           <optInAssetID>      ASSET_ID       </optInAssetID>
           <optInAssetBalance> SENDER_BALANCE
                            => SENDER_BALANCE -Int AMOUNT
           </optInAssetBalance>
           ...
         </optInAsset>
         ...
       </account>
       <account>
         <address> RECEIVER </address>
         <optInAsset>
           <optInAssetID>      ASSET_ID       </optInAssetID>
           <optInAssetBalance> RECEIVER_BALANCE
                            => RECEIVER_BALANCE +Int AMOUNT
           </optInAssetBalance>
           ...
         </optInAsset>
         ...
       </account>
    requires hasOptedInAsset(ASSET_ID, SENDER)
     andBool SENDER_BALANCE -Int AMOUNT >=Int 0
     andBool (getOptInAssetField(AssetFrozen, SENDER, ASSET_ID) ==K 0)
     andBool hasOptedInAsset(ASSET_ID, RECEIVER)
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
         <assetAmount>   AMOUNT   </assetAmount>
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
         ...
       </account>
    requires assetCreated(ASSET_ID)
     andBool notBool hasOptedInAsset(ASSET_ID, SENDER)
     andBool AMOUNT ==Int 0
```

* **Asset Freeze**

Not supported.

```k
  rule <k> #executeTxn(@afrz) => #avmPanic(TXN_ID, UNSUPPORTED_TXN_TYPE) ... </k>
       <currentTx> TXN_ID </currentTx>
```

* **Application Call**
```k
  rule <k> #executeTxn(@appl) => #evalTeal() ... </k>
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
