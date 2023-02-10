Algorand Transaction Representation
===================================

```k
require "avm/teal/teal-fields.md"
require "avm/teal/teal-types.md"
require "avm/teal/teal-syntax.md"
```

Transaction State Representation
--------------------------------

```k
module TXN-FIELDS
  imports TEAL-FIELDS
  imports TEAL-SYNTAX
  imports BYTES
  imports AVM-CONSTANTS
```

*Pseudo fields*

We maintain a number of pseudo fields that are not part of the official AVM specification and serve the internal purposes of the semantics.

In TEALv4, the opcodes `gload` and `gloads` were added to access the final scratch space of the
past application call transactions in the group. We, thus, maintain a `<finalScratch>` sub-cell, initially an empty `.Map`. The cell will be hold the final state of that transaction's scratch space.

```k
```

*Transaction Header*

```k
  configuration
      <txHeader>
        <fee>         NoTValue </fee>
        <firstValid>  NoTValue </firstValid>       // first round during which the transaction is valid
        <lastValid>   NoTValue </lastValid>        // the transaction is not valid beyond this round (round range max is 1000 rounds)
        <genesisHash> NoTValue </genesisHash>      // uniquely identifies the network
        <sender>      NoTValue </sender>
        <txType>      NoTValue </txType>
        <typeEnum>    NoTValue </typeEnum>
        <groupID>     ""       </groupID>
        <groupIdx>    NoTValue </groupIdx>
        <genesisID>   NoTValue </genesisID>        // a human-readable name: does not necessarily uniquely identify the network
        <lease>       NoTValue </lease>
        <note>        NoTValue </note>
        <rekeyTo>     NoTValue </rekeyTo>
      </txHeader>
```

*Pay Transaction*

```k
  configuration
      <payTxFields multiplicity="?">
        <receiver>         NoTValue </receiver>
        <amount>           NoTValue </amount>           // this is 0 if not specified
        <closeRemainderTo> NoTValue </closeRemainderTo> // close the sender account and transfer any remaining balance to this account
      </payTxFields>
```

*Application Call Transaction*

```k
  configuration
      <appCallTxFields multiplicity="?">
        <applicationID>        NoTValue    </applicationID>
        <onCompletion>         NoTValue    </onCompletion>
        <accounts>             .TValueList </accounts>
        <approvalProgramSrc>     (int 0):TealInputPgm </approvalProgramSrc>
        <clearStateProgramSrc>   (int 1):TealInputPgm </clearStateProgramSrc>
        <approvalProgram>      NoTValue      </approvalProgram>
        <clearStateProgram>    NoTValue      </clearStateProgram>
        <applicationArgs>      .TValueList </applicationArgs> // maximum size is 2KB, and all args are internally byte strings
        <foreignApps>          .TValueList </foreignApps>
        <foreignAssets>        .TValueList </foreignAssets>
        <boxReferences>        .TValuePairList </boxReferences>
        <globalStateSchema>
          <globalNui> NoTValue </globalNui>
          <globalNbs> NoTValue </globalNbs>
        </globalStateSchema>
        <localStateSchema>
          <localNui> NoTValue </localNui>
          <localNbs> NoTValue </localNbs>
        </localStateSchema>
        <extraProgramPages> NoTValue </extraProgramPages>
      </appCallTxFields>
```

*Key Registration Transaction*

```k
  configuration
    <keyRegTxFields multiplicity="?">
      <votePk>           NoTValue </votePk>
      <selectionPK>      NoTValue </selectionPK>
      <voteFirst>        NoTValue </voteFirst>
      <voteLast>         NoTValue </voteLast>
      <voteKeyDilution>  NoTValue </voteKeyDilution>
      <nonparticipation> NoTValue </nonparticipation>
    </keyRegTxFields>
```

*Asset Configuration Transaction*

