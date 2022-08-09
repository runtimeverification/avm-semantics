// Compute maximum of two numbers
// the program starts with an arbitrary valid stack which must have at least
// 2 free slots,
// and an arbitrary scratch that must contain 0 |-> X, 1 |-> Y.
module SIMPLE-SPEC
  imports VERIFICATION

//   claim <k> sumTo(3, 5) => 12 </k>
//   claim <k> sumTo(2, 7) => 27 </k>

  // Compute maximum of two Ints
//   claim <k>
//          #LoadPgm(
//            // load Y and X on stack
//            load 0
//            load 1
//            // compare X and Y and jump if Y is greter
//            >
//            bz MAX_Y
//            // if X > Y then load X on top pf the stack
//            load 0
//            b END
//            // // otherwise load Y on top of the stack
//            MAX_Y:
//            load 1
//            END:
//          , 0)
//          ~> #startExecution()
//          => .
//         </k>
//         <pc> 0 => ?_ </pc>
//         <program> .Map => ?_ </program>
//         <jumped> false </jumped>
//         <mode> stateless </mode>
//         <version> 2 </version>
//         <stack> INITIAL_STACK => ?MAX:Int : INITIAL_STACK </stack>
//         <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
//         <scratch> M => M </scratch>
//         <labels> LL => ?_ </labels>
//         <returncode> 4 => ?RETURN_CODE </returncode>
//         <returnstatus>
//           "Failure - program is stuck" => ?RETURN_STATUS
//         </returnstatus>
//         <globals> _ </globals>
//         <txGroup> _ </txGroup>
//         <blockchain> _ </blockchain>
//     requires  notBool (MAX_Y in_labels LL)
//       andBool (notBool (END in_labels LL))
//       andBool (MAX_Y =/=K END)
// 
//       andBool (0 in_keys(M)) andBool (M[0] ==K X:Int)
//       andBool (1 in_keys(M)) andBool (M[1] ==K Y:Int)
// 
//       andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
//     ensures   (?RETURN_CODE =/=Int 3)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
//       andBool (?MAX ==Int maxInt(X, Y))
// 
//   // Add up all ApplicationArgs
//   claim <k>
//          #LoadPgm(
//            // Setup loop counter
//            int 0
//            store 0
//            
//            // Setup sum variable
//            int 0
//            store 1
// 
//            LOOP_BEGIN:
//            // Break out of loop if all AppArgs have been processed
//            txn NumAppArgs
//            load 0
//            ==
//            bnz LOOP_END
// 
//            // Load ith AppArg
//            load 0
//            txnas ApplicationArgs
//            btoi
// 
//            // Add to current sum
//            load 1
//            +
//            store 1
// 
//            // Increment loop counter
//            load 0
//            int 1
//            +
//            store 0
// 
//            b LOOP_BEGIN
//            LOOP_END:
//            load 1
//          , 0)
//          ~> #startExecution()
//          => .
//         </k>
//         <pc> 0 => ?_ </pc>
//         <program> .Map => ?_ </program>
//         <jumped> false </jumped>
//         <mode> stateful </mode>
//         <version> 5 </version>
//         <stack> INITIAL_STACK => ?SUM:Int : INITIAL_STACK </stack>
//         <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
//         <scratch> _ => ?_ </scratch>
//         <labels> LL => ?_ </labels>
//         <returncode> 4 => ?RETURN_CODE </returncode>
//         <returnstatus>
//           "Failure - program is stuck" => ?RETURN_STATUS
//         </returnstatus>
//         <globals> _ </globals>
//         <txGroup> 
//           <txGroupID> _ </txGroupID>
//           <currentTx> TX_ID </currentTx>
//           <transactions>
//             <transaction>
//               <txID> TX_ID </txID>
//               <appCallTxFields>
//                 <applicationArgs>
//                   Int2Bytes(ARG1, BE, Unsigned)
//                   Int2Bytes(ARG2, BE, Unsigned)
//                   Int2Bytes(ARG3, BE, Unsigned)
//                 </applicationArgs>
//                 ...
//               </appCallTxFields>
//               <txHeader>
//                 <typeEnum> @ appl </typeEnum>
//                 ...
//               </txHeader>
//               ...
//             </transaction>
//             ...
//           </transactions>
//         </txGroup>
//         <blockchain> _ </blockchain>
//     requires  notBool (LOOP_BEGIN in_labels LL)
//       andBool (notBool (LOOP_END in_labels LL))
//       andBool (LOOP_BEGIN =/=K LOOP_END)
// 
//       andBool #sizeTStack(INITIAL_STACK) +Int 2 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
//       andBool ARG1 +Int ARG2 +Int ARG3 <=Int MAX_UINT64
//       andBool ARG1 >=Int 0
//       andBool ARG2 >=Int 0
//       andBool ARG3 >=Int 0
//       andBool ARG1 <=Int MAX_UINT64
//       andBool ARG2 <=Int MAX_UINT64
//       andBool ARG3 <=Int MAX_UINT64
//     ensures   (?RETURN_CODE =/=Int 3)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
//       andBool (?SUM ==Int ARG1 +Int ARG2 +Int ARG3)
// 
//   // Find maximum of ApplicationArgs
//   claim <k>
//          #LoadPgm(
//            // Setup loop counter
//            int 0
//            store 0
//            
//            // Setup max variable
//            int 0
//            store 1
// 
//            LOOP_BEGIN:
//            // Break out of loop if all AppArgs have been processed
//            txn NumAppArgs
//            load 0
//            ==
//            bnz LOOP_END
// 
//            // Load ith AppArg
//            load 0
//            txnas ApplicationArgs
//            btoi
// 
//            // Compute max of ith AppArg and current max
//            load 1
//            >
// 
//            // Load ith AppArg and current max to prepare for select
//            load 1
//            load 0
//            txnas ApplicationArgs
//            btoi
//            
//            // Move comparison result to top of stack
//            dig 2
// 
//            // Select max value
//            select
//            store 1
// 
//            // Increment loop counter
//            load 0
//            int 1
//            +
//            store 0
// 
//            pop
//            b LOOP_BEGIN
//            LOOP_END:
//            load 1
//          , 0)
//          ~> #startExecution()
//          => .
//         </k>
//         <pc> 0 => ?_ </pc>
//         <program> .Map => ?_ </program>
//         <jumped> false </jumped>
//         <mode> stateful </mode>
//         <version> 5 </version>
//         <stack> INITIAL_STACK => ARG2 : INITIAL_STACK </stack>
//         <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
//         <scratch> _ => ?_ </scratch>
//         <labels> LL => ?_ </labels>
//         <returncode> 4 => ?RETURN_CODE </returncode>
//         <returnstatus>
//           "Failure - program is stuck" => ?RETURN_STATUS
//         </returnstatus>
//         <globals> _ </globals>
//         <txGroup> 
//           <txGroupID> _ </txGroupID>
//           <currentTx> TX_ID </currentTx>
//           <transactions>
//             <transaction>
//               <txID> TX_ID </txID>
//               <appCallTxFields>
//                 <applicationArgs>
//                   Int2Bytes(ARG1, BE, Unsigned)
//                   Int2Bytes(ARG2, BE, Unsigned)
//                   Int2Bytes(ARG3, BE, Unsigned)
//                 </applicationArgs>
//                 ...
//               </appCallTxFields>
//               <txHeader>
//                 <typeEnum> @ appl </typeEnum>
//                 ...
//               </txHeader>
//               ...
//             </transaction>
//             ...
//           </transactions>
//         </txGroup>
//         <blockchain> _ </blockchain>
//     requires  notBool (LOOP_BEGIN in_labels LL)
//       andBool (notBool (LOOP_END in_labels LL))
//       andBool (LOOP_BEGIN =/=K LOOP_END)
//       andBool ARG2 >Int ARG1
//       andBool ARG2 >Int ARG3
//       andBool ARG1 >Int 0
//       andBool ARG2 >Int 0
//       andBool ARG3 >Int 0
// 
//       andBool #sizeTStack(INITIAL_STACK) +Int 4 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
//     ensures   (?RETURN_CODE =/=Int 3)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)


  // Sum to N
