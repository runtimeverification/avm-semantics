module MAX-LIST-SPEC
  imports VERIFICATION
  // Find maximum of ApplicationArgs
  claim <k>
         #LoadPgm(
           // Setup loop counter
           int 0
           store 0
           
           // Setup max variable
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

           // Compute max of ith AppArg and current max
           load 1
           >

           // Load ith AppArg and current max to prepare for select
           load 1
           load 0
           txnas ApplicationArgs
           btoi
           
           // Move comparison result to top of stack
           dig 2

           // Select max value
           select
           store 1

           // Increment loop counter
           load 0
           int 1
           +
           store 0

           pop
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
        <stack> INITIAL_STACK => ARG2 : INITIAL_STACK </stack>
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
            <groupID> GROUP_ID </groupID>
            <groupIdx> GROUP_IDX:Int </groupIdx>
            <applicationArgs>
              Int2Bytes(ARG1, BE, Unsigned)
              Int2Bytes(ARG2, BE, Unsigned)
              Int2Bytes(ARG3, BE, Unsigned)
            </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
          ...
        </transactions>
        <currentApplicationID> APP_ID </currentApplicationID>
        <activeApps> (SetItem(APP_ID) => .Set) ... </activeApps>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> GROUP_IDX |-> TX_ID ... </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires  notBool (LOOP_BEGIN in_labels LL)
      andBool (notBool (LOOP_END in_labels LL))
      andBool (LOOP_BEGIN =/=K LOOP_END)
      andBool ARG2 >Int ARG1
      andBool ARG2 >Int ARG3
      andBool ARG1 >Int 0
      andBool ARG2 >Int 0
      andBool ARG3 >Int 0

      andBool MAX_STACK_DEPTH >Int #sizeTStack(INITIAL_STACK) +Int 4 // at least 4 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)

endmodule
