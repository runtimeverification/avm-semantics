```k
requires "avm/teal/teal-syntax.md"
requires "avm/avm-configuration.md"
requires "avm/avm-limits.md"
requires "avm/panics.md"

module TEAL-EXECUTION
  imports AVM-CONFIGURATION
  imports AVM-LIMITS
  imports TEAL-OPCODES
  imports TEAL-SYNTAX
  imports TEAL-STACK
  imports TEAL-TYPES
  imports TEAL-INTERPRETER-STATE
  imports AVM-PANIC
```

TEAL Interpreter Initialization
-------------------------------

Before starting the execution of a TEAL progam, the `<teal>` cell needs to be (re-)initialised, since
there may be some remaining artefacts of the previous transaction's TEAL.

```k
  rule <k> #initContext() => . ...</k>
       <currentTxnExecution>
         <teal>
         _ => (
           <pc> 0 </pc>
           <program> .Map </program>
           <mode> undefined </mode>
           <version> 1 </version>
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
         ...
       </currentTxnExecution>

  rule <k> #restoreContext() => . ...</k>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <txnExecutionContext> (<currentTxnExecution> C </currentTxnExecution> => .K) ... </txnExecutionContext>
         ...
       </transaction>
       <currentTxnExecution> _ => C </currentTxnExecution>
```

```k
  rule <k> #initApp(APP_ID) => . ...</k>
       <currentApplicationID> _ => APP_ID </currentApplicationID>
       <currentApplicationAddress> _ => getAppAddressBytes(APP_ID) </currentApplicationAddress>
       <creatorAddress> _ => {AC [ APP_ID ]}:>Bytes </creatorAddress>
       <activeApps> (.Set => SetItem(APP_ID)) REST </activeApps>
       <lastTxnGroupID> _ => "" </lastTxnGroupID>
       <mode> _ => stateful </mode>
       <appCreator> AC </appCreator>
    requires notBool(APP_ID in REST) andBool (APP_ID in_keys(AC))

  rule <k> #initApp(APP_ID) => #panic(APP_ALREADY_ACTIVE) ... </k>
       <activeApps> REST </activeApps>
    requires APP_ID in REST

  rule <k> #initApp(APP_ID) => #panic(MISSING_APP_CREATOR) ... </k>
       <appCreator> AC </appCreator>
    requires notBool(APP_ID in_keys(AC))
```

```k
  rule <k> #initSmartSig() => .K ... </k>
       <mode> _ => stateless </mode>
```

### Program initialization

The parsed TEAL pragmas and program are supplied to the `#loadInputPgm` rule that:

* calls the `loadProgramCell` function to transform the program into a `Map` from program counter values to opcodes
* calls the `loadLabelsCell` to extract the `Map` from labels to program counter values
* if pragmas are supplied, loads the version; otherwise sets the version to `PARAM_DEFAULT_TEAL_VERSION`
* panics if duplicate labels were discovered by the `loadLabelsCell` function

```k
  syntax AlgorandCommand ::= #loadInputPgm( TealInputPgm )
  //------------------------------------------------------

  rule <k> #loadInputPgm(PRAGMAS:TealPragmas PGM:TealPgm) => #checkDuplicateLabels() ...</k>
       <program> _ => loadProgramCell(PGM, 0)      </program>
       <labels>  _ => loadLabelsCell(PGM, 0, .Map) </labels>
       <version> _ => loadVersionCell(PRAGMAS)     </version>

  rule <k> #loadInputPgm(PGM:TealPgm) => #checkDuplicateLabels() ...</k>
       <program> _ => loadProgramCell(PGM, 0)      </program>
       <labels>  _ => loadLabelsCell(PGM, 0, .Map) </labels>
       <version> _ => PARAM_DEFAULT_TEAL_VERSION   </version>
```

```k
  syntax AlgorandCommand ::= #checkDuplicateLabels()
  //------------------------------------------------
  rule <k> #checkDuplicateLabels() => #panic(DUPLICATE_LABEL) ... </k>
       <labels> duplicate-label </labels>
  rule <k> #checkDuplicateLabels() => . ... </k> [owise]
```