```k
  // Note: - Asset creation: if no asset ID specified
  //         Asset update: if both asset ID and (all) asset params are specified
  //         Asset destruction: if asset ID specified but no parameters
  configuration
    <assetConfigTxFields multiplicity="?">
      <configAsset> NoTValue </configAsset>           // the asset ID
      <assetParams>
        <configTotal>         0        </configTotal>
        <configDecimals>      0        </configDecimals>
        <configDefaultFrozen> 0        </configDefaultFrozen>
        <configUnitName>      .Bytes   </configUnitName>
        <configAssetName>     .Bytes   </configAssetName>
        <configAssetURL>      .Bytes   </configAssetURL>
        <configMetaDataHash>  .Bytes   </configMetaDataHash>
        <configManagerAddr>   PARAM_ZERO_ADDR </configManagerAddr>
        <configReserveAddr>   PARAM_ZERO_ADDR </configReserveAddr>
        <configFreezeAddr>    PARAM_ZERO_ADDR </configFreezeAddr>
        <configClawbackAddr>  PARAM_ZERO_ADDR </configClawbackAddr>
      </assetParams>
    </assetConfigTxFields>
```

*Asset Transfer Transaction*

```k
  // Note: Three uses: 1. opt-in to receive an asset (sender and receiver are the same and the amount is 0)
  //                   2. Transfer an Asset (amount is non-zero, and assumes the receiver had already opted-in before)
  //                   3. Revoke an asset (having an asset asender, from which asset will be revoked)
  configuration
    <assetTransferTxFields multiplicity="?">
      <xferAsset>     0 </xferAsset>
      <assetAmount>   0 </assetAmount>
      <assetReceiver> .Bytes </assetReceiver>
      <assetASender>  .Bytes </assetASender>
      <assetCloseTo>  .Bytes </assetCloseTo>
    </assetTransferTxFields>
```

*Asset Freeze Transaction*

```k
 configuration
   <assetFreezeTxFields multiplicity="?">
     <freezeAccount> PARAM_ZERO_ADDR </freezeAccount>
     <freezeAsset>   0 </freezeAsset>
     <assetFrozen>   0 </assetFrozen>
   </assetFreezeTxFields>

endmodule
```

Transaction Group State Representation
--------------------------------------

```k
module ALGO-TXN
  imports TXN-FIELDS
  imports TEAL-TYPES
  imports SET
  imports LIST
  imports BYTES-HOOKED
  imports GLOBALS
```

*Transaction Group Configuration*

```k
  // TODO: We also need to represent signed transactions (? -- maybe for later)
  // Note: Signed Transaction: (Sig, MSig, LogicSig, Txn)
  // Note: There can be up to 16 transactions in a group (?)
  //       (see https://developer.algorand.org/docs/features/atomic_transfers/
  // Note: Group-id is calculated by hashing the concatenation of its list of transactions.
  //       Then, it is stored in the header field of each transaction in the list. (So hashing is performed
  //       on the transactions with empty group-id fields?)

  configuration
      <transactions>
        <transaction multiplicity="*" type="Map">
          <txID> "" </txID>
          <txHeader/>
          <txnTypeSpecificFields>
            <payTxFields/>
            <appCallTxFields/>
            <keyRegTxFields/>
            <assetConfigTxFields/>
            <assetTransferTxFields/>
            <assetFreezeTxFields/>
          </txnTypeSpecificFields>
          <applyData>
            <txScratch>       .Map  </txScratch>
            <txConfigAsset>   0     </txConfigAsset>
            <txApplicationID> 0     </txApplicationID>
            <log>
              <logData> .TValueList </logData>
              <logSize> 0:TValue    </logSize>
            </log>
          </applyData>
          <txnExecutionContext> .K </txnExecutionContext>
          <resume> false </resume>
        </transaction>
      </transactions>
```

*Transaction ID Getter*

```k
  syntax String ::= getTxID(TransactionCell) [function, total]
  //---------------------------------------------------------------
  rule getTxID(<transaction> <txID> ID </txID> ... </transaction>) => ID
```

*Transaction Group Accessors*

