module TEAL-EXECUTION-SPEC
  imports VERIFICATION

  claim <k> #startExecution() => . </k>
        <pc> 0 => ?_ </pc>
        <program>
          0 |-> load 0
          1 |-> load 1
          2 |-> >
          3 |-> bz MAX_Y
          4 |-> load 0
          5 |-> b END
          6 |-> MAX_Y:
          7 |-> load 1
          8 |-> END:
        </program>
        <currentTx> "0" </currentTx>
        <transactions>
          ((<transaction>
            <txID> "0" </txID>
            <txType> "appl" </txType>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>)=> ?_)
        </transactions>
        <labels>
          END |-> 8
          MAX_Y |-> 6
        </labels>
        <jumped> false </jumped>
        <stack> INITIAL_STACK => ?MAX : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => 1 +Int #sizeTStack(INITIAL_STACK) </stacksize>
        <scratch> SCRATCH => SCRATCH </scratch>
        <currentApplicationID> APP_ID:Int </currentApplicationID>
        <activeApps> (SetItem(APP_ID) => .Set) </activeApps>
        <returncode> 4 => ?RETURN_CODE </returncode>
        <returnstatus>
          "Failure - program is stuck" => ?RETURN_STATUS
        </returnstatus>
        <blockchain> _ </blockchain>
    requires  notBool (MAX_Y in_labels LL)
      andBool (notBool (END in_labels LL))
      andBool (MAX_Y =/=K END)

      andBool (0 in_keys(SCRATCH)) andBool (SCRATCH[0] ==K X:Int)
      andBool (1 in_keys(SCRATCH)) andBool (SCRATCH[1] ==K Y:Int)

      andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String returnDesc(ILLEGAL_JUMP))
      andBool (?RETURN_STATUS =/=String returnDesc(STACK_OVERFLOW))
      andBool (?RETURN_STATUS =/=String returnDesc(STACK_UNDERFLOW))
      andBool (?MAX ==Int maxInt(X, Y))

endmodule
