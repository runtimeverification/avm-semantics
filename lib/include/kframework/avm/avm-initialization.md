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
           ...
         </transaction>
         TXNS
       </transactions>
       requires notBool (ID in_txns(<transactions> TXNS </transactions>))
```

#### Application Call Transaction

```k
  syntax AlgorandCommand ::= "addAppCallTx" TxIDCell SenderCell ApplicationIDCell
                                            OnCompletionCell AccountsCell
                                            ApplicationArgsCell ForeignAppsCell 
                                            ForeignAssetsCell
                                            GlobalNuiCell GlobalNbsCell
                                            LocalNuiCell LocalNbsCell
                                            ExtraProgramPagesCell
                                            "<approvalPgmIdx>" Int "</approvalPgmIdx>"
                                            "<clearStatePgmIdx>" Int "</clearStatePgmIdx>"
  //-----------------------------------------------------------
  rule <k> addAppCallTx <txID>              ID              </txID>
                        <sender>            SENDER          </sender>
                        <applicationID>     APP_ID          </applicationID>
                        <onCompletion>      ON_COMPLETION   </onCompletion>
                        <accounts>          ACCOUNTS        </accounts>
                        <applicationArgs>   ARGS            </applicationArgs>
                        <foreignApps>       APPS            </foreignApps>
                        <foreignAssets>     ASSETS          </foreignAssets>
                        <globalNui>         GLOBAL_INTS     </globalNui>
                        <globalNbs>         GLOBAL_BYTES    </globalNbs>
                        <localNui>          LOCAL_INTS      </localNui>
                        <localNbs>          LOCAL_BYTES     </localNbs>
                        <extraProgramPages> EXTRA_PAGES     </extraProgramPages>
                        <approvalPgmIdx>    APPROVAL_IDX    </approvalPgmIdx>
                        <clearStatePgmIdx>  CLEAR_STATE_IDX </clearStatePgmIdx>
       => #pushTxnBack(<txID> ID </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> ID </txID>
           <txHeader>
             <sender>   SENDER </sender>
             <txType>   "appl" </txType>
             <typeEnum> @ appl </typeEnum>
             <group>    ID     </group> // for testing, we make these the same as sequential TxIDs
             ...                           // other fields will receive default values
           </txHeader>
           <appCallTxFields>
             <applicationID>        APP_ID               </applicationID>
             <onCompletion>         ON_COMPLETION        </onCompletion>
             <accounts>             ACCOUNTS             </accounts>
             <applicationArgs>      convertToBytes(ARGS) </applicationArgs>
             <foreignApps>          APPS                 </foreignApps>
             <foreignAssets>        ASSETS               </foreignAssets>
             <globalNui>            GLOBAL_INTS          </globalNui>
             <globalNbs>            GLOBAL_BYTES         </globalNbs>
             <localNui>             LOCAL_INTS           </localNui>
             <localNbs>             LOCAL_BYTES          </localNbs>
             <extraProgramPages>    EXTRA_PAGES          </extraProgramPages>
             <approvalProgramSrc>   getTealByIndex(TEAL_PGMS_LIST, APPROVAL_IDX)    </approvalProgramSrc>
             <clearStateProgramSrc> getTealByIndex(TEAL_PGMS_LIST, CLEAR_STATE_IDX) </clearStateProgramSrc>
             ...                            // other fields will receive default values
           </appCallTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       <tealPrograms> TEAL_PGMS_LIST </tealPrograms>
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

#### Assets Initialization

The asset initialization rule must be used *after* initializing accounts.

