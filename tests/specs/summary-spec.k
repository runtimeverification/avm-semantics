module SUMMARY-SPEC
    imports VERIFICATION

// Start with claim of no-op:
//    claim <k> #pragma version 2
//              #pragma mode stateless
//              int 18446744073709551615
//              int 18446744073709551615
//              mulw
//              store 0
//              store 1
//              int 18446744073709551615
//              int 1
//              mulw
//              store 2
//              store 3
//              int 1
//              int 1
//              mulw
//              store 4
//              store 5
//              int 1
//           => . </k>
//          <stacksize> SS </stacksize>
//      requires SS <=Int 10

// From counterexample, prove summary:
// Note that you can not read `SS +Int 2 <Int MAX_STACK_DEPTH` off directly from the counterexample.
    claim <k> 
              #pragma version 2
              #pragma mode stateless
              int 18446744073709551615
              int 18446744073709551615
              mulw
              store 0
              store 1
              int 18446744073709551615
              int 1
              mulw
              store 2
              store 3
              int 1
              int 1
              mulw
              store 4
              store 5
              int 1
            ~> #startExecution()
           => . </k>
          <mode> stateless </mode>
          <pc> 0 => ?_ </pc>
          <program> .Map => ?_ </program>
          <jumped> false </jumped>
          <version> 2 </version>
          <stacksize> 1 => 1 +Int 1 </stacksize>
          <stack> .TStack => 1 : .TStack </stack>
          <scratch> SCRATCH
                 => SCRATCH [ 0 <- 1                    ]
                            [ 1 <- 18446744073709551614 ]
                            [ 2 <- 18446744073709551615 ]
                            [ 3 <- 0                    ]
                            [ 4 <- 1                    ]
                            [ 5 <- 0                    ]
          </scratch>
          <returncode> 4 => ?_ </returncode>
          <returnstatus>
            "Failure - program is stuck" => ?_
          </returnstatus>

endmodule
