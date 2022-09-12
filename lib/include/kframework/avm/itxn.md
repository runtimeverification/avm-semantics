```k
requires "avm/txn.md"
requires "avm/avm-configuration.md"
requires "avm/teal/teal-types.md"
requires "avm/teal/teal-fields.md"
requires "avm/teal/teal-execution.md"

module ALGO-ITXN
  imports ALGO-TXN
  imports AVM-CONFIGURATION
  imports TEAL-TYPES
  imports TEAL-FIELDS
  imports TEAL-EXECUTION
  imports MAP

  syntax KItem ::= #setItxnField(TxnFieldTop, TValue, Int)

  rule <k> #setItxnField(Sender, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <sender> _ => VAL </sender> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Fee, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <fee> _ => VAL </fee> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Note, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <note> _ => VAL </note> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(RekeyTo, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <rekeyTo> _ => VAL </rekeyTo> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(TxType, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> 
                   <txType> _ => VAL </txType> 
                   <typeEnum> _=> typeString2Enum(VAL) </typeEnum>
                    ...
                  </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(TypeEnum, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> 
                   <txType> _ => typeEnum2String(VAL) </txType> 
                   <typeEnum> _ => VAL </typeEnum>
                   ...
                  </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(_:TxnPayField, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .PayTxFieldsCell =>
           <payTxFields>
             <receiver> .Bytes </receiver>
             <amount> 0 </amount>
             <closeRemainderTo> .Bytes </closeRemainderTo>
           </payTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Receiver, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <receiver> _ => VAL </receiver> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Amount, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <amount> _ => VAL </amount> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(CloseRemainderTo, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <closeRemainderTo> _ => VAL </closeRemainderTo> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(_:TxnKeyregField, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .KeyRegTxFieldsCell =>
           <keyRegTxFields>
             <votePk> .Bytes </votePk>
             <selectionPK> .Bytes </selectionPK>
             <voteFirst> 0 </voteFirst>
             <voteLast> 0 </voteLast>
             <voteKeyDilution> 0 </voteKeyDilution>
             <nonparticipation> 0 </nonparticipation>
           </keyRegTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(VotePK, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <votePk> _ => VAL </votePk> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(SelectionPK, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <selectionPK> _ => VAL </selectionPK> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(VoteFirst, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <voteFirst> _ => VAL </voteFirst> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(VoteLast, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <voteLast> _ => VAL </voteLast> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(VoteKeyDilution, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <voteKeyDilution> _ => VAL </voteKeyDilution> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Nonparticipation, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <nonparticipation> _ => VAL </nonparticipation> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAcfgField, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .AssetConfigTxFieldsCell =>
           <assetConfigTxFields>
             <configAsset> 0 </configAsset>
             <assetParams>
               <configTotal> 0 </configTotal>
               <configDecimals> 0 </configDecimals>
               <configDefaultFrozen> 0 </configDefaultFrozen>
               <configUnitName> .Bytes </configUnitName>
               <configAssetName> .Bytes </configAssetName>
               <configAssetURL> .Bytes </configAssetURL>
               <configMetaDataHash> .Bytes </configMetaDataHash>
               <configManagerAddr> .Bytes </configManagerAddr>
               <configReserveAddr> .Bytes </configReserveAddr>
               <configFreezeAddr> .Bytes </configFreezeAddr>
               <configClawbackAddr> .Bytes </configClawbackAddr>
             </assetParams>
           </assetConfigTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAsset, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configAsset> _ => VAL </configAsset> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetTotal, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configTotal> _ => VAL </configTotal> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetDecimals, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configDecimals> _ => VAL </configDecimals> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetDefaultFrozen, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configDefaultFrozen> _ => VAL </configDefaultFrozen> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetUnitName, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configUnitName> _ => VAL </configUnitName> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetName, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configAssetName> _ => VAL </configAssetName> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetURL, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configAssetURL> _ => VAL </configAssetURL> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetMetaDataHash, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configMetaDataHash> _ => VAL </configMetaDataHash> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetManager, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configManagerAddr> _ => VAL </configManagerAddr> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetReserve, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configReserveAddr> _ => VAL </configReserveAddr> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetFreeze, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configFreezeAddr> _ => VAL </configFreezeAddr> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ConfigAssetClawback, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <configClawbackAddr> _ => VAL </configClawbackAddr> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAxferField, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .AssetTransferTxFieldsCell =>
           <assetTransferTxFields>
             <xferAsset> 0 </xferAsset>
             <assetAmount> 0 </assetAmount>
             <assetReceiver> .Bytes </assetReceiver>
             <assetASender> .Bytes </assetASender>
             <assetCloseTo> .Bytes </assetCloseTo>
           </assetTransferTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(XferAsset, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <xferAsset> _ => VAL </xferAsset> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(AssetAmount, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <assetAmount> _ => VAL </assetAmount> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(AssetASender, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <assetASender> _ => VAL </assetASender> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(AssetReceiver, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <assetReceiver> _ => VAL </assetReceiver> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(AssetCloseTo, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <assetCloseTo> _ => VAL </assetCloseTo> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(_:TxnAfrzField, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .AssetFreezeTxFieldsCell =>
           <assetFreezeTxFields>
             <freezeAccount> .Bytes </freezeAccount>
             <freezeAsset> 0 </freezeAsset>
             <assetFrozen> 0 </assetFrozen>
           </assetFreezeTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(FreezeAsset, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <freezeAsset> _ => VAL </freezeAsset> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(FreezeAssetAccount, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <freezeAccount> _ => VAL </freezeAccount> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(FreezeAssetFrozen, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <assetFrozen> _ => VAL </assetFrozen> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(FIELD, _, IDX) ... </k>
       <innerTransactions>
         IDX |->
         <transaction>
           .AppCallTxFieldsCell =>
           <appCallTxFields>
             <applicationID> 0 </applicationID>
             <onCompletion> 0 </onCompletion>
             <accounts> .TValueList </accounts>
             <approvalProgramSrc> (int 0):TealInputPgm </approvalProgramSrc>
             <clearStateProgramSrc> (int 0):TealInputPgm </clearStateProgramSrc>
             <approvalProgram> .Bytes </approvalProgram>
             <clearStateProgram> .Bytes </clearStateProgram>
             <applicationArgs> .TValueList </applicationArgs>
             <foreignApps> .TValueList </foreignApps>
             <foreignAssets> .TValueList </foreignAssets>
             <globalStateSchema>
               <globalNui> 0 </globalNui>
               <globalNbs> 0 </globalNbs>
             </globalStateSchema>
             <localStateSchema>
               <localNui> 0 </localNui>
               <localNbs> 0 </localNbs>
             </localStateSchema>
             <extraProgramPages> 0 </extraProgramPages>
             <txScratch> .Map </txScratch>
             <logs> .TValueList </logs>
             <logSize> 0 </logSize>
           </appCallTxFields>
           ...
         </transaction>
         ...
       </innerTransactions>
    requires isTxnApplField(FIELD) orBool isTxnaField(FIELD)

  rule <k> #setItxnField(ApplicationID, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <applicationID> _ => VAL </applicationID> ... </transaction>
         ...
       </innerTransactions>
       
  rule <k> #setItxnField(OnCompletion, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <onCompletion> _ => VAL </onCompletion> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ApprovalProgram, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <approvalProgram> _ => VAL </approvalProgram> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ClearStateProgram, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <clearStateProgram> _ => VAL </clearStateProgram> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(ApplicationArgs, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <applicationArgs> APP_ARGS => append(VAL, APP_ARGS) </applicationArgs> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Accounts, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <accounts> ACCOUNTS => append(VAL, ACCOUNTS) </accounts> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Applications, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <foreignApps> APPS => append(VAL, APPS) </foreignApps> ... </transaction>
         ...
       </innerTransactions>

  rule <k> #setItxnField(Assets, VAL, IDX) => . ... </k>
       <innerTransactions>
         IDX |-> <transaction> <foreignAssets> ASSETS => append(VAL, ASSETS) </foreignAssets> ... </transaction>
         ...
       </innerTransactions>
```

```k
  // Ensures the transaction is not malformed prior to executing it in a group. E.g., has fields set only for
  // one type of transaction. This implementation does not yet allow unsetting of fields, e.g. setting them to
  // a default value, allowing you to set more than one type of transaction field as long as all but one end
  // up with only default values.
  syntax KItem ::= #checkItxn(TransactionCell)

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <payTxFields> _ </payTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <appCallTxFields> _ </appCallTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <keyRegTxFields> _ </keyRegTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <assetConfigTxFields> _ </assetConfigTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <assetTransferTxFields> _ </assetTransferTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(
         <transaction> 
           <txID> _ </txID>
           <txHeader> _ </txHeader>
           <assetFreezeTxFields> _ </assetFreezeTxFields>
         </transaction>) => . ... 
       </k>

  rule <k> #checkItxn(<transaction> T </transaction>) => panic(TXN_INVALID) ...</k> [owise]

  syntax KItem ::= #checkItxns(Map)

  rule <k> #checkItxns((_ |-> T) REST) => #checkItxn(T) ~> #checkItxns(REST) ...</k>
  rule <k> #checkItxns(.Map) => . ...</k>

endmodule
```
