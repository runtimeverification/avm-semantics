```k
requires "avm/teal/teal-syntax.md"
requires "avm/avm-configuration.md"
requires "avm/avm-limits.md"

module TEAL-EXECUTION
  imports AVM-CONFIGURATION
  imports AVM-LIMITS
  imports TEAL-OPCODES
  imports TEAL-SYNTAX
  imports TEAL-STACK
  imports TEAL-INTERPRETER-STATE
```

TEAL Interpreter Initialization
-------------------------------

Before starting the execution of a TEAL progam, the `<teal>` cell needs to be (re-)initialised, since
there may be some remaining artefacts of the previous transaction's TEAL.

```k
  rule <k> #cleanUp() => .K ... </k>
       <teal>
         _ => (
           <pc> 0 </pc>
           <program> .Map </program>
           <mode> stateless </mode>
           <version> 4 </version>
           <stack> .TStack </stack>
           <stacksize> 0 </stacksize>
           <jumped> false </jumped>
           <labels> .Map </labels>
           <callStack> .List </callStack>
           <scratch> .Map </scratch>
           <intcblock> .Map </intcblock>
           <bytecblock> .Map </bytecblock>
         )
       </teal>
```

### Program initialization

The parsed TEAL pragmas and program are initially supplied on the `<k>` cell as
`TealPragmas` and `TealInputPgm`.

Pragmas are applied directly, and then the `#LoadPgm` performs program pre-processing:

* the program is transformed into a `Map` from program addresses to opcodes and stored
  into the `<program>` cell;
* every opcode is checked to be valid for the current execution mode and
  `panic(INVALID_OP_FOR_MODE)` is triggered accordingly;
* the labels are collected and stored into the `<labels>` cell as keys, with their program
  addresses as values;
* if a label is encountered twice, the `panic(DUPLICATE_LABEL)` computation is triggered.

```k
  rule <k> Rs:TealPragmas P:TealPgm => Rs ~> #LoadPgm(P, 0) ... </k>
  rule <k> R:TealPragma Rs:TealPragmas => R ~> Rs ... </k>

  rule <k> #pragma mode M:TealMode => .K ...  </k>
       <mode> _ => M </mode>

  rule <k> #pragma version V => . ... </k>
       <version> _ => V </version>

  // legacy pseudo pragma for setting up current transaction --- now noop
  rule <k> #pragma txn _ => .K ... </k>

  // Load the teal program into the `<progam>` cell (program memory)
  syntax KItem ::= #LoadPgm(TealPgm, Int)
  // ----------------------------------
  rule <k> #LoadPgm( Op Pgm, PC ) => #LoadPgm( Pgm, PC +Int 1 ) ... </k>
       <mode> Mode </mode>
       <program> PGM => PGM[PC <- Op] </program>
    requires #ValidOpForMode( Mode, Op )
     andBool (notBool isLabelCode(Op))

  rule <k> #LoadPgm( (L:) Pgm, PC ) => #LoadPgm( Pgm, PC +Int 1 ) ... </k>
       <program> PGM => PGM[PC <- (L:)] </program>
       <labels> LL => LL[L <- PC] </labels>
    requires notBool (L in_labels LL)

  rule <k> #LoadPgm( (L:) _, _ ) => panic(DUPLICATE_LABEL) ... </k>
       <labels> LL </labels>
    requires L in_labels LL

  rule <k> #LoadPgm( Op _, _) => panic(INVALID_OP_FOR_MODE) ... </k>
       <mode> Mode </mode>
    requires notBool #ValidOpForMode( Mode, Op )

  rule <k> #LoadPgm( Op, PC) => .K ... </k>
       <mode> Mode </mode>
       <program> PGM => PGM[PC <- Op] </program>
    requires #ValidOpForMode( Mode, Op )
     andBool (notBool isLabelCode(Op))

  rule <k> #LoadPgm( (L:) , PC ) => .K ... </k>
       <program> PGM => PGM[PC <- (L:)] </program>
       <labels> LL => LL[L <- PC] </labels>
    requires notBool (L in_labels LL)

  rule <k> #LoadPgm( (L:) , _ ) => panic(DUPLICATE_LABEL) ... </k>
       <labels> LL </labels>
    requires L in_labels LL

  rule <k> #LoadPgm( Op, _) => panic(INVALID_OP_FOR_MODE) ... </k>
       <mode> Mode </mode>
    requires notBool #ValidOpForMode( Mode, Op )

  syntax Bool ::= #ValidOpForMode( TealMode, TealOpCodeOrLabel ) [function]
  // ----------------------------------------------------------------------
  rule #ValidOpForMode( _M:TealMode, _O:PseudoOpCode ) => true
  rule #ValidOpForMode( _M:TealMode, _O:OpCode       ) => true
  rule #ValidOpForMode( _M:TealMode, _L:LabelCode    ) => true
  rule #ValidOpForMode( stateless,   _O:SigOpCode    ) => true
  rule #ValidOpForMode( stateful,    _O:AppOpCode    ) => true
  rule #ValidOpForMode( stateful,    _O:SigOpCode    ) => false
  rule #ValidOpForMode( stateless,   _O:AppOpCode    ) => false
```