```k
  syntax String ::= getTxnGroupID(String) [function]
  //------------------------------------------------
  rule [[ getTxnGroupID(TXN_ID) => I ]]
       <transaction> 
         <txID> TXN_ID </txID>
         <groupID> I </groupID>
         ...
       </transaction>

  syntax Int ::= getTxnGroupIndex(String) [function]
  //------------------------------------------------
  rule [[ getTxnGroupIndex(TXN_ID) => I ]]
       <transaction> 
         <txID> TXN_ID </txID>
         <groupIdx> I </groupIdx>
         ...
       </transaction>

  syntax MaybeTValue ::= getTxnField(String, TxnField)                 [function, total]
  syntax MaybeTValue ::= getTxnField(String, TxnaField, Int)           [function, total]
  syntax TValueList  ::= getTxnField(String, TxnaField)                [function, total]
  //-----------------------------------------------------------------------------

  rule [[ getTxnField(I, TxID) => normalize(I) ]]
       <transaction>
         <txID> I </txID>
         ...
       </transaction>

  rule [[ getTxnField(I, Sender) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <sender> X </sender>
         ...
       </transaction>

  rule [[ getTxnField(I, Fee) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <fee> X </fee>
         ...
       </transaction>

  rule [[ getTxnField(I, FirstValid) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <firstValid> X </firstValid>
         ...
       </transaction>

  //  rule [[ getTxnField(I, FirstValidTime) => normalize(X) ]]
  //    <transaction>
  //      <txID> I </txID>
  //      <firstValidTime> X </firstValidTime>
  //      ...
  //    </transaction>

  rule [[ getTxnField(I, LastValid) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <lastValid> X </lastValid>
         ...
       </transaction>

  rule [[ getTxnField(I, Note)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <note> X </note>
         ...
       </transaction>

  rule [[ getTxnField(I, Lease)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <lease> X </lease>
         ...
       </transaction>

  rule [[ getTxnField(I, Type)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <txType> X </txType>
         ...
       </transaction>

  rule [[ getTxnField(I, TypeEnum)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> X </typeEnum>
         ...
       </transaction>

  rule [[ getTxnField(I, GroupIndex)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <groupIdx> X </groupIdx>
         ...
       </transaction>

  rule [[ getTxnField(I, RekeyTo)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <rekeyTo> X </rekeyTo>
         ...
       </transaction>

  rule [[ getTxnField(I, Receiver) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <receiver> X </receiver>
         ...
       </transaction>

  rule [[ getTxnField(I, Amount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <amount> X </amount>
         ...
       </transaction>

  rule [[ getTxnField(I, CloseRemainderTo) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <closeRemainderTo> X </closeRemainderTo>
         ...
       </transaction>

  rule [[ getTxnField(I, VotePK) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <votePk> X </votePk>
         ...
       </transaction>

  rule [[ getTxnField(I, SelectionPK) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <selectionPK> X </selectionPK>
         ...
       </transaction>

  rule [[ getTxnField(I, VoteFirst) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <voteFirst> X </voteFirst>
         ...
       </transaction>

  rule [[ getTxnField(I, VoteLast) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <voteLast> X </voteLast>
         ...
       </transaction>

  rule [[ getTxnField(I, VoteKeyDilution) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <voteKeyDilution> X </voteKeyDilution>
         ...
       </transaction>

  rule [[ getTxnField(I, XferAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <xferAsset> X </xferAsset>
         ...
       </transaction>

  rule [[ getTxnField(I, AssetAmount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <assetAmount> X </assetAmount>
         ...
       </transaction>

  rule [[ getTxnField(I, AssetSender) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <assetASender> X </assetASender>
         ...
       </transaction>

  rule [[ getTxnField(I, AssetReceiver) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <assetReceiver> X </assetReceiver>
         ...
       </transaction>

  rule [[ getTxnField(I, AssetCloseTo) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <assetCloseTo> X </assetCloseTo>
         ...
       </transaction>

  rule [[ getTxnField(I, ApplicationID) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <applicationID> X </applicationID>
         ...
       </transaction>

  rule [[ getTxnField(I, OnCompletion) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <onCompletion> X </onCompletion>
         ...
       </transaction>

  rule [[ getTxnField(I, ApplicationArgs, J) => normalize(getTValueAt(J, X)) ]]
       <transaction>
         <txID> I </txID>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>
    requires 0 <=Int J andBool J <Int size(X)

  rule [[ getTxnField(I, ApplicationArgs) => X ]]
       <transaction>
         <txID> I </txID>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>

  rule [[ getTxnField(I, NumAppArgs) => size(X) ]]
       <transaction>
         <txID> I </txID>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>

  rule [[ getTxnField(I, Accounts, 0) => normalize(A) ]]
       <transaction>
         <txID> I </txID>
         <sender> A </sender>
         ...
       </transaction>

  rule [[ getTxnField(I, Accounts, J) => normalize(getTValueAt(J -Int 1, X)) ]]
       <transaction>
         <txID> I </txID>
         <accounts> X </accounts>
         ...
       </transaction>
    requires 0 <Int J andBool J <=Int size(X)

  rule [[ getTxnField(I, Accounts) => (A X) ]]
       <transaction>
         <txID> I </txID>
         <sender> A </sender>
         <accounts> X </accounts>
         ...
       </transaction>

  rule [[ getTxnField(I, NumAccounts) => size(X) ]]
       <transaction>
         <txID> I </txID>
         <accounts> X </accounts>
         ...
       </transaction>

  rule [[ getTxnField(I, ApprovalProgram) => X ]]
       <transaction>
         <txID> I </txID>
         <approvalProgram> X </approvalProgram>
         ...
       </transaction>

  rule [[ getTxnField(I, ClearStateProgram) => X ]]
       <transaction>
         <txID> I </txID>
         <clearStateProgram> X </clearStateProgram>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configAsset> X </configAsset>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetTotal) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configTotal> X </configTotal>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetDecimals) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configDecimals> X </configDecimals>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetDefaultFrozen) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configDefaultFrozen> X </configDefaultFrozen>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetUnitName) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configUnitName> X </configUnitName>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetName) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configAssetName> X </configAssetName>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetURL) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configAssetURL> X </configAssetURL>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetMetaDataHash) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configMetaDataHash> X </configMetaDataHash>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetManager) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configManagerAddr> X </configManagerAddr>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetReserve) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configReserveAddr> X </configReserveAddr>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetFreeze) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configFreezeAddr> X </configFreezeAddr>
         ...
       </transaction>

  rule [[ getTxnField(I, ConfigAssetClawback) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <configClawbackAddr> X </configClawbackAddr>
         ...
       </transaction>

  rule [[ getTxnField(I, FreezeAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <freezeAsset> X </freezeAsset>
         ...
       </transaction>

  rule [[ getTxnField(I, FreezeAssetAccount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <freezeAccount> X </freezeAccount>
         ...
       </transaction>

  rule [[ getTxnField(I, FreezeAssetFrozen) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <assetFrozen> X </assetFrozen>
         ...
       </transaction>

  rule [[ getTxnField(I, Applications, 0) => normalize(A) ]]
       <transaction>
         <txID> I </txID>
         ...
       </transaction>
       <currentApplicationID> A </currentApplicationID>

  rule [[ getTxnField(I, Applications, J) => normalize(getTValueAt(J -Int 1, X)) ]]
       <transaction>
         <txID> I </txID>
         <foreignApps> X </foreignApps>
         ...
       </transaction>
    requires 0 <=Int J andBool J <=Int size(X)

  rule [[ getTxnField(I, Applications) => (A X) ]]
       <transaction>
         <txID> I </txID>
         <foreignApps> X </foreignApps>
         ...
       </transaction>
       <currentApplicationID> A </currentApplicationID>

  rule [[ getTxnField(I, Assets, J) => normalize(getTValueAt(J, X)) ]]
       <transaction>
         <txID> I </txID>
         <foreignAssets> X </foreignAssets>
         ...
       </transaction>
    requires 0 <=Int J andBool J <Int size(X)

  rule [[ getTxnField(I, Assets) => X ]]
       <transaction>
         <txID> I </txID>
         <foreignAssets> X </foreignAssets>
         ...
       </transaction>

  rule [[ getTxnField(I, NumAssets) => size(X) ]]
       <transaction>
         <txID> I </txID>
         <foreignAssets> X </foreignAssets>
         ...
       </transaction>

  rule [[ getTxnField(I, LastLog) => MSG ]]
       <transaction>
         <txID> I </txID>
         <logData> _ MSG:TBytes </logData>
         ...
       </transaction>

  rule [[ getTxnField(I, LastLog) => MSG ]]
       <transaction>
         <txID> I </txID>
         <logData> MSG:TBytes </logData>
         ...
       </transaction>

  rule [[ getTxnField(I, NumLogs) => size(LOGS) ]]
       <transaction>
         <txID> I </txID>
         <logData> LOGS </logData>
         ...
       </transaction>

  rule [[ getTxnField(I, Logs, J) => normalize(getTValueAt(J, LOGS)) ]]
       <transaction>
         <txID> I </txID>
         <logData> LOGS </logData>
         ...
       </transaction>

  rule [[ getTxnField(I, Logs) => LOGS ]]
       <transaction>
         <txID> I </txID>
         <logData> LOGS </logData>
         ...
       </transaction>

  rule [[ getTxnField(I, CreatedApplicationID) => CREATED_APP ]]
       <transaction>
         <txID> I </txID>
         <txApplicationID> CREATED_APP </txApplicationID>
         ...
       </transaction>

  rule [[ getTxnField(I, CreatedAssetID) => CREATED_ASSET ]]
       <transaction>
         <txID> I </txID>
         <txConfigAsset> CREATED_ASSET </txConfigAsset>
         ...
       </transaction>
```

