module PAY-SPEC
  imports VERIFICATION

claim [pay]:
  <kavm>
    <k> #evalFirstTx() => .K ... </k>

    <returncode>   4 => 0   </returncode>
    <returnstatus> _ => ?_ </returnstatus>

    <transactions>
       <transaction>
          <txID> "0" </txID>
          <txHeader>
              <groupID>  "GROUP0"        </groupID>
              <groupIdx> 0               </groupIdx>
              <sender>   SENDER_ADDRESS  </sender>
              <txType>   "pay"           </txType>
              <typeEnum> @ pay           </typeEnum>
              <rekeyTo>  PARAM_ZERO_ADDR </rekeyTo>
              ...
          </txHeader>
          <txnTypeSpecificFields>
            <payTxFields>
                <receiver>         RECEIVER_ADDRESS </receiver>
                <amount>           PAYMENT_AMOUNT   </amount>
                <closeRemainderTo> PARAM_ZERO_ADDR  </closeRemainderTo>
            </payTxFields>
            ...
          </txnTypeSpecificFields>
          <resume> false </resume>
          ...
        </transaction>
    </transactions>

    <avmExecution>
      <currentTx>       _ => ?_                </currentTx>
      <deque>           ListItem("0") => .List </deque>
      <dequeIndexSet>   SetItem("0")           </dequeIndexSet>
      <touchedAccounts> .List => ?_            </touchedAccounts>
      ...
    </avmExecution>

    <blockchain>
      <accountsMap>
          (account(SENDER_ADDRESS, SENDER_BALANCE, SENDER_MIN_BALANCE)
           =>
           account(SENDER_ADDRESS, ?SENDER_BALANCE_POST, SENDER_MIN_BALANCE))
          (account(RECEIVER_ADDRESS, RECEIVER_BALANCE, RECEIVER_MIN_BALANCE)
           =>
           account(RECEIVER_ADDRESS, ?RECEIVER_BALANCE_POST, RECEIVER_MIN_BALANCE))
      </accountsMap>
      <txnIndexMap>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "GROUP0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> 0 |-> "0" </txnIndexMapGroupValues>
        </txnIndexMapGroup>
      </txnIndexMap>
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

   // payment amount is small
   andBool #range(0 < PAYMENT_AMOUNT <= 10000)

   // spec-specific requirements on variables
   andBool SENDER_MIN_BALANCE   >=Int PARAM_MIN_BALANCE
   andBool RECEIVER_MIN_BALANCE >=Int PARAM_MIN_BALANCE
   andBool SENDER_BALANCE       >=Int SENDER_MIN_BALANCE +Int PAYMENT_AMOUNT
   andBool RECEIVER_BALANCE     >=Int RECEIVER_MIN_BALANCE
   andBool #rangeUInt(64, RECEIVER_BALANCE +Int PAYMENT_AMOUNT)

   // Addresses are unique
   andBool SENDER_ADDRESS =/=K RECEIVER_ADDRESS

 ensures true
   andBool #rangeUInt(64, ?SENDER_BALANCE_POST)
   andBool #rangeUInt(64, ?RECEIVER_BALANCE_POST)
   andBool ?SENDER_BALANCE_POST   >=Int SENDER_MIN_BALANCE
   andBool ?SENDER_BALANCE_POST   ==Int SENDER_BALANCE   -Int PAYMENT_AMOUNT
   andBool ?RECEIVER_BALANCE_POST ==Int RECEIVER_BALANCE +Int PAYMENT_AMOUNT
endmodule