TEAL Execution
--------------

### Starting execution

```k
  rule <k> #startExecution() => #fetchOpcode() ... </k>
```

### Opcode fetching

The `#fetchOpcode()` operation will lookup the next opcode from program memory and
put it into the `<k>` cell for execution.

```k
  rule <k> #fetchOpcode() => PGM[PC] ~> #incrementPC() ... </k>
       <pc> PC </pc>
       <program> PGM </program>
   requires isValidProgamAddress(PC)

  syntax Bool ::= isValidProgamAddress(Int) [function]
  // -------------------------------------------------
  rule [[ isValidProgamAddress(ADDR) => true ]]
       <program> PGM </program>
    requires 0 <=Int ADDR andBool ADDR <Int size(PGM)
  rule isValidProgamAddress(_) => false [owise]
```

If there the PC goes one step beyond the program address space, it means that the execution is finished:

```k
  rule <k> #fetchOpcode() => #finalizeExecution() ... </k>
       <pc> PC </pc>
       <program> PGM </program>
   requires PC ==Int size(PGM)
```

### Program counter

Program counter is incremented after every opcode execution, unless its a branch.
The semantics of branches updates the PC on its own.

```k
  rule <k> #incrementPC() => #fetchOpcode() ... </k>
       <pc> PC => PC +Int #if JUMPED #then 0 #else 1 #fi </pc>
       <jumped> JUMPED => false </jumped>
```

TEAL Interpreter Finalization
-----------------------------

After evaluating the TEAL code of an application call or a logic signature we need to finalize
the `<teal>` cell, depending on the evaluation result: whether the transaction has been accepted or
rejected.

Possible return codes:

- 4 - program got stuck (No valid program is expected to terminate returning this code)
- 3 - program panicked
- 2 - program terminated with bad stack (non-singleton or singleton byte-array stack)
- 1 - program terminated with failure (zero-valued singleton stack)
- 0 - program terminated with success (positive-valued singleton stack)

