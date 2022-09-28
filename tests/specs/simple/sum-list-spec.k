module SUM-LIST-SPEC
  imports VERIFICATION

  // Add up all ApplicationArgs
  claim <k>
         #LoadPgm(
           // Setup loop counter
           int 0
           store 0
           
           // Setup sum variable
           int 0
           store 1

           LOOP_BEGIN:
           // Break out of loop if all AppArgs have been processed
           txn NumAppArgs
           load 0
           ==
           bnz LOOP_END

           // Load ith AppArg
           load 0
           txnas ApplicationArgs
           btoi

           // Add to current sum
           load 1
           +
           store 1

           // Increment loop counter
           load 0
           int 1
           +
           store 0

           b LOOP_BEGIN
           LOOP_END:
           load 1
         , 0)
         ~> #startExecution()
         => .
        </k>
        <pc> 0 => ?_ </pc>
        <program> .Map => ?_ </program>
        <jumped> false </jumped>
        <mode> stateful </mode>
        <version> 5 </version>
        <stack> INITIAL_STACK => ?SUM:Int : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
        <scratch> _ => ?_ </scratch>
        <labels> LL => ?_ </labels>
        <returncode> 4 => ?RETURN_CODE </returncode>
        <returnstatus>
          "Failure - program is stuck" => ?RETURN_STATUS
        </returnstatus>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <appCallTxFields>
              <applicationArgs>
                Int2Bytes(ARG1, BE, Unsigned)
                Int2Bytes(ARG2, BE, Unsigned)
                Int2Bytes(ARG3, BE, Unsigned)
              </applicationArgs>
              ...
            </appCallTxFields>
            <txHeader>
              <typeEnum> @ appl </typeEnum>
              <group> TX_ID </group>
              ...
            </txHeader>
            ...
          </transaction>
          ...
        </transactions>
        <blockchain> _ </blockchain>
    requires  notBool (LOOP_BEGIN in_labels LL)
      andBool (notBool (LOOP_END in_labels LL))
      andBool (LOOP_BEGIN =/=K LOOP_END)

      andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
      andBool ARG1 +Int ARG2 +Int ARG3 <=Int MAX_UINT64
      andBool ARG1 >=Int 0
      andBool ARG2 >=Int 0
      andBool ARG3 >=Int 0
      andBool ARG1 <=Int MAX_UINT64
      andBool ARG2 <=Int MAX_UINT64
      andBool ARG3 <=Int MAX_UINT64
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
      andBool (?SUM ==Int ARG1 +Int ARG2 +Int ARG3)

endmodule
