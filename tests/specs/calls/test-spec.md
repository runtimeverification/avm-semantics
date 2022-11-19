```k
module TEST-SPEC
  imports VERIFICATION
```

```k

claim
  <kavm>

    <k> gtxna 1 ApplicationArgs 0 => . </k>

    <transactions>
      <transaction>
        <txID> PAY_TX_ID </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "pay" </txType>
          <typeEnum> @ pay </typeEnum>
          <groupID> "2" </groupID>
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
        ...
      </transaction>
      <transaction>
        <txID> TX_ID </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "appl" </txType>
          <typeEnum> @ appl </typeEnum>
          <groupID> "1" </groupID>
          <groupIdx> 1 </groupIdx>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <applicationArgs> 123 456 </applicationArgs>
            ...
          </appCallTxFields>
        </txnTypeSpecificFields>
        ...
      </transaction>
    </transactions>
    <stack> .TStack => 123 : .TStack </stack>
    <stacksize> 0 </stacksize>
    <currentTx> TX_ID </currentTx>
    <txnIndexMap>
      <txnIndexMapGroup>
        <txnIndexMapGroupKey> "1" </txnIndexMapGroupKey>
//        <txnIndexMapGroupValues> .Map [0 <- PAY_TX_ID] [1 <- TX_ID] </txnIndexMapGroupValues>
        <txnIndexMapGroupValues> .Map [1 <- TX_ID] </txnIndexMapGroupValues>
      </txnIndexMapGroup>
    </txnIndexMap>
    ...

  </kavm>

  requires APP_ID >Int 0
   andBool APP_ADDRESS ==K getAppAddressBytes(APP_ID)
   andBool APP_BALANCE >=Int APP_MIN_BALANCE
   andBool CREATOR_ADDRESS =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K CREATOR_ADDRESS
   andBool SENDER_BALANCE >=Int SENDER_MIN_BALANCE
//   andBool PAY_TX_ID =/=K TX_ID
 //  andBool ARG1 +Int ARG2 <=Int MAX_UINT64

//  ensures ?APP_RESULT ==K Int2Bytes(ARG1 +Int ARG2, BE, Unsigned)

```

```k
endmodule
```