Note: For stateless teal, failure means rejecting the transaction. For stateful
teal, failure means undoing changes made to the state (for more details, see
[this article](https://developer.algorand.org/docs/features/asc1/).)
```k
  rule <k> #finalizeExecution() => .K ... </k>
       <stack> I : .TStack </stack>
       <stacksize> SIZE </stacksize>
       <returncode> 4 => 0 </returncode>
       <returnstatus> _ => "Success - positive-valued singleton stack" </returnstatus>
    requires I >Int 0 andBool SIZE ==Int 1

  rule <k> #finalizeExecution() => .K </k>
       <stack> I : .TStack => I : .TStack </stack>
       <stacksize> _ </stacksize>
       <returncode> 4 => 1 </returncode>
       <returnstatus> _ => "Failure - zero-valued singleton stack" </returnstatus>
    requires I <=Int 0

  rule <k> #finalizeExecution() => .K </k>
       <stack> _ </stack>
       <stacksize> SIZE </stacksize>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - stack size greater than 1" </returnstatus>
    requires SIZE >Int 1

  rule <k> #finalizeExecution() => .K </k>
       <stack> .TStack </stack>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - empty stack" </returnstatus>

  rule <k> #finalizeExecution() => .K </k>
       <stack> (_:Bytes) : .TStack </stack>
       <stacksize> _ </stacksize>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - singleton stack with byte array type" </returnstatus>
```

```k
  syntax KItem ::= #saveScratch()
  //-----------------------------
  rule <k> #saveScratch() => . ...</k>
       <currentTx> TXN_ID </currentTx>
       <transaction>
         <txID> TXN_ID </txID>
         <txScratch> _ => SCRATCH </txScratch>
         ...
       </transaction>
       <scratch> SCRATCH </scratch>
```

Panic Behaviors
---------------

A TEAL program may panic for one of the following reasons:

1.  Opcode used not valid for current mode of execution

2.  The `err` opcode is encountered

3.  Integer overflow

4.  Integer underflow

5.  Division by zero

6.  `concat`: The resulting byte array is too large (> 4k bytes)

7.  `txn`/`txna`: Accessing a transaction field failed
    - The transaction does not exist
    - The transaction type is invalid
    - The requested field is invalid for the transaction type
    - Indexing an array field out of bounds
    - Access to a field of transaction beyond `GroupIndex` is requested via `gaid(s)` or `gload(s)` opcode

8.  An opcode attempts to write to or read from an invalid scratch space
    location

9.  An opcode attempts to use an invalid index for a byte array (`substring*`,
    `arg`)

10. branching beyond the end of the program or brcnhing backwards (`b*`)

11. An input in the stack is not of the expected type

12. An input in the stack is not in the expected range, for example not `0` or `1` for `setbit`

13. An opcode attempts to push to a full stack

14. An opcode attempts to pop from an empty stack

15. An assertion is violated, i.e. the asserted expression evaluates to zero

16. A negative number is supplied on stack. That panic behavior is impossible in concrete
    execution, but is helpful in some symbolic execution scenarios.

17. A subroutine call attempt with a full call stack, or a subroutine return with an empty one.

18. Math attempted on a byte-array larger than `MAX_BYTE_MATH_SIZE`.

Other reasons for panic behavior, which do not apply to this specification
of TEAL, include:

19. `global`: Wrong global field (rejected by our TEAL parser; syntax
    definition disallows invalid fields)

20. `txn/txna`: wrong type argument (rejected by our TEAL parser; syntax
    definition disallows invalid fields)

21. Loading constants from beyond the bytecblock or the intcblock of the
    program (This is specific to post-assembly TEAL and does not apply to our
    abstract semantics)

22. Invalid opcode (rejected by our TEAL parser; syntax definition disallows
    invalid opcodes)

Panic conditions (1 -- 18 above) are captured by the `panic` computation,
which carries a message describing the reason for panicking and sets the
return code to 3 (see return codes below).

```k
  // Panic types
  syntax String ::= "INVALID_OP_FOR_MODE"        [macro]
  syntax String ::= "ERR_OPCODE"                 [macro]
  syntax String ::= "INT_OVERFLOW"               [macro]
  syntax String ::= "INT_UNDERFLOW"              [macro]
  syntax String ::= "DIV_BY_ZERO"                [macro]
  syntax String ::= "BYTES_OVERFLOW"             [macro]
  syntax String ::= "TXN_ACCESS_FAILED"          [macro]
  syntax String ::= "INVALID_SCRATCH_LOC"        [macro]
  syntax String ::= "TXN_OUT_OF_BOUNDS"          [macro]
  syntax String ::= "FUTURE_TXN"                 [macro]
  syntax String ::= "INDEX_OUT_OF_BOUNDS"        [macro]
  syntax String ::= "ILLEGAL_JUMP"               [macro]
  syntax String ::= "ILL_TYPED_STACK"            [macro]
  syntax String ::= "LOG_CALLS_EXCEEDED"         [macro]
  syntax String ::= "LOG_SIZE_EXCEEDED"          [macro]
  syntax String ::= "GLOBAL_BYTES_EXCEEDED"      [macro]
  syntax String ::= "GLOBAL_INTS_EXCEEDED"       [macro]
  syntax String ::= "LOCAL_BYTES_EXCEEDED"       [macro]
  syntax String ::= "LOCAL_INTS_EXCEEDED"        [macro]
  syntax String ::= "STACK_OVERFLOW"             [macro]
  syntax String ::= "STACK_UNDERFLOW"            [macro]
  syntax String ::= "ASSERTION_VIOLATION"        [macro]
  syntax String ::= "IMPOSSIBLE_NEGATIVE_NUMBER" [macro]
  syntax String ::= "DUPLICATE_LABEL"            [macro]
  syntax String ::= "CALLSTACK_UNDERFLOW"        [macro]
  syntax String ::= "CALLSTACK_OVERFLOW"         [macro]
  syntax String ::= "INVALID_ARGUMENT"           [macro]
  syntax String ::= "MATH_BYTES_ARG_TOO_LONG"    [macro]
  //----------------------------------------------------
  rule INVALID_OP_FOR_MODE => "invalid opcode for current execution mode"
  rule ERR_OPCODE          => "err opcode encountered"
  rule INT_OVERFLOW        => "integer overflow"
  rule INT_UNDERFLOW       => "integer underflow"
  rule DIV_BY_ZERO         => "division by zero"
  rule BYTES_OVERFLOW      => "resulting byte array too large"
  rule TXN_ACCESS_FAILED   => "transaction field access failed"
  rule INVALID_SCRATCH_LOC => "invalid scratch space location"
  rule TXN_OUT_OF_BOUNDS   => "transaction index out of bounds"
  rule FUTURE_TXN          => "tried to access transaction that hasn't executed yet"
  rule INDEX_OUT_OF_BOUNDS => "array index out of bounds"
  rule ILLEGAL_JUMP        => "illegal branch to a non-existing label"
  rule ILL_TYPED_STACK     => "wrong argument type(s) for opcode"
  rule LOG_CALLS_EXCEEDED  => "too many log calls in transaction"
  rule LOG_SIZE_EXCEEDED   => "total size of log calls in transaction is too large"
  rule GLOBAL_BYTES_EXCEEDED => "tried to store too many byte values in global storage"
  rule GLOBAL_INTS_EXCEEDED => "tried to store too many int values in global storage"
  rule LOCAL_BYTES_EXCEEDED => "tried to store too many byte values in local storage"
  rule LOCAL_INTS_EXCEEDED => "tried to store too many int values in local storage"
  rule INVALID_ARGUMENT    => "wrong argument range(s) for opcode"
  rule STACK_OVERFLOW      => "stack overflow"
  rule STACK_UNDERFLOW     => "stack underflow"
  rule ASSERTION_VIOLATION => "assertion violation"
  rule DUPLICATE_LABEL     => "duplicate label"
  rule IMPOSSIBLE_NEGATIVE_NUMBER => "impossible happened: negative number on stack"
  rule CALLSTACK_UNDERFLOW => "call stack underflow: illegal retsub"
  rule CALLSTACK_OVERFLOW  => "call stack overflow: recursion is too deep"
  rule MATH_BYTES_ARG_TOO_LONG => "math attempted on large byte-array"
  rule ASSERTION_VIOLATION => "assertion violation"
  //--------------------------------------------------------------------------------

  syntax KItem ::= panic(String)
  // ---------------------------
  rule <k> panic(S) ~> _ => .K </k>
       <returncode> 4 => 3 </returncode>
       <returnstatus> _ => "Failure - panic: " +String S </returnstatus>
```

```k
endmodule
```
