```k
requires "json.md"
requires "avm/blockchain.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-stack.md"
requires "avm/panics.md"
```

Algorand Vitual Machine State
-----------------------------

```k
module AVM-CONFIGURATION
  imports JSON
  imports INT
  imports LIST
  imports SET
  imports ALGO-BLOCKCHAIN
  imports TEAL-INTERPRETER-STATE
  imports TEAL-SYNTAX
  imports ID-SYNTAX

  configuration
    <kavm>
      <k> $PGM:JSON </k>
      <returncode exit=""> 4 </returncode> // the simulator exit code
      <returnstatus> "":String </returnstatus> // the exit status message

      // The transaction group as submitted
      <transactions/>

      // Transaction can create inner transactions, and we chose to treat them similarly to the outer ones.
      // We add them into an execution deque --- inner transactions are executed right after their parent one.
      // Initially, the execution deque will contain the transactions from the submitted group (up to `MaxTxGroupSize`, 16 currently).
      // Outer transactions are referred to by their actual `txID`s. Inner transaction will be assigned "fake" `txID`s,
      // starting from `MaxTxGroupSize` (currently 16).
      <avmExecution>

        // The ID of the transaction currently being executed
        <currentTx> "0" </currentTx>

        // The top of the deque is the currently executing transaction, followed by the next transaction which will be 
        // executed when this one is (completely) finished, etc.
        <txnDeque>
          <deque>         .List </deque>
          <dequeIndexSet> .Set  </dequeIndexSet>
        </txnDeque>

        // The execution context of the current transaction.
        <currentTxnExecution>
          // Globals are mostly immutable during the group execution,
          // besides the application-related fields: CurrentApplicationID, CreatorID
          // and CurrentApplicationAddress
          <globals/>

          // the `<teal>` cell will control evaluation of TEAL code of the current transaction.
          // The semantics of TEAL has *read-only* access to the `<blockchain>` cell
          // and *read-write* access to the `<effects>` cell.
          <teal/>

          // the effects of the transaction. Upon approval of the transaction,
          // its effects will be applied onto the `<blockchain>` cell.
          // TODO: how to represent effects? We need to track changes to accounts, assets and apps.
          <effects> .List </effects>

          // The group ID of the last inner transaction group that was (directly) executed by the current transaction
          <lastTxnGroupID> "" </lastTxnGroupID>

        </currentTxnExecution>

        // The inner transaction group that is currently being constructed using `itxn_begin`, `itxn_next`, `itxn_field`, but
        // which has not yet been executed using `itxn_submit`
        <innerTransactions> .List </innerTransactions>

        // Applications which are currently on the call stack. This cell is needed so that we can check for re-entrant
        // app calls. The `<txnDeque>` is not sufficient for this because it contains transactions that were not yet called but 
        // will be called further back in the call stack. 
        <activeApps> .Set </activeApps>

        // Accounts for which a check will be made at the end of the top-level transaction group to ensure their balance is at 
        // or above their minimum balance
        <touchedAccounts> .List </touchedAccounts>

      </avmExecution>

      // The blockchain state will be incrementally updated after
      // each transaction in the group. If one of the transactions fails,
      // the state will be rolled back to the one before execution the group.
      <blockchain/>

      // A ;-separated concatenation of their source code of TEAL contracts
      // should be supplied as `-cTEAL_PROGRAMS` configuration variuable
      // argument ot `krun`
      <tealPrograms> $TEAL_PROGRAMS:Map </tealPrograms>
    </kavm>

  // Top-level control of the semantics.
  // Defined in `avm-execution.md`
  syntax AVMSimulation
  syntax AlgorandCommand

  // Defined in `avm-testing.md`
  syntax TestingCommand

  // Control of transaction evaluation
  // Defined in `avm-execution.md`
  syntax TxnCommand
```

## Lookup for kavm configuration

```k
  //--------------------------------------
  rule [[ getCurrentTxn() => I ]]
    <currentTx> I </currentTx>
```

```k
endmodule
```

TEAL Interpreter State
----------------------

```k
module TEAL-INTERPRETER-STATE
  imports TEAL-SYNTAX
  imports TEAL-STACK
  imports MAP
  imports INT
  imports LIST
```

Stateless and stateful TEAL programs are parameterized by slightly different
input state. All TEAL programs have access to the:

-   stack
-   call stack
-   scratch memory
-   containing transaction and transaction group
-   globals

Stateless TEAL programs additionally have access to the:

-   logic signature arguments

Stateful TEAL programs additionally have access to:

-   local and global application state
-   application state for foreign applications
-   asset parameters for foreign assets

Note: our configuration also contains a return code. However, this return code
is _not_ a return code in the sense of TEAL; rather, it is a return code in the
sense of POSIX process semantics. This return code is used by the test harness
to determine when a test has succeeded/failed.

To perform jumps, we maintain a map of labels to their program addresses and a `<jumped>` cell that tracks if the last executed opcode triggered a jump.

```k
  syntax LabelMap ::= Map

  syntax Bool ::= Label "in_labels" LabelMap [function]
  // --------------------------------------------------
  rule L in_labels LL => L in_keys(LL)

  syntax Int ::= getLabelAddress(Label) [function]
  // ---------------------------------------------
  rule [[ getLabelAddress(L) => {LL[L]}:>Int ]]
       <labels> LL </labels>
```

A subroutine call in TEAL is essentially an unconditional branch to a label, which also saves the program address of the next instruction on the call stack.

```k
  syntax CallStack ::= List
```

```k
  configuration
    <teal>
      <pc> 0 </pc>
      <program> .Map </program>
      <mode> undefined </mode>
      <version> 1 </version>               // the default TEAL version is 1 if no #pragma version is specified
      <stack> .TStack </stack>             // stores UInt64 or Bytes
      <stacksize> 0 </stacksize>           // current stack size
      <jumped> false </jumped>             // `true` if the previous opcode triggered a jump
      <labels> .Map </labels>              // a map from labels seen so far in a program
                                           // to their corresponding program addresses, Label |-> Int
      <callStack> .List </callStack>
      <scratch> .Map </scratch>            // Int |-> TValue
      <intcblock> .Map </intcblock>        // (currently not used)
      <bytecblock> .Map </bytecblock>      // (currently not used)
    </teal>

  syntax TealExecutionOp ::= #initApp( Int )
                           | #initSmartSig()
                           | #restoreContext()
                           | #initContext()
                           | #startExecution()
                           | #finalizeExecution()
                           | #fetchOpcode()
                           | #incrementPC()
endmodule
```
