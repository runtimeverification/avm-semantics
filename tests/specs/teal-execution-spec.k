module TEAL-EXECUTION-SPEC
  imports VERIFICATION

  claim <k>
         #LoadPgm(
           // load Y and X on stack
           load 0
           load 1
           // compare X and Y and jump if Y is greter
           >
           bz MAX_Y
           // if X > Y then load X on top pf the stack
           load 0
           b END
           // otherwise load Y on top of the stack
           MAX_Y:
           load 1
           // END:
         , 0)
          // => .
         ~> #startExecution() => .
        </k>
        <pc> 0 => ?_ </pc>
        <program>
          .Map =>
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
        <jumped> false </jumped>
        <stack> INITIAL_STACK => INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) </stacksize>
        <scratch> SCRATCH => SCRATCH </scratch>
        <labels> LL => ?_ </labels>
        <returncode> 4 => ?RETURN_CODE </returncode>
        <returnstatus>
          "Failure - program is stuck" => ?RETURN_STATUS
        </returnstatus>
        <globals> _ </globals>
        <txGroup> _ </txGroup>
        <blockchain> _ </blockchain>
    requires  notBool (MAX_Y in_labels LL)
      andBool (notBool (END in_labels LL))
      andBool (MAX_Y =/=K END)

      andBool (0 in_keys(SCRATCH)) andBool (SCRATCH[0] ==K X:Int)
      andBool (1 in_keys(SCRATCH)) andBool (SCRATCH[1] ==K Y:Int)

      andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
      andBool (?MAX ==Int maxInt(X, Y))

endmodule
