```k
module ADD-APP-ARGS-SPEC
  imports VERIFICATION
```

```k

claim [main]:
  <kavm>

    <k> #initGlobals() ~> #evalTxGroup() => . </k>

    <returncode>   4                        => 0                                      </returncode>
    <returnstatus> _                        => ?_                                     </returnstatus>

    <transactions>
      <transaction>
        <txID> TX_ID:String </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "appl" </txType>
          <typeEnum> @ appl </typeEnum>
          <groupIdx> 1 </groupIdx>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <applicationArgs> ARG1:Int ARG2:Int </applicationArgs>
            ...
          </appCallTxFields>
        </txnTypeSpecificFields>
        <applyData>
          <txScratch> _ => ?_ </txScratch>
          <logData> .TValueList => ?APP_RESULT </logData>
          <logSize> 0 => ?_ </logSize>
          ...
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
         <globals>
           <groupSize>                 _ => ?_ </groupSize>
           <globalRound>               _ => ?_ </globalRound>
           <latestTimestamp>           _ => ?_ </latestTimestamp>
           <currentApplicationID>      _ => ?_ </currentApplicationID>
           <currentApplicationAddress> _ => ?_ </currentApplicationAddress>
           <creatorAddress>            _ => ?_ </creatorAddress>
         </globals>
         <teal>
           <pc> 0 => ?_ </pc>
           <program> .Map  => ?_ </program>
           <mode> undefined  => ?_ </mode>
           <version> 1  => ?_ </version>
           <stack> .TStack  => ?_ </stack>
           <stacksize> 0  => ?_ </stacksize>
           <jumped> false  => ?_ </jumped>
           <labels> .Map  => ?_ </labels>
           <callStack> .List  => ?_ </callStack>
           <scratch> .Map  => ?_ </scratch>
           <intcblock> .Map  => ?_ </intcblock>
           <bytecblock> .Map  => ?_ </bytecblock>
         </teal>
         <effects> .List => ?_ </effects>
         <lastTxnGroupID> _ => ?_ </lastTxnGroupID>
      </currentTxnExecution>
      <innerTransactions> .List </innerTransactions>
      <activeApps> .Set => ?_ </activeApps>
      <touchedAccounts> .List => ?_ </touchedAccounts>
    </avmExecution>

    <blockchain>
      <accountsMap>
        <account>
          <address> SENDER_ADDRESS:Bytes => ?_ </address>
          <balance> SENDER_BALANCE:Int => ?_ </balance>
          <minBalance> SENDER_MIN_BALANCE:Int </minBalance>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
        <account>
          <address> CREATOR_ADDRESS:Bytes => ?_ </address>
          <balance> _ => ?_ </balance>
          <minBalance> _ => ?_ </minBalance>
          <appsCreated>
            <app>
              <appID> APP_ID </appID>
              <approvalPgmSrc> (
                  txn ApplicationArgs 0
                  txn ApplicationArgs 1
                  +
                  itob
                  log

                  int 1
                  return
                ):TealInputPgm => ?_
              </approvalPgmSrc>
              <clearStatePgmSrc> (int 1 return):TealInputPgm => ?_ </clearStatePgmSrc>
              ...
            </app>
          </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
        <account>
          <address> APP_ADDRESS:Bytes </address>
          <balance> APP_BALANCE:Int => ?_ </balance>
          <minBalance> APP_MIN_BALANCE:Int </minBalance>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
      </accountsMap>
      <appCreator> .Map [APP_ID <- CREATOR_ADDRESS] </appCreator>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
      ...
    </blockchain>

    <tealPrograms> _ </tealPrograms>

  </kavm>

  requires APP_ID >Int 0
   andBool APP_ADDRESS ==K getAppAddressBytes(APP_ID)
   andBool APP_BALANCE >=Int APP_MIN_BALANCE
   andBool CREATOR_ADDRESS =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K CREATOR_ADDRESS
   andBool SENDER_BALANCE >=Int SENDER_MIN_BALANCE
   andBool ARG1 +Int ARG2 <=Int MAX_UINT64

  ensures ?APP_RESULT ==K padLeftBytes(Int2Bytes(ARG1 +Int ARG2, BE, Unsigned), 8, 0)

```

```k
endmodule
```