//   claim <k>
//          #LoadPgm(
//            // i = 1
//            int 1
//            store 0
//            
//            // sum = 0
//            int 0
//            store 1
// 
//            LOOP_BEGIN:
// 
//            // sum = sum + i
//            load 1
//            load 0
//            +
//            store 1
// 
//            // if(i == N) break
//            txna ApplicationArgs 0
//            btoi
//            load 0
//            ==
//            bnz LOOP_END
// 
//            // i++
//            load 0
//            int 1
//            +
//            store 0
// 
//            b LOOP_BEGIN
// 
//            LOOP_END:
//            load 1
//          , 0)
//          ~> #startExecution()
//          => .
//         </k>
//         <pc> 0 => ?_ </pc>
//         <program> .Map => ?_ </program>
//         <jumped> false </jumped>
//         <mode> stateful </mode>
//         <version> 5 </version>
//         <stack> INITIAL_STACK => ?SUM : INITIAL_STACK </stack>
//         <stacksize> #sizeTStack(INITIAL_STACK) => #sizeTStack(INITIAL_STACK) +Int 1 </stacksize>
//         <scratch> _ => ?_ </scratch>
//         <labels> LL => ?_ </labels>
//         <returncode> 4 => ?RETURN_CODE </returncode>
//         <returnstatus>
//           "Failure - program is stuck" => ?RETURN_STATUS
//         </returnstatus>
//         <globals> _ </globals>
//         <txGroup> 
//           <txGroupID> _ </txGroupID>
//           <currentTx> TX_ID </currentTx>
//           <transactions>
//             <transaction>
//               <txID> TX_ID </txID>
//               <appCallTxFields>
//                 <applicationArgs>
//                   Int2Bytes(N, BE, Unsigned)
//                 </applicationArgs>
//                 ...
//               </appCallTxFields>
//               <txHeader>
//                 <typeEnum> @ appl </typeEnum>
//                 ...
//               </txHeader>
//               ...
//             </transaction>
//             ...
//           </transactions>
//         </txGroup>
//         <blockchain> _ </blockchain>
//     requires  notBool (LOOP_BEGIN in_labels LL)
//       andBool (notBool (LOOP_END in_labels LL))
//       andBool (LOOP_BEGIN =/=K LOOP_END)
// 
//       andBool #sizeTStack(INITIAL_STACK) +Int 4 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
//     ensures   (?RETURN_CODE =/=Int 3)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
//       andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)
//       andBool (?SUM ==Int (N *Int (N +Int 1)) /Int 2)

  claim
    <k>
      (bnz LOOP_END:Label ~> #incrementPC ( )) => .
    </k>
    <returncode>
      4 => ?RETURN_CODE
    </returncode>
    <returnstatus>
      "Failure - program is stuck" => ?RETURN_STATUS
    </returnstatus>
    <txGroup>
      ...
      <currentTx>
        TX_ID:Int
      </currentTx>
      <transactions>
        <transaction>
          <txID>
            TX_ID:Int
          </txID>
          <txHeader>
            ...
            <typeEnum>
              6
            </typeEnum>
          </txHeader>
          <appCallTxFields>
            ...
            <applicationArgs>
              Int2Bytes ( N:Int , BE , Unsigned )
            </applicationArgs>
          </appCallTxFields>
        </transaction>
        ...
      </transactions>
    </txGroup>
    <currentTxnExecution>
      ...
      <teal>
        ...
        <pc>
          13 => 21
        </pc>
        <program>
          0 |-> int 1
          1 |-> store 0
          2 |-> int 0
          3 |-> store 1
          4 |-> LOOP_BEGIN:Label :
          5 |-> load 1
          6 |-> load 0
          7 |-> +
          8 |-> store 1
          9 |-> txna ApplicationArgs 0
          10 |-> btoi
          11 |-> load 0
          12 |-> ==
          13 |-> bnz LOOP_END:Label
          14 |-> load 0
          15 |-> int 1
          16 |-> +
          17 |-> store 0
          18 |-> b LOOP_BEGIN:Label
          19 |-> LOOP_END:Label :
          20 |-> load 1
        </program>
        <mode>
          stateful
        </mode>
        <version>
          5
        </version>
        <stack>
          bool2Int ( N:Int ==Int 1 ) : INITIAL_STACK:TStack
        </stack>
        <stacksize>
          #sizeTStack ( INITIAL_STACK:TStack , 0 ) +Int 1
        </stacksize>
        <jumped>
          false
        </jumped>
        <labels>
          LL:Map [ LOOP_BEGIN:Label <- 4 ] [ LOOP_END:Label <- 19 ]
        </labels>
        <scratch>
          _Gen2:Map [ 0 <- (I:Int => N) ] [ 1 <- (SUM:Int => ((N *Int (N +Int 1)) /Int 2))]
        </scratch>
      </teal>
    </currentTxnExecution>
    requires  notBool (LOOP_BEGIN in_labels LL)
      andBool (notBool (LOOP_END in_labels LL))
      andBool (LOOP_BEGIN =/=K LOOP_END)
      andBool #sizeTStack(INITIAL_STACK) +Int 4 <Int MAX_STACK_DEPTH // at least 2 more free slots on stack
//      andBool ((N *Int (N +Int 1)) /Int 2 <=Int MAX_UINT64)
//      andBool (I <=Int N)
//      andBool (I +Int N <=Int MAX_UINT64)
//      andBool SUM ==Int ((I *Int (I +Int 1)) /Int 2)
//       andBool I +Int 1 <=Int MAX_UINT64

      andBool sumTo(N) <=Int MAX_UINT64
      andBool SUM +Int sumTo(I +Int 1, N) <=Int MAX_UINT64
      andBool SUM >=Int 0

      andBool sumTo(I) <=Int MAX_UINT64
      andBool I <=Int N
      andBool I >=Int 1

    ensures   (?RETURN_CODE =/=Int 3)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String ILLEGAL_JUMP)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_OVERFLOW)
      andBool (?RETURN_STATUS =/=String "Failure - panic: " +String STACK_UNDERFLOW)

 endmodule
