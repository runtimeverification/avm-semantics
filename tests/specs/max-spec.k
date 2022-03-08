// Compute maximum of two numbers
// the program starts with an arbitrary valid stack which must have at least
// 2 free slots,
// and an arbitrary scratch that must contain 0 |-> X, 1 |-> Y.
module MAX-SPEC
  imports VERIFICATION

  claim <k>
         // load Y and X on stack
         load 0 ~> load 1
         // compare X and Y and jump if Y is greter
         ~> >
         ~> bz MAX_Y
         // if X > Y then load X on top pf the stack
         ~> load 0
         ~> b END
         // // otherwise load Y on top of the stack
         ~> MAX_Y:
         ~> load 1
         ~> END:
           => . ...
        </k>
        <mode> stateless </mode>
        <version> 2 </version>
        <stack> .TStack => ?MAX:?_ </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <scratch> M => M </scratch>
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

      andBool (0 in_keys(M)) andBool (M[0] ==K X)
      andBool (1 in_keys(M)) andBool (M[1] ==K Y)

      andBool S +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
      andBool (?MAX ==Int maxInt(X, Y))
 endmodule