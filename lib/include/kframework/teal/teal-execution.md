```k
requires "../common/teal-syntax.md"
requires "./teal-limits.md"
requires "../avm/avm-configuration.md"

module TEAL-EXECUTION
  imports AVM-CONFIGURATION
  imports TEAL-OPCODES
  imports TEAL-SYNTAX
  imports TEAL-STACK
  imports TEAL-LIMITS
  imports TEAL-INTERPRETER-STATE
```

### Preparing for executing a TEAL progam

Before starting the execution of a TEAL progam, the `<teal>` cell needs to be (re-)initialised, since
there may be some remaining artefacts of the previous transaction's TEAL.

TODO: how to be less verbose and just init the cell with default values from the configuration definition?

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

### Starting execution

```k
  rule <k> #startExecution() => #fetchOpcode() ... </k>
```

### Finalizing execution

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
  syntax KItem ::= #halt()

//  rule <k> #fetchOpcode() => #finalizeExecution() ... </k>
  rule <k> #fetchOpcode() => #halt() ... </k>
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

```k
endmodule
```
