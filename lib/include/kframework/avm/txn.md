Algorand Transaction Representation
===================================

```k
require "avm/teal/teal-fields.md"
require "avm/teal/teal-types.md"
```

Transaction State Representation
--------------------------------

```k
module TXN-FIELDS
  imports TEAL-FIELDS
  imports TEAL-SYNTAX
  imports BYTES
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
        <group>       NoTValue </group>
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
        <configTotal>         NoTValue </configTotal>
        <configDecimals>      NoTValue </configDecimals>
        <configDefaultFrozen> NoTValue </configDefaultFrozen>
        <configUnitName>      NoTValue </configUnitName>
        <configAssetName>     NoTValue </configAssetName>
        <configAssetURL>      NoTValue </configAssetURL>
        <configMetaDataHash>  NoTValue </configMetaDataHash>
        <configManagerAddr>   NoTValue </configManagerAddr>
        <configReserveAddr>   NoTValue </configReserveAddr>
        <configFreezeAddr>    NoTValue </configFreezeAddr>
        <configClawbackAddr>  NoTValue </configClawbackAddr>
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
      <xferAsset>     NoTValue </xferAsset>
      <assetAmount>   NoTValue </assetAmount>
      <assetReceiver> NoTValue </assetReceiver>
      <assetASender>  NoTValue </assetASender>
      <assetCloseTo>  NoTValue </assetCloseTo>
    </assetTransferTxFields>
```

*Asset Freeze Transaction*

```k
 configuration
   <assetFreezeTxFields multiplicity="?">
     <freezeAccount> NoTValue </freezeAccount>
     <freezeAsset>   NoTValue </freezeAsset>
     <assetFrozen>   NoTValue </assetFrozen>
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
      <txGroup>
        <txGroupID> 0 </txGroupID>
        <currentTx> 0 </currentTx>
        <transactions>
          <transaction multiplicity="*" type="Map">
            <txID> 0 </txID>
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
              <innerTxns>       .List </innerTxns>
              <txConfigAsset>   0     </txConfigAsset>
              <txApplicationID> 0     </txApplicationID>
              <log>
                <logData> .TValueList </logData>
                <logSize> 0:TValue    </logSize>
              </log>
            </applyData>
          </transaction>
        </transactions>
        <touchedAccounts> .Set </touchedAccounts>
      </txGroup>
```

*Transaction ID Getter*

```k
  syntax Int ::= getTxID(TransactionCell) [function, functional]
  //-------------------------------------------------------------
  rule getTxID(<transaction> <txID> ID </txID> ... </transaction>) => ID
```

*Transaction Group Accessors*

