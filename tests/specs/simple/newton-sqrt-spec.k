module NEWTON-SQRT-SPEC
  imports VERIFICATION

  claim <k>
         #LoadPgm(
           // x = N
           // n = N
           txna ApplicationArgs 0
           btoi
           dup
           store 0
           store 1

           LOOP_BEGIN:

           // root = (x + (n / x)) / 2
           load 1
           load 0
           /
           load 0
           +
           int 2
           /
           store 2

           // if(root == x) break (solution converged) 
           load 2
           load 0
           ==
           bnz LOOP_END

           // x = root
           load 2
           store 0

           b LOOP_BEGIN

           LOOP_END:
           load 0
         , 0)
         ~> #startExecution()
         => .
        </k>
        <pc> 0 => ?_ </pc>
        <program> .Map => ?_ </program>
        <jumped> false </jumped>
        <mode> stateful </mode>
        <version> 5 </version>
        <stack> INITIAL_STACK => ?SQRT : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
        <scratch> _ => ?_ </scratch>
        <labels> LL => ?_ </labels>
        <returncode> 4 => ?RETURN_CODE </returncode>
        <returnstatus>
          "Failure - program is stuck" => ?RETURN_STATUS
        </returnstatus>
        <globals> _ </globals>
        <txGroup> 
          <txGroupID> _ </txGroupID>
          <currentTx> TX_ID </currentTx>
          <transactions>
            <transaction>
              <txID> TX_ID </txID>
              <appCallTxFields>
                <applicationArgs>
                  Int2Bytes(N, BE, Unsigned)
                </applicationArgs>
                ...
              </appCallTxFields>
              <txHeader>
                <typeEnum> @ appl </typeEnum>
                ...
              </txHeader>
              ...
            </transaction>
            ...
          </transactions>
        </txGroup>
        <blockchain> _ </blockchain>
    requires  notBool (LOOP_BEGIN in_labels LL)
      andBool (notBool (LOOP_END in_labels LL))
      andBool (LOOP_BEGIN =/=K LOOP_END)

      andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
      andBool N >Int 0
      andBool N +Int 1 <=Int MAX_UINT64
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
//      andBool (?SQRT ^Int 2) <=Int N
//      andBool ((?SQRT +Int 1) ^Int 2) >Int N

endmodule