```k
  syntax AlgorandCommand ::= "addAssetConfigTx" TxIDCell SenderCell ConfigAssetCell ConfigTotalCell
                                                ConfigDecimalsCell ConfigDefaultFrozenCell ConfigUnitNameCell
                                                ConfigAssetNameCell ConfigAssetURLCell ConfigMetaDataHashCell
                                                ConfigManagerAddrCell ConfigReserveAddrCell
                                                ConfigFreezeAddrCell ConfigClawbackAddrCell
  //-----------------------------------------------------------
  rule <k> addAssetConfigTx <txID>                TXN_ID        </txID>
                            <sender>              SENDER        </sender>
                            <configAsset>         ASSET_ID      </configAsset>
                            <configTotal>         TOTAL         </configTotal>
                            <configDecimals>      DECIMALS      </configDecimals>
                            <configDefaultFrozen> FROZEN        </configDefaultFrozen>
                            <configUnitName>      UNIT_NAME     </configUnitName>
                            <configAssetName>     NAME          </configAssetName>
                            <configAssetURL>      ASSET_URL     </configAssetURL>
                            <configMetaDataHash>  METADATA_HASH </configMetaDataHash>
                            <configManagerAddr>   MGR_ADDR      </configManagerAddr>
                            <configReserveAddr>   RES_ADDR      </configReserveAddr>
                            <configFreezeAddr>    FRZ_ADDR      </configFreezeAddr>
                            <configClawbackAddr>  CLB_ADDR      </configClawbackAddr>
       => #pushTxnBack(<txID> TXN_ID </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> TXN_ID </txID>
           <txHeader>
             <sender>      SENDER </sender>
             <txType>      "acfg" </txType>
             <typeEnum>    @ acfg </typeEnum>
             <group>       TXN_ID </group> // for testing, we make these the same as sequential TxIDs
             ...                           // other fields will receive default values
           </txHeader>
           <assetConfigTxFields>
             <configAsset> ASSET_ID </configAsset>           // the asset ID
             <assetParams>
               <configTotal>         TOTAL         </configTotal>
               <configDecimals>      DECIMALS      </configDecimals>
               <configDefaultFrozen> FROZEN        </configDefaultFrozen>
               <configUnitName>      UNIT_NAME     </configUnitName>
               <configAssetName>     NAME          </configAssetName>
               <configAssetURL>      ASSET_URL     </configAssetURL>
               <configManagerAddr>   MGR_ADDR      </configManagerAddr>
               <configMetaDataHash>  METADATA_HASH </configMetaDataHash>
               <configReserveAddr>   RES_ADDR      </configReserveAddr>
               <configFreezeAddr>    FRZ_ADDR      </configFreezeAddr>
               <configClawbackAddr>  CLB_ADDR      </configClawbackAddr>
             </assetParams>
           </assetConfigTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       requires notBool (TXN_ID in_txns(<transactions> TXNS </transactions>))
```

### Asset transfer

```k
  syntax AlgorandCommand ::= "addAssetTransferTx" TxIDCell SenderCell XferAssetCell AssetAmountCell
                                                  AssetASenderCell AssetReceiverCell AssetCloseToCell
  //-----------------------------------------------------------------------------------------------

  rule <k> addAssetTransferTx <txID>          TXN_ID        </txID>
                              <sender>        SENDER        </sender>
                              <xferAsset>     ASSET_ID      </xferAsset>
                              <assetAmount>   AMOUNT        </assetAmount>
                              <assetASender>  CLAWBACK_FROM </assetASender>
                              <assetReceiver> RECEIVER      </assetReceiver>
                              <assetCloseTo>  CLOSE_TO      </assetCloseTo>
           => #pushTxnBack(<txID> TXN_ID </txID>)
           ...
       </k>
       <transactions>
         TXNS =>
         <transaction>
           <txID> TXN_ID </txID>
           <txHeader>
             <sender>   SENDER  </sender>
             <txType>   "axfer" </txType>
             <typeEnum> @ axfer </typeEnum>
             <group>    TXN_ID  </group> // for testing, we make these the same as sequential TxIDs
             ...                         // other fields will receive default values
           </txHeader>
           <assetTransferTxFields>
             <xferAsset>     ASSET_ID      </xferAsset>
             <assetAmount>   AMOUNT        </assetAmount>
             <assetASender>  CLAWBACK_FROM </assetASender>
             <assetReceiver> RECEIVER      </assetReceiver>
             <assetCloseTo>  CLOSE_TO      </assetCloseTo>
             ...
           </assetTransferTxFields>
           ...
         </transaction>
         TXNS
       </transactions>
       requires notBool (TXN_ID in_txns(<transactions> TXNS </transactions>))

```

### Teal Programs Declaration

```k
  syntax AlgorandCommand ::= "declareTealSource" String
  //------------------------------------------------
  rule <k> declareTealSource _ => .K ... </k>
```

```k
endmodule
```