```k
  syntax Int ::= getTxnGroupID() [function]
  //--------------------------------------
  rule [[ getTxnGroupID() => I ]]
    <txGroupID> I </txGroupID>

  syntax Int ::= getCurrentTxn() [function]
  //--------------------------------------
  rule [[ getCurrentTxn() => I ]]
    <currentTx> I </currentTx>

  syntax MaybeTValue ::= getTxnField(Int, TxnField)       [function, functional]
  syntax MaybeTValue ::= getTxnField(Int, TxnaField, Int) [function, functional]
  syntax TValueList  ::= getTxnField(Int, TxnaField)      [function, functional]
  //-------------------------------------------------------------------------------
  rule [[ getTxnField(I, TxID) => normalize(I) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         ...
       </transaction>
    requires #isValidForTxnType(TxID, TYPE)

  rule [[ getTxnField(I, Sender) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <sender> X </sender>
         ...
       </transaction>
    requires #isValidForTxnType(Sender, TYPE)

  rule [[ getTxnField(I, Fee) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <fee> X </fee>
         ...
       </transaction>
    requires #isValidForTxnType(Fee, TYPE)

  rule [[ getTxnField(I, FirstValid) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <firstValid> X </firstValid>
         ...
       </transaction>
    requires #isValidForTxnType(FirstValid, TYPE)

  //  rule [[ getTxnField(I, FirstValidTime) => normalize(X) ]]
  //    <transaction>
  //      <txID> I </txID>
  //      <firstValidTime> X </firstValidTime>
  //      ...
  //    </transaction>

  rule [[ getTxnField(I, LastValid) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <lastValid> X </lastValid>
         ...
       </transaction>
    requires #isValidForTxnType(LastValid, TYPE)

  rule [[ getTxnField(I, Note)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <note> X </note>
         ...
       </transaction>
    requires #isValidForTxnType(Note, TYPE)

  rule [[ getTxnField(I, Lease)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <lease> X </lease>
         ...
       </transaction>
    requires #isValidForTxnType(Lease, TYPE)

  rule [[ getTxnField(I, TxType)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <txType> X </txType>
         ...
       </transaction>
    requires #isValidForTxnType(TxType, TYPE)

  rule [[ getTxnField(I, TypeEnum)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> X </typeEnum>
         ...
       </transaction>
    requires #isValidForTxnType(TypeEnum, X)

  rule [[ getTxnField(I, GroupIndex)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <group> X </group>
         ...
       </transaction>
    requires #isValidForTxnType(GroupIndex, TYPE)

  rule [[ getTxnField(I, RekeyTo)  => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <rekeyTo> X </rekeyTo>
         ...
       </transaction>
    requires #isValidForTxnType(RekeyTo, TYPE)

  rule [[ getTxnField(I, Receiver) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <receiver> X </receiver>
         ...
       </transaction>
    requires #isValidForTxnType(Receiver, TYPE)

  rule [[ getTxnField(I, Amount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <amount> X </amount>
         ...
       </transaction>
    requires #isValidForTxnType(Amount, TYPE)

  rule [[ getTxnField(I, CloseRemainderTo) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <closeRemainderTo> X </closeRemainderTo>
         ...
       </transaction>
    requires #isValidForTxnType(CloseRemainderTo, TYPE)

  rule [[ getTxnField(I, VotePK) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <votePk> X </votePk>
         ...
       </transaction>
    requires #isValidForTxnType(VotePK, TYPE)

  rule [[ getTxnField(I, SelectionPK) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <selectionPK> X </selectionPK>
         ...
       </transaction>
    requires #isValidForTxnType(SelectionPK, TYPE)

  rule [[ getTxnField(I, VoteFirst) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <voteFirst> X </voteFirst>
         ...
       </transaction>
    requires #isValidForTxnType(VoteFirst, TYPE)

  rule [[ getTxnField(I, VoteLast) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <voteLast> X </voteLast>
         ...
       </transaction>
    requires #isValidForTxnType(VoteLast, TYPE)

  rule [[ getTxnField(I, VoteKeyDilution) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <voteKeyDilution> X </voteKeyDilution>
         ...
       </transaction>
    requires #isValidForTxnType(VoteKeyDilution, TYPE)

  rule [[ getTxnField(I, XferAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <xferAsset> X </xferAsset>
         ...
       </transaction>
    requires #isValidForTxnType(XferAsset, TYPE)

  rule [[ getTxnField(I, AssetAmount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <assetAmount> X </assetAmount>
         ...
       </transaction>
    requires #isValidForTxnType(AssetAmount, TYPE)

  rule [[ getTxnField(I, AssetASender) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <assetASender> X </assetASender>
         ...
       </transaction>
    requires #isValidForTxnType(AssetASender, TYPE)

  rule [[ getTxnField(I, AssetReceiver) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <assetReceiver> X </assetReceiver>
         ...
       </transaction>
    requires #isValidForTxnType(AssetReceiver, TYPE)

  rule [[ getTxnField(I, AssetCloseTo) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <assetCloseTo> X </assetCloseTo>
         ...
       </transaction>
    requires #isValidForTxnType(AssetCloseTo, TYPE)

  rule [[ getTxnField(I, ApplicationID) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <applicationID> X </applicationID>
         ...
       </transaction>
    requires #isValidForTxnType(ApplicationID, TYPE)

  rule [[ getTxnField(I, OnCompletion) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <onCompletion> X </onCompletion>
         ...
       </transaction>
    requires #isValidForTxnType(OnCompletion, TYPE)

  rule [[ getTxnField(I, ApplicationArgs, J) => normalize(getTValueAt(J, X)) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>
    requires #isValidForTxnType(ApplicationArgs, TYPE)
     andBool 0 <=Int J andBool J <Int size(X)

  rule [[ getTxnField(I, ApplicationArgs) => X ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>
    requires #isValidForTxnType(ApplicationArgs, TYPE)

  rule [[ getTxnField(I, NumAppArgs) => size(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <applicationArgs> X </applicationArgs>
         ...
       </transaction>
    requires #isValidForTxnType(NumAppArgs, TYPE)

  rule [[ getTxnField(I, Accounts, 0) => normalize(A) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <sender> A </sender>
         ...
       </transaction>
    requires #isValidForTxnType(Accounts, TYPE)

  rule [[ getTxnField(I, Accounts, J) => normalize(getTValueAt(J -Int 1, X)) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <accounts> X </accounts>
         ...
       </transaction>
    requires #isValidForTxnType(Accounts, TYPE)
     andBool 0 <Int J andBool J <=Int size(X)

  rule [[ getTxnField(I, Accounts) => (A X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <sender> A </sender>
         <accounts> X </accounts>
         ...
       </transaction>
    requires #isValidForTxnType(Accounts, TYPE)

  rule [[ getTxnField(I, NumAccounts) => size(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <accounts> X </accounts>
         ...
       </transaction>
    requires #isValidForTxnType(NumAccounts, TYPE)

  rule [[ getTxnField(I, ApprovalProgram) => X ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <approvalProgram> X </approvalProgram>
         ...
       </transaction>
    requires #isValidForTxnType(ApprovalProgram, TYPE)

  rule [[ getTxnField(I, ClearStateProgram) => X ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <clearStateProgram> X </clearStateProgram>
         ...
       </transaction>
    requires #isValidForTxnType(ClearStateProgram, TYPE)

  rule [[ getTxnField(I, ConfigAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configAsset> X </configAsset>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAsset, TYPE)

  rule [[ getTxnField(I, ConfigAssetTotal) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configTotal> X </configTotal>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetTotal, TYPE)

  rule [[ getTxnField(I, ConfigAssetDecimals) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configDecimals> X </configDecimals>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetDecimals, TYPE)

  rule [[ getTxnField(I, ConfigAssetDefaultFrozen) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configDefaultFrozen> X </configDefaultFrozen>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetDefaultFrozen, TYPE)

  rule [[ getTxnField(I, ConfigAssetUnitName) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configUnitName> X </configUnitName>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetUnitName, TYPE)

  rule [[ getTxnField(I, ConfigAssetName) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configAssetName> X </configAssetName>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetName, TYPE)

  rule [[ getTxnField(I, ConfigAssetURL) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configAssetURL> X </configAssetURL>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetURL, TYPE)

  rule [[ getTxnField(I, ConfigAssetMetaDataHash) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configMetaDataHash> X </configMetaDataHash>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetMetaDataHash, TYPE)

  rule [[ getTxnField(I, ConfigAssetManager) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configManagerAddr> X </configManagerAddr>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetManager, TYPE)

  rule [[ getTxnField(I, ConfigAssetReserve) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configReserveAddr> X </configReserveAddr>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetReserve, TYPE)

  rule [[ getTxnField(I, ConfigAssetFreeze) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configFreezeAddr> X </configFreezeAddr>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetFreeze, TYPE)

  rule [[ getTxnField(I, ConfigAssetClawback) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <configClawbackAddr> X </configClawbackAddr>
         ...
       </transaction>
    requires #isValidForTxnType(ConfigAssetClawback, TYPE)

  rule [[ getTxnField(I, FreezeAsset) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <freezeAsset> X </freezeAsset>
         ...
       </transaction>
    requires #isValidForTxnType(FreezeAsset, TYPE)

  rule [[ getTxnField(I, FreezeAssetAccount) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <freezeAccount> X </freezeAccount>
         ...
       </transaction>
    requires #isValidForTxnType(FreezeAssetAccount, TYPE)

  rule [[ getTxnField(I, FreezeAssetFrozen) => normalize(X) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <assetFrozen> X </assetFrozen>
         ...
       </transaction>
    requires #isValidForTxnType(FreezeAssetFrozen, TYPE)

  rule [[ getTxnField(I, Applications, J) => normalize(getTValueAt(J, X)) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <foreignApps> X </foreignApps>
         ...
       </transaction>
    requires #isValidForTxnType(Applications, TYPE)
     andBool 0 <=Int J andBool J <Int size(X)

  rule [[ getTxnField(I, Applications) => X ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <foreignApps> X </foreignApps>
         ...
       </transaction>
    requires #isValidForTxnType(Applications, TYPE)

  rule [[ getTxnField(I, Assets, J) => normalize(getTValueAt(J, X)) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <foreignAssets> X </foreignAssets>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)
     andBool 0 <=Int J andBool J <Int size(X)

  rule [[ getTxnField(I, Assets) => X ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <foreignAssets> X </foreignAssets>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)

  rule [[ getTxnField(I, LastLog) => MSG ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <logData> _ MSG:TBytes </logData>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)

  rule [[ getTxnField(I, LastLog) => MSG ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <logData> MSG:TBytes </logData>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)

  rule [[ getTxnField(I, NumLogs) => size(LOGS) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <logData> LOGS </logData>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)

  rule [[ getTxnField(I, Logs, J) => normalize(getTValueAt(J, LOGS)) ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <logData> LOGS </logData>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)

  rule [[ getTxnField(I, Logs) => LOGS ]]
       <transaction>
         <txID> I </txID>
         <typeEnum> TYPE  </typeEnum>
         <logData> LOGS </logData>
         ...
       </transaction>
    requires #isValidForTxnType(Assets, TYPE)
```

