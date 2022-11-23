```k
module TEST-SPEC
  imports VERIFICATION
```

```k

claim
  <kavm>

    <k> testAbc(b"def", 321) => . </k>

    <returncode>   4                        => 0                                      </returncode>
    <returnstatus> "Failure - AVM is stuck" => "Success - transaction group accepted" </returnstatus>
    <paniccode>    0                        => 0                                      </paniccode>
    <panicstatus>  ""                       => ""                                     </panicstatus>

    <transactions>
      <transaction>
        <txID> PAY_TX_ID:String </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "pay" </txType>
          <typeEnum> @ pay </typeEnum>
          <groupID> GROUP_ID:String </groupID>
          <groupIdx> 0 </groupIdx>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <payTxFields>
            <receiver>  APP_ADDRESS </receiver>
            <amount> AMOUNT </amount>
            <closeRemainderTo> NoTValue </closeRemainderTo>
          </payTxFields>
        </txnTypeSpecificFields>
        <applyData>
          <txScratch> _ => ?_ </txScratch>
          <logData> .TValueList => ?_ </logData>
          <logSize> 0 => ?_ </logSize>
          ...
        </applyData>
        <txnExecutionContext> _ => ?_ </txnExecutionContext>
        <resume> false => true </resume>
      </transaction>
      <transaction>
        <txID> APPL_TX_ID:String </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "appl" </txType>
          <typeEnum> @ appl </typeEnum>
          <groupID> GROUP_ID:String </groupID>
          <groupIdx> 1 </groupIdx>
          <firstValid> FV:Int </firstValid>
          <lastValid> LV:Int </lastValid>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <applicationArgs> FUNCTION_NAME:Bytes Int2Bytes(AMOUNT:Int, BE, Unsigned) </applicationArgs>
            <foreignAssets> ASSET_ID </foreignAssets>
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
      <currentTx> _ => ?_ </currentTx>
      <txnDeque>
        <deque> ListItem(PAY_TX_ID) ListItem(APPL_TX_ID) => .List </deque>
        <dequeIndexSet> SetItem(PAY_TX_ID) SetItem(APPL_TX_ID) => ?_ </dequeIndexSet>
      </txnDeque>
      <currentTxnExecution>
         <globals>
           <groupSize>                 _ => ?_ </groupSize>
           <currentApplicationID>      _ => ?_ </currentApplicationID>
           <currentApplicationAddress> _ => ?_ </currentApplicationAddress>
           <creatorAddress>            _ => ?_ </creatorAddress>
           ...
         </globals>
         <teal>    _ => ?_ </teal>
         <effects> .List </effects>
         <lastTxnGroupID> _ => ?_ </lastTxnGroupID>
      </currentTxnExecution>
      <innerTransactions> .List </innerTransactions>
      <activeApps> .Set => ?_ </activeApps>
      <touchedAccounts> .Set => ?_ </touchedAccounts>
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
          <assetsOptedIn>
            <optInAsset>
              <optInAssetID>      ASSET_ID </optInAssetID>
              <optInAssetBalance> ASSET_BAL </optInAssetBalance>
              <optInAssetFrozen>  0 </optInAssetFrozen>
            </optInAsset>
          </assetsOptedIn>
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
txn NumAppArgs
int 1
>=
assert

txna ApplicationArgs 0
byte "buy"
==
bnz BUY

BUY:

  global GroupSize
  int 2
  ==
  assert

  gtxn 0 TypeEnum 
  int pay
  ==
  assert

  gtxn 0 Amount 
  txna ApplicationArgs 1
  btoi
  ==
  assert

  gtxn 0 Receiver
  global CurrentApplicationAddress
  ==
  assert

  txn NumAssets
  int 1
  ==
  assert

  txn Assets 0
  itob
  app_global_get
  txna ApplicationArgs 1
  btoi
  *
  store 0

  itxn_begin

    int axfer
    itxn_field TypeEnum

    txn Sender
    itxn_field AssetReceiver

    load 0
    itxn_field AssetAmount

    txn Assets 0
    itxn_field XferAsset

  itxn_submit

  b END

END:

  int 1
  return
                ):TealInputPgm => ?_
              </approvalPgmSrc>
              <globalState>
                <globalNumInts>   1             </globalNumInts>
                <globalNumBytes>  0             </globalNumBytes>
                <globalBytes>     .Map             </globalBytes>
                <globalInts>      .Map  [Int2Bytes(ASSET_ID, BE, Unsigned) <- SCALING_FACTOR:Int]                </globalInts>
              </globalState>
              <clearStatePgmSrc> (int 1 return):TealInputPgm => ?_ </clearStatePgmSrc>
              ...
            </app>
          </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated>
            <asset>
              <assetID>            ASSET_ID:Int </assetID>
              <assetTotal>         ASSET_TOTAL:Int </assetTotal>
              <assetDefaultFrozen> 0 </assetDefaultFrozen>
              <assetManagerAddr>   CREATOR_ADDRESS </assetManagerAddr>
              ...
            </asset>
          </assetsCreated>
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
          <assetsOptedIn>
            <optInAsset>
              <optInAssetID>      ASSET_ID </optInAssetID>
              <optInAssetBalance> ASSET_BAL </optInAssetBalance>
              <optInAssetFrozen>  0 </optInAssetFrozen>
            </optInAsset>
          </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
      </accountsMap>
      <appCreator> .Map [APP_ID <- CREATOR_ADDRESS] </appCreator>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
      <nextTxnID> NEXT_TXN_ID </nextTxnID>
      <nextGroupID> NEXT_GROUP_ID </nextGroupID>
      ...
    </blockchain>

    <tealPrograms> _ </tealPrograms>

  </kavm>

  requires APP_ID >Int 0
   andBool APP_ID ==Int 321
   andBool SENDER_ADDRESS ==K b"abc"
   andBool CREATOR_ADDRESS ==K b"def"
   andBool APP_ADDRESS ==K getAppAddressBytes(APP_ID)
   andBool APP_BALANCE >=Int APP_MIN_BALANCE
   andBool CREATOR_ADDRESS =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K CREATOR_ADDRESS
   andBool SENDER_BALANCE >=Int SENDER_MIN_BALANCE
   andBool END =/=K BUY
   andBool SENDER_BALANCE -Int AMOUNT >=Int SENDER_MIN_BALANCE
   andBool SENDER_MIN_BALANCE >=Int 0
   andBool FUNCTION_NAME ==K b"buy"
   andBool PAY_TX_ID =/=K APPL_TX_ID
   andBool SCALING_FACTOR *Int AMOUNT <=Int MAX_UINT64
   andBool SCALING_FACTOR >Int 0
   andBool Int2String(NEXT_TXN_ID) =/=String APPL_TX_ID
   andBool Int2String(NEXT_TXN_ID) =/=String PAY_TX_ID
   andBool APP_BALANCE -Int (SCALING_FACTOR *Int AMONUT) >=Int 0

   andBool Int2String(NEXT_GROUP_ID +Int 1) =/=String GROUP_ID
//   andBool Int2String(NEXT_GROUP_ID) =/=String GROUP_ID
```

```k
endmodule
```