*Failure*
```k
  rule getTxnField(_, _:TxnaField    ) => .TValueList            [owise]
  rule getTxnField(_, FIELD:TxnField ) => getDefaultValue(FIELD) [owise]
  rule getTxnField(_, _:TxnaField, _ ) => NoTValue               [owise]
```

*Default field values*
```k

  syntax TValue ::= getDefaultValue(TxnField) [function]

  rule getDefaultValue(Sender)                    => PARAM_ZERO_ADDR
  rule getDefaultValue(Fee)                       => 0
  rule getDefaultValue(FirstValid)                => 0
  rule getDefaultValue(LastValid)                 => 0
  rule getDefaultValue(Note)                      => .Bytes
  rule getDefaultValue(Lease)                     => .Bytes
  rule getDefaultValue(Receiver)                  => PARAM_ZERO_ADDR
  rule getDefaultValue(Amount)                    => 0
  rule getDefaultValue(CloseRemainderTo)          => PARAM_ZERO_ADDR
  rule getDefaultValue(VotePK)                    => PARAM_ZERO_ADDR
  rule getDefaultValue(SelectionPK)               => PARAM_ZERO_ADDR
  rule getDefaultValue(VoteFirst)                 => 0
  rule getDefaultValue(VoteLast)                  => 0
  rule getDefaultValue(VoteKeyDilution)           => 0
  rule getDefaultValue(Type)                      => .Bytes
  rule getDefaultValue(TypeEnum)                  => 0
  rule getDefaultValue(XferAsset)                 => 0
  rule getDefaultValue(AssetAmount)               => 0
  rule getDefaultValue(AssetSender)               => PARAM_ZERO_ADDR
  rule getDefaultValue(AssetReceiver)             => PARAM_ZERO_ADDR
  rule getDefaultValue(AssetCloseTo)              => PARAM_ZERO_ADDR
  rule getDefaultValue(GroupIndex)                => 0
  rule getDefaultValue(TxID)                      => .Bytes
  rule getDefaultValue(ApplicationID)             => 0
  rule getDefaultValue(OnCompletion)              => 0
  rule getDefaultValue(NumAppArgs)                => 0
  rule getDefaultValue(NumAccounts)               => 0
  rule getDefaultValue(ApprovalProgram)           => .Bytes
  rule getDefaultValue(ClearStateProgram)         => .Bytes
  rule getDefaultValue(RekeyTo)                   => PARAM_ZERO_ADDR
  rule getDefaultValue(ConfigAsset)               => 0
  rule getDefaultValue(ConfigAssetTotal)          => 0
  rule getDefaultValue(ConfigAssetDecimals)       => 0
  rule getDefaultValue(ConfigAssetDefaultFrozen)  => 0
  rule getDefaultValue(ConfigAssetUnitName)       => .Bytes
  rule getDefaultValue(ConfigAssetName)           => .Bytes
  rule getDefaultValue(ConfigAssetURL)            => .Bytes
  rule getDefaultValue(ConfigAssetMetaDataHash)   => .Bytes
  rule getDefaultValue(ConfigAssetManager)        => PARAM_ZERO_ADDR
  rule getDefaultValue(ConfigAssetReserve)        => PARAM_ZERO_ADDR
  rule getDefaultValue(ConfigAssetFreeze)         => PARAM_ZERO_ADDR
  rule getDefaultValue(ConfigAssetClawback)       => PARAM_ZERO_ADDR
  rule getDefaultValue(FreezeAsset)               => 0
  rule getDefaultValue(FreezeAssetAccount)        => PARAM_ZERO_ADDR
  rule getDefaultValue(FreezeAssetFrozen)         => 0
  rule getDefaultValue(NumAssets)                 => 0
  rule getDefaultValue(NumApplications)           => 0
  rule getDefaultValue(GlobalNumUint)             => 0
  rule getDefaultValue(GlobalNumByteSlice)        => 0
  rule getDefaultValue(LocalNumUint)              => 0
  rule getDefaultValue(LocalNumByteSlice)         => 0
  rule getDefaultValue(ExtraProgramPages)         => 0
  rule getDefaultValue(Nonparticipation)          => 0
  rule getDefaultValue(NumLogs)                   => 0
  rule getDefaultValue(CreatedAssetID)            => 0
  rule getDefaultValue(CreatedApplicationID)      => 0
  rule getDefaultValue(LastLog)                   => .Bytes
  rule getDefaultValue(StateProofPK)              => .Bytes
  rule getDefaultValue(NumApprovalProgramPages)   => 0
  rule getDefaultValue(NumClearStateProgramPages) => 0

```