```k
  syntax Int ::= loadVersionCell(TealPragmas) [function, total]
  //-----------------------------------------------------------
  rule loadVersionCell ( #pragma version V _:TealPragmas ) => V
  rule loadVersionCell ( #pragma version V               ) => V
```

```k
  syntax Map ::= loadProgramCell(TealPgm, Int) [function, total]
  //------------------------------------------------------------
  rule loadProgramCell( Op:TealOpCodeOrLabel Pgm, PC ) => ((PC |-> Op) loadProgramCell( Pgm, PC +Int 1 ))
  rule loadProgramCell( Op:TealOpCodeOrLabel,     PC ) =>  (PC |-> Op)
```

```k
  syntax LoadLabelsResult ::= loadLabelsCell(TealPgm, Int, Map)  [function, total]
  //------------------------------------------------------------------------------
  rule loadLabelsCell( Op:TealOpCodeOrLabel Pgm, PC, LABELS ) => loadLabelsCell( Pgm, PC +Int 1, LABELS ) requires notBool(isLabelCode(Op))
  rule loadLabelsCell( Op:TealOpCodeOrLabel,     _ , LABELS ) => LABELS                                   requires notBool(isLabelCode(Op))
  rule loadLabelsCell( (L:):LabelCode Pgm, PC, LABELS ) => (loadLabelsCell( Pgm, PC +Int 1, (LABELS (L |-> PC)))) requires notBool (L in_labels LABELS)
  rule loadLabelsCell( (L:):LabelCode,     PC, LABELS ) => (L |-> PC) LABELS requires notBool (L in_labels LABELS)
  rule loadLabelsCell( (L:):LabelCode _,   _,  LABELS ) => duplicate-label requires (L in_labels LABELS)
  rule loadLabelsCell( (L:):LabelCode,     _,  LABELS ) => duplicate-label requires (L in_labels LABELS)
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
  rule <k> #fetchOpcode() => PGM[PC] ~> #incrementPC() ~> #fetchOpcode() ... </k>
       <pc> PC </pc>
       <program> PGM </program>
       <returncode> STATUS_CODE </returncode>
   requires isValidProgamAddress(PC) andBool STATUS_CODE ==Int 4

  rule <k> #fetchOpcode() => .K ... </k>
       <pc> PC </pc>
       <returncode> STATUS_CODE </returncode>
   requires STATUS_CODE =/=Int 4
   andBool isValidProgamAddress(PC)

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
  rule <k> #incrementPC() => . ... </k>
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
  syntax KItem ::= #deactivateApp()
  syntax KItem ::= #checkStack()

  rule <k> #finalizeExecution() => #saveScratch() ~> #deactivateApp() ~> #checkStack() ... </k>
    requires getTxnField(getCurrentTxn(), TypeEnum) ==K (@ appl)

  rule <k> #deactivateApp() => . ... </k>
       <currentApplicationID> APP_ID </currentApplicationID>
       <activeApps> (SetItem(APP_ID) => .Set) ... </activeApps>

  rule <k> #checkStack() => .K ... </k>
       <stack> I : .TStack </stack>
       <stacksize> SIZE </stacksize>
    requires I >Int 0 andBool SIZE ==Int 1

  rule <k> #checkStack() => #panic(ZERO_STACK) ... </k>
       <stack> I : .TStack </stack>
       <stacksize> _ </stacksize>
    requires 0 >=Int I

  rule <k> #checkStack() => #panic(BAD_STACK) ... </k>
       <stack> _ </stack>
       <stacksize> SIZE </stacksize>
    requires SIZE >Int 1

  rule <k> #checkStack() => #panic(BAD_STACK) ... </k>
       <stack> .TStack </stack>

  rule <k> #checkStack() => #panic(BAD_STACK) ... </k>
       <stack> (_:Bytes) : .TStack </stack>
       <stacksize> _ </stacksize>
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


```k
endmodule
```