*Failure*
```k
  rule getTxnField(_, _:TxnaField)    => .TValueList [owise]
  rule getTxnField(_, _:TxnField    ) => NoTValue    [owise]
  rule getTxnField(_, _, _          ) => NoTValue    [owise]
```

*Other Helper Functions*

```k
  syntax MaybeTValue ::= getAccountAddressAt(Int) [function]
  //--------------------------------------------------------
  rule getAccountAddressAt(I) => getTxnField(getCurrentTxn(), Accounts, I)

  syntax MaybeTValue ::= getForeignAppAt(Int) [function]
  //----------------------------------------------------
  rule getForeignAppAt(I) => getTxnField(getCurrentTxn(), Applications, I)

  syntax MaybeTValue ::= getForeignAssetAt(Int) [function]
  //------------------------------------------------------
  rule getForeignAssetAt(I) => getTxnField(getCurrentTxn(), Assets, I)
```

```k
  syntax TAddressLiteral ::= getAppAddress(Int) [function, functional]
  //---------------------------------------------------------
  rule getAppAddress(APP_ID) => Bytes2TAddressLiteral(b"application" +Bytes String2Bytes(Int2String(APP_ID)))
```

```k
  syntax Bool ::= Int "in_txns" "(" TransactionsCell ")" [function]
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


  syntax Bool ::= #isValidForTxnType(TxnField,     Int) [function]
  syntax Bool ::= #isValidForTxnType(TxnaField,    Int) [function]
  // -------------------------------------------------------------
  // all transaction types
  rule #isValidForTxnType(_:TxnHeaderField, I)    => 1 <=Int I andBool I <=Int 6
  // the pay transaction type
  rule #isValidForTxnType(_:TxnPayField   , I)    => I ==Int 1
  // the keyreg transaction type
  rule #isValidForTxnType(_:TxnKeyregField, I)    => I ==Int 2
  // the config asset transaction type
  rule #isValidForTxnType(_:TxnAcfgField  , I)    => I ==Int 3
  // the asset transfer transaction type
  rule #isValidForTxnType(_:TxnAxferField , I)    => I ==Int 4
  // the asset freeze transaction type
  rule #isValidForTxnType(_:TxnAfrzField  , I)    => I ==Int 5
  // the application call transaction type
  rule #isValidForTxnType(_:TxnApplField  , I)    => I ==Int 6
  rule #isValidForTxnType(_:TxnaField     , I)    => I ==Int 6

endmodule
```