*Other Helper Functions*

```k
  syntax Bool ::= Int "in_calledApps" "(" TransactionsCell ")" [function]
  //---------------------------------------------------------------------
  rule I in_calledApps( <transactions>
                          <transaction>
                            <txnTypeSpecificFields>
                              <appCallTxFields>
                                <applicationID> APP_ID </applicationID> ...
                              </appCallTxFields>
                            </txnTypeSpecificFields> ...
                          </transaction>
                          REST
                        </transactions> )
       => I in_calledApps(<transactions> REST </transactions>)
    requires I =/=K APP_ID

  rule I in_calledApps( <transactions>
                          <transaction>
                            <txnTypeSpecificFields>
                              <appCallTxFields>
                                <applicationID> I </applicationID> ...
                              </appCallTxFields>
                            </txnTypeSpecificFields> ...
                          </transaction>
                          ...
                        </transactions> )
       => true

  rule _ in_calledApps( <transactions> .Bag </transactions> ) => false
```

```k
  syntax Int ::= groupSize(String, TransactionsCell) [function]
  //------------------------------------------------
  rule groupSize( GROUP_ID,
                  <transactions>
                    <transaction>
                      <groupID> GROUP_ID </groupID>
                      ...
                    </transaction>
                    REST
                  </transactions>)
       => 1 +Int groupSize(GROUP_ID, <transactions> REST </transactions>)

  rule groupSize( GROUP_ID,
                  <transactions>
                    <transaction>
                      <groupID> GROUP_ID' </groupID>
                      ...
                    </transaction>
                    REST
                  </transactions>)
       => groupSize(GROUP_ID, <transactions> REST </transactions>)
    requires GROUP_ID =/=K GROUP_ID'

  rule groupSize( _, <transactions> .Bag </transactions>) => 0
```


```k
  syntax Bool ::= String "in_txns" "(" TransactionsCell ")" [function]
  // --------------------------------------------------------------
  rule I in_txns( <transactions>
                    <transaction>
                      <txID> I </txID> ...
                    </transaction> ...
                  </transactions> )
       => true

  rule I in_txns( <transactions>
                    <transaction>
                      <txID> I' </txID> ...
                    </transaction> REST
                  </transactions> )
       => I in_txns( <transactions> REST </transactions> )
    requires I =/=K I'

  rule _ in_txns( <transactions> .Bag </transactions> ) => false


endmodule
```
