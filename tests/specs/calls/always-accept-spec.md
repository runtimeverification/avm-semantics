```k
module ALWAYS-ACCEPT-SPEC
  imports VERIFICATION
```

```k

claim 
  <kavm>

    <k> #evalTxGroup() => . </k>

    <returncode>   4                        => 0                                      </returncode>
    <returnstatus> _                        => ?_                                     </returnstatus>

    <transactions>
      <transaction>
        <txID> TX_ID:String </txID>
        <txHeader>
          <fee> _ </fee>
          <firstValid> _ </firstValid>
          <lastValid> _ </lastValid>
          <genesisHash> _ </genesisHash>
          <sender> SENDER:Bytes </sender>
          <txType> "appl" </txType>
          <typeEnum> @ appl </typeEnum>
          <groupID> _ </groupID>
          <groupIdx> _ </groupIdx>
          <genesisID> _ </genesisID>
          <lease> _ </lease>
          <note> _ </note>
          <rekeyTo> _ </rekeyTo>
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <accounts> _ </accounts>
            <approvalProgramSrc> _ </approvalProgramSrc>
            <clearStateProgramSrc> _ </clearStateProgramSrc>
            <approvalProgram> _ </approvalProgram>
            <clearStateProgram> _ </clearStateProgram>
            <applicationArgs> _ </applicationArgs>
            <foreignApps> _ </foreignApps>
            <foreignAssets> _ </foreignAssets>
            <boxReferences> _ </boxReferences>
            <globalStateSchema>
              <globalNui> _ </globalNui>
              <globalNbs> _ </globalNbs>
            </globalStateSchema>
            <localStateSchema>
              <localNui> _ </localNui>
              <localNbs> _ </localNbs>
            </localStateSchema>
            <extraProgramPages> _ </extraProgramPages>
          </appCallTxFields>
        </txnTypeSpecificFields>
        <applyData>
          <txScratch> _ => ?_ </txScratch>
          <txConfigAsset> _ => ?_ </txConfigAsset>
          <txApplicationID> _ => ?_ </txApplicationID>
          <log>
            <logData> _ => ?_ </logData>
            <logSize> _ => ?_ </logSize>
          </log>
        </applyData>
        <txnExecutionContext> _ => ?_ </txnExecutionContext>
        <resume> false => true </resume>
      </transaction>
    </transactions>

    <avmExecution>
      <currentTx> TX_ID => ?_ </currentTx>
      <txnDeque>
        <deque> ListItem(TX_ID) => .List </deque>
        <dequeIndexSet> SetItem(TX_ID) => ?_ </dequeIndexSet>
      </txnDeque>
      <currentTxnExecution>
        _ => ?_
      </currentTxnExecution>
      <innerTransactions> _ => ?_ </innerTransactions>
      <activeApps> .Set => ?_ </activeApps>
      <touchedAccounts> .List => ?_ </touchedAccounts>
    </avmExecution>

    <blockchain>
      <accountsMap>
        <account>
          <address> SENDER:Bytes => ?_ </address>
          <balance> BALANCE:Int => ?_ </balance>
          <minBalance> MIN_BALANCE:Int => ?_ </minBalance>
          <round> _ => ?_ </round>
          <preRewards> _ => ?_ </preRewards>
          <rewards> _ => ?_ </rewards>
          <status> _ => ?_ </status>
          <key> _ => ?_ </key>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
        </account>
        <account>
          <address> CREATOR_ADDRESS:Bytes => ?_ </address>
          <balance> _ => ?_ </balance>
          <minBalance> _ => ?_ </minBalance>
          <round> _ => ?_ </round>
          <preRewards> _ => ?_ </preRewards>
          <rewards> _ => ?_ </rewards>
          <status> _ => ?_ </status>
          <key> _ => ?_ </key>
          <appsCreated>
            <app>
              <appID> APP_ID => ?_ </appID>
              <approvalPgmSrc> (int 1 return):TealInputPgm => ?_ </approvalPgmSrc>
              <clearStatePgmSrc> (int 1 return):TealInputPgm => ?_ </clearStatePgmSrc>
              <approvalPgm> _ => ?_ </approvalPgm>
              <clearStatePgm> _ => ?_ </clearStatePgm>
              <globalState>
                <globalNumInts> _ => ?_ </globalNumInts>
                <globalNumBytes> _ => ?_ </globalNumBytes>
                <globalBytes> _ => ?_ </globalBytes>
                <globalInts> _ => ?_ </globalInts>
              </globalState>
              <localState>
                <localNumInts> _ => ?_ </localNumInts>
                <localNumBytes> _ => ?_ </localNumBytes>
              </localState>
              <extraPages> _ => ?_ </extraPages>
            </app>
          </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
        </account>
      </accountsMap>
      <appCreator> .Map [APP_ID <- CREATOR_ADDRESS] </appCreator>
      <assetCreator> _ => ?_ </assetCreator>
      <blocks> _ => ?_ </blocks>
      <blockheight> _ => ?_ </blockheight>
      <nextAssetID> _ => ?_ </nextAssetID>
      <nextAppID> _ => ?_ </nextAppID>
      <nextTxnID> _ => ?_ </nextTxnID>
      <nextGroupID> _ => ?_ </nextGroupID>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
    </blockchain>

    <tealPrograms> _ </tealPrograms>

  </kavm>

  requires APP_ID >Int 0
   andBool BALANCE >=Int MIN_BALANCE
   andBool SENDER =/=K CREATOR_ADDRESS


```

```k
endmodule
```
