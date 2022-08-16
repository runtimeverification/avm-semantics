// Compute maximum of two numbers
// the program starts with an arbitrary valid stack which must have at least
// 2 free slots,
// and an arbitrary scratch that must contain 0 |-> X, 1 |-> Y.
module SIMPLE-SPEC
  imports VERIFICATION

  // Compute maximum of two Ints
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
           // // otherwise load Y on top of the stack
           MAX_Y:
           load 1
           END:
         , 0)
         ~> #startExecution()
         => . ...
        </k>
        <pc> 0 => ?_ </pc>
        <program> .Map => ?_ </program>
        <jumped> false </jumped>
        <mode> stateless </mode>
        <version> 2 </version>
        <stack> INITIAL_STACK => ?MAX:Int : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
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

      andBool (0 in_keys(M)) andBool (M[0] ==K X:Int)
      andBool (1 in_keys(M)) andBool (M[1] ==K Y:Int)

      andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
      andBool (?MAX ==Int maxInt(X, Y))

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
         => . ...
        </k>
        <pc> 0 => ?_ </pc>
        <program> .Map => ?_ </program>
        <jumped> false </jumped>
        <mode> stateful </mode>
        <version> 5 </version>
        <stack> INITIAL_STACK => ?SUM:Int : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
        <scratch> M => ?_ </scratch>
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
                  Int2Bytes(ARG1, BE, Unsigned)
                  Int2Bytes(ARG2, BE, Unsigned)
                  Int2Bytes(ARG3, BE, Unsigned)
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
           load 0
           txnas ApplicationArgs
           btoi
           load 1
           
           // Move comparison result to top of stack
           uncover 2

           // Select max value
           select
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
         => . ...
        </k>
        <pc> 0 => ?_ </pc>
        <program> .Map => ?_ </program>
        <jumped> false </jumped>
        <mode> stateful </mode>
        <version> 5 </version>
        <stack> INITIAL_STACK => ?MAX:Int : INITIAL_STACK </stack>
        <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
        <scratch> M => ?_ </scratch>
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
                  Int2Bytes(ARG1, BE, Unsigned)
                  Int2Bytes(ARG2, BE, Unsigned)
                  Int2Bytes(ARG3, BE, Unsigned)
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

      andBool #sizeTStack(INITIAL_STACK) +Int 3 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
      andBool ?MAX ==Int (maxInt(ARG1, maxInt(ARG2, ARG3)))


 endmodule
