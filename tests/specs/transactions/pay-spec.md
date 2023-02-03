```k
module PAY-SPEC
  imports VERIFICATION
```

```k

claim
  <kavm>

    <k> #evalTxGroup() => . </k>

    <returncode>   4 => 0   </returncode>
    <returnstatus> _ => ?_ </returnstatus>

    <transactions>
      paymentTxn("0", "GROUP0", 0, SENDER_ADDRESS, RECEIVER_ADDRESS, PAYMENT_AMOUNT) => ?_
    </transactions>

    <avmExecution>
      <currentTx> _ => ?_ </currentTx>
      <deque>         ListItem("0") => ?_ </deque>
      <dequeIndexSet> SetItem("0") </dequeIndexSet>
      <touchedAccounts> .List => ?_ </touchedAccounts>
      <globals> _ => ?_ </globals>
      <teal>    _ => ?_  </teal>
      <effects> .List => ?_ </effects>
      <lastTxnGroupID> _ => ?_ </lastTxnGroupID>
      ...
    </avmExecution>

    <blockchain>
      <accountsMap>
          (account(SENDER_ADDRESS, SENDER_BALANCE) => account(SENDER_ADDRESS, ?SENDER_BALANCE_POST))
          (account(RECEIVER_ADDRESS, RECEIVER_BALANCE) => account(RECEIVER_ADDRESS, ?RECEIVER_BALANCE_POST))
//        <account>
//          <address> SENDER_ADDRESS:Bytes </address>
//          <balance> SENDER_BALANCE:Int => ?SENDER_BALANCE_POST </balance>
//          <minBalance> SENDER_MIN_BALANCE:Int </minBalance>
//          <appsCreated> .Bag </appsCreated>
//          <appsOptedIn> .Bag </appsOptedIn>
//          <assetsCreated> .Bag </assetsCreated>
//          <assetsOptedIn> .Bag </assetsOptedIn>
//          <boxes> .Bag </boxes>
//          ...
//        </account>
//        <account>
//          <address> RECEIVER_ADDRESS:Bytes </address>
//          <balance> RECEIVER_BALANCE:Int => ?RECEIVER_BALANCE_POST </balance>
//          <minBalance> RECEIVER_MIN_BALANCE:Int </minBalance>
//          <appsCreated> .Bag </appsCreated>
//          <appsOptedIn> .Bag </appsOptedIn>
//          <assetsCreated> .Bag </assetsCreated>
//          <assetsOptedIn> .Bag </assetsOptedIn>
//          <boxes> .Bag </boxes>
//          ...
//        </account>
      </accountsMap>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
      <nextTxnID> 1 => ?_ </nextTxnID>
      <nextGroupID> 1 => ?_ </nextGroupID>
      ...
    </blockchain>

    ...

  </kavm>

  requires true
  
   // variables are in range
   andBool #rangeUInt(64, SENDER_MIN_BALANCE)
   andBool #rangeUInt(64, RECEIVER_MIN_BALANCE)
   andBool #rangeUInt(64, SENDER_BALANCE)
   andBool #rangeUInt(64, RECEIVER_BALANCE)
   andBool #rangeUInt(64, PAYMENT_AMOUNT)

   // spec-specific requirements on variables
   andBool SENDER_MIN_BALANCE >=Int PARAM_MIN_BALANCE
   andBool RECEIVER_MIN_BALANCE >=Int PARAM_MIN_BALANCE
   andBool SENDER_BALANCE   >=Int SENDER_MIN_BALANCE +Int PAYMENT_AMOUNT
   andBool RECEIVER_BALANCE >=Int RECEIVER_MIN_BALANCE
   andBool #rangeUInt(64, RECEIVER_BALANCE +Int PAYMENT_AMOUNT)

   // Addresses are unique
   andBool SENDER_ADDRESS =/=K RECEIVER_ADDRESS

 ensures true
   andBool #rangeUInt(64, ?SENDER_BALANCE_POST)
   andBool #rangeUInt(64, ?RECEIVER_BALANCE_POST)
   andBool ?SENDER_BALANCE_POST   >=Int SENDER_MIN_BALANCE
   andBool ?SENDER_BALANCE_POST   ==Int SENDER_BALANCE   -Int PAYMENT_AMOUNT
   andBool ?RECEIVER_BALANCE_POST ==Int RECEIVER_BALANCE +Int PAYMENT_AMOUNT
```

```k
endmodule
```
