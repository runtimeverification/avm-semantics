```k
requires "avm/txn.md"
requires "avm/avm-configuration.md"
requires "avm/avm-txn-deque.md"
requires "avm/avm-execution.md"
requires "avm/avm-initialization.md"
requires "avm/teal/teal-types.md"
requires "avm/teal/teal-fields.md"
requires "avm/teal/teal-execution.md"

module ALGO-ITXN
  imports ALGO-TXN
  imports AVM-CONFIGURATION
  imports AVM-INITIALIZATION
  imports AVM-TXN-DEQUE
  imports TEAL-TYPES
  imports TEAL-FIELDS
  imports TEAL-EXECUTION
  imports MAP

  syntax KItem ::= #setItxnField(TxnFieldTop, TValue)

  rule <k> #setItxnField(Sender, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <sender> _ => VAL </sender> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Fee, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <fee> _ => VAL </fee> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Note, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <note> _ => VAL </note> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(RekeyTo, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <rekeyTo> _ => VAL </rekeyTo> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(TxType, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> 
                   <txType> _ => VAL </txType> 
                   <typeEnum> _=> typeString2Enum(VAL) </typeEnum>
                    ...
                  </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(TypeEnum, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> 
                   <txType> _ => typeEnum2String(VAL) </txType> 
                   <typeEnum> _ => VAL </typeEnum>
                   ...
                  </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(_:TxnPayField, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .PayTxFieldsCell =>
           <payTxFields>
             <receiver>         .Bytes </receiver>
             <amount>           0      </amount>
             <closeRemainderTo> .Bytes </closeRemainderTo>
           </payTxFields>
           ...
         </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Receiver, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <receiver> _ => VAL </receiver> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Amount, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <amount> _ => VAL </amount> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(CloseRemainderTo, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <closeRemainderTo> _ => VAL </closeRemainderTo> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(_:TxnKeyregField, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .KeyRegTxFieldsCell =>
           <keyRegTxFields>
             <votePk>           .Bytes </votePk>
             <selectionPK>      .Bytes </selectionPK>
             <voteFirst>        0      </voteFirst>
             <voteLast>         0      </voteLast>
             <voteKeyDilution>  0      </voteKeyDilution>
             <nonparticipation> 0      </nonparticipation>
           </keyRegTxFields>
           ...
         </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(VotePK, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <votePk> _ => VAL </votePk> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(SelectionPK, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <selectionPK> _ => VAL </selectionPK> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(VoteFirst, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <voteFirst> _ => VAL </voteFirst> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(VoteLast, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <voteLast> _ => VAL </voteLast> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(VoteKeyDilution, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <voteKeyDilution> _ => VAL </voteKeyDilution> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Nonparticipation, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <nonparticipation> _ => VAL </nonparticipation> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAcfgField, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .AssetConfigTxFieldsCell =>
           <assetConfigTxFields>
             <configAsset> 0 </configAsset>
             <assetParams>
               <configTotal>         0                           </configTotal>
               <configDecimals>      0                           </configDecimals>
               <configDefaultFrozen> 0                           </configDefaultFrozen>
               <configUnitName>      .Bytes                      </configUnitName>
               <configAssetName>     .Bytes                      </configAssetName>
               <configAssetURL>      .Bytes                      </configAssetURL>
               <configMetaDataHash>  .Bytes                      </configMetaDataHash>
               <configManagerAddr>   getGlobalField(ZeroAddress) </configManagerAddr>
               <configReserveAddr>   getGlobalField(ZeroAddress) </configReserveAddr>
               <configFreezeAddr>    getGlobalField(ZeroAddress) </configFreezeAddr>
               <configClawbackAddr>  getGlobalField(ZeroAddress) </configClawbackAddr>
             </assetParams>
           </assetConfigTxFields>
           ...
         </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAsset, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configAsset> _ => VAL </configAsset> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetTotal, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configTotal> _ => VAL </configTotal> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetDecimals, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configDecimals> _ => VAL </configDecimals> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetDefaultFrozen, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configDefaultFrozen> _ => VAL </configDefaultFrozen> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetUnitName, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configUnitName> _ => VAL </configUnitName> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetName, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configAssetName> _ => VAL </configAssetName> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetURL, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configAssetURL> _ => VAL </configAssetURL> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetMetaDataHash, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configMetaDataHash> _ => VAL </configMetaDataHash> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetManager, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configManagerAddr> _ => VAL </configManagerAddr> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetReserve, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configReserveAddr> _ => VAL </configReserveAddr> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetFreeze, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configFreezeAddr> _ => VAL </configFreezeAddr> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetClawback, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <configClawbackAddr> _ => VAL </configClawbackAddr> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAxferField, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .AssetTransferTxFieldsCell =>
           <assetTransferTxFields>
             <xferAsset>     0                           </xferAsset>
             <assetAmount>   0                           </assetAmount>
             <assetReceiver> getGlobalField(ZeroAddress) </assetReceiver>
             <assetASender>  getGlobalField(ZeroAddress) </assetASender>
             <assetCloseTo>  getGlobalField(ZeroAddress) </assetCloseTo>
           </assetTransferTxFields>
           ...
         </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(XferAsset, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <xferAsset> _ => VAL </xferAsset> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(AssetAmount, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <assetAmount> _ => VAL </assetAmount> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(AssetASender, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <assetASender> _ => VAL </assetASender> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(AssetReceiver, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <assetReceiver> _ => VAL </assetReceiver> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(AssetCloseTo, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <assetCloseTo> _ => VAL </assetCloseTo> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAfrzField, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .AssetFreezeTxFieldsCell =>
           <assetFreezeTxFields>
             <freezeAccount> getGlobalField(ZeroAddress) </freezeAccount>
             <freezeAsset>   0                           </freezeAsset>
             <assetFrozen>   0                           </assetFrozen>
           </assetFreezeTxFields>
           ...
         </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(FreezeAsset, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <freezeAsset> _ => VAL </freezeAsset> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(FreezeAssetAccount, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <freezeAccount> _ => VAL </freezeAccount> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(FreezeAssetFrozen, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <assetFrozen> _ => VAL </assetFrozen> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(FIELD, _) ... </k>
       <innerTransactions>
         ...
         ListItem(
         <transaction>
           .AppCallTxFieldsCell =>
           <appCallTxFields>
             <applicationID>        0                    </applicationID>
             <onCompletion>         0                    </onCompletion>
             <accounts>             .TValueList          </accounts>
             <approvalProgramSrc>   (int 0):TealInputPgm </approvalProgramSrc>
             <clearStateProgramSrc> (int 0):TealInputPgm </clearStateProgramSrc>
             <approvalProgram>      .Bytes               </approvalProgram>
             <clearStateProgram>    .Bytes               </clearStateProgram>
             <applicationArgs>      .TValueList          </applicationArgs>
             <foreignApps>          .TValueList          </foreignApps>
             <foreignAssets>        .TValueList          </foreignAssets>
             <globalStateSchema>
               <globalNui> 0 </globalNui>
               <globalNbs> 0 </globalNbs>
             </globalStateSchema>
             <localStateSchema>
               <localNui> 0 </localNui>
               <localNbs> 0 </localNbs>
             </localStateSchema>
             <extraProgramPages>    0                    </extraProgramPages>
           </appCallTxFields>
           ...
         </transaction>)
       </innerTransactions>
    requires isTxnApplField(FIELD) orBool isTxnaField(FIELD)

  rule <k> #setItxnField(ApplicationID, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <applicationID> _ => VAL </applicationID> ... </transaction>)
       </innerTransactions>
       
  rule <k> #setItxnField(OnCompletion, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <onCompletion> _ => VAL </onCompletion> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ApprovalProgram, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <approvalProgram> _ => VAL </approvalProgram> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ClearStateProgram, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <clearStateProgram> _ => VAL </clearStateProgram> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(ApplicationArgs, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <applicationArgs> APP_ARGS => append(VAL, APP_ARGS) </applicationArgs> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Accounts, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <accounts> ACCOUNTS => append(VAL, ACCOUNTS) </accounts> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Applications, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <foreignApps> APPS => append(VAL, APPS) </foreignApps> ... </transaction>)
       </innerTransactions>

  rule <k> #setItxnField(Assets, VAL) => . ... </k>
       <innerTransactions>
         ...
         ListItem(<transaction> <foreignAssets> ASSETS => append(VAL, ASSETS) </foreignAssets> ... </transaction>)
       </innerTransactions>
```

```k
  syntax KItem ::= #checkItxn(TransactionCell)

  rule <k> #checkItxn(TXN) => (#checkItxnFieldsCoherent(TXN) ~> #checkForReentrance(TXN)) ...</k>

  syntax KItem ::= #checkForReentrance(TransactionCell)

  rule <k> #checkForReentrance(
             <transaction>
               <txID> TX_ID </txID>
               <txnTypeSpecificFields>
                 <appCallTxFields>
                   <applicationID> APP_ID </applicationID>
                   ...
                 </appCallTxFields>
               </txnTypeSpecificFields>
               ...
             </transaction>) => . 
             ...
       </k>
       <activeApps> AA </activeApps>
    requires notBool(APP_ID in AA )

  rule <k> #checkForReentrance(
             <transaction>
               <txID> TX_ID </txID>
               <txnTypeSpecificFields>
                 <appCallTxFields>
                   <applicationID> APP_ID </applicationID>
                   ...
                 </appCallTxFields>
               </txnTypeSpecificFields>
               ...
             </transaction>) => panic(ITXN_REENTRY)
             ...
       </k>
       <activeApps> AA </activeApps>
    requires APP_ID in AA

  rule <k> #checkForReentrance(_) => . ...</k>  [owise]

  // Ensures the transaction is not malformed prior to executing it in a group. E.g., has fields set only for
  // one type of transaction. This implementation does not yet allow unsetting of fields, e.g. setting them to
  // a default value, allowing you to set more than one type of transaction field as long as all but one end
  // up with only default values.
  syntax KItem ::= #checkItxnFieldsCoherent(TransactionCell)

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <payTxFields> _ </payTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <appCallTxFields> _ </appCallTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <keyRegTxFields> _ </keyRegTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <assetConfigTxFields> _ </assetConfigTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <assetTransferTxFields> _ </assetTransferTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(
         <transaction> 
           <txnTypeSpecificFields>
             <assetFreezeTxFields> _ </assetFreezeTxFields>
           </txnTypeSpecificFields>
           ...
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxnFieldsCoherent(<transaction> T </transaction>) => panic(TXN_INVALID) ...</k> [owise]

  syntax KItem ::= #checkItxns(List)

  rule <k> #checkItxns((ListItem(T:TransactionCell) REST)) => (#checkItxn(T) ~> #checkItxns(REST)) ...</k>
  rule <k> #checkItxns(.List) => . ...</k>

  syntax AlgorandCommand ::= #evalTxGroup()

  syntax KItem ::= #executeItxnGroup()
  //----------------------------------

  rule <k> #executeItxnGroup() => (#saveState() ~> #pushItxns() ~> #evalTxGroup()) ...</k>

  syntax KItem ::= #pushItxns()
  //---------------------------

  rule <k> #pushItxns() => (#pushTxnFront(<txID> TXN_ID </txID>) ~> #pushItxns()) ...</k>
       <innerTransactions> OTHER_ITXNS:List (ListItem(
         <transaction>
           <txID> _ </txID>
           <txHeader>
             <groupID> GROUP_ID </groupID>
             TX_HEADER
           </txHeader>
           TXN_BODY
         </transaction>
         ) => .List)
       </innerTransactions>
       <transactions>
         (.Bag =>
         <transaction>
           <txID> TXN_ID </txID>
           <txHeader>
             <groupID> GROUP_ID </groupID>
             TX_HEADER
           </txHeader>
           TXN_BODY
         </transaction>)
         TXNS
       </transactions>
       <nextTxnID> TXN_ID => TXN_ID +Int 1 </nextTxnID>

  rule <k> #pushItxns() => . ...</k>
       <innerTransactions> .List </innerTransactions>

  syntax KItem ::= #saveState()

  rule <k> #saveState() => . ...</k>
       <currentTxnExecution> C </currentTxnExecution>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <txnExecutionContext>
           _ => <currentTxnExecution> C </currentTxnExecution>
         </txnExecutionContext>
         ...
       </transaction>

  syntax KItem ::= #loadFromGroupInner(Int, TxnField)
  syntax KItem ::= #loadFromGroupInner(Int, TxnaField, Int)

  rule <k> #loadFromGroupInner(GROUP_IDX, FIELD) => . ...</k>
       <lastTxnGroupID> LAST_GROUP </lastTxnGroupID>
       <stack> XS => ({getTxnField(TX_ID, FIELD)}:>TValue : XS) </stack>
       <stacksize> SS => SS +Int 1 </stacksize>
       <transaction>
         <txID> TX_ID </txID>
         <groupID> LAST_GROUP </groupID>
         <groupIdx> GROUP_IDX </groupIdx>
         ...
       </transaction>
//    requires isTValue(getTxnField(TX_ID, FIELD))

  rule <k> #loadFromGroupInner(GROUP_IDX, FIELD, IDX) => . ...</k>
       <lastTxnGroupID> LAST_GROUP </lastTxnGroupID>
       <stack> XS => ({getTxnField(TX_ID, FIELD, IDX)}:>TValue : XS) </stack>
       <stacksize> SS => SS +Int 1 </stacksize>
       <transaction>
         <txID> TX_ID </txID>
         <groupID> LAST_GROUP </groupID>
         <groupIdx> GROUP_IDX </groupIdx>
         ...
       </transaction>
    requires isTValue(getTxnField(TX_ID, FIELD, IDX))

  syntax Int ::= getLastItxnGroupIdx()  [function]

  rule [[ getLastItxnGroupIdx() => countTxnsInGroup(<transactions> TXNS </transactions>, GROUP) -Int 1 ]]
       <transactions> TXNS </transactions>
       <lastTxnGroupID> GROUP </lastTxnGroupID>

endmodule
```
