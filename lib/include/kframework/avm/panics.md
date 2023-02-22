```k
module AVM-PANIC
  imports STRING
  imports INT
  imports AVM-CONFIGURATION
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
  // Application return types
  syntax Int ::= "SUCCESS" [macro]
               | "ZERO_STACK" [macro]
               | "BAD_STACK" [macro]
               | "INTERNAL_ERROR" [macro]
               | "STUCK" [macro]
               | "INVALID_JSON" [macro]

  // Panic types
  syntax Int ::= "INVALID_OP_FOR_MODE" [macro]
               | "ERR_OPCODE" [macro]
               | "INT_OVERFLOW" [macro]
               | "INT_UNDERFLOW" [macro]
               | "DIV_BY_ZERO" [macro]
               | "BYTES_OVERFLOW" [macro]
               | "TXN_ACCESS_FAILED" [macro]
               | "TXN_INVALID" [macro]
               | "INVALID_SCRATCH_LOC" [macro]
               | "TXN_OUT_OF_BOUNDS" [macro]
               | "FUTURE_TXN" [macro]
               | "INDEX_OUT_OF_BOUNDS" [macro]
               | "ILLEGAL_JUMP" [macro]
               | "ILL_TYPED_STACK" [macro]
               | "LOG_CALLS_EXCEEDED" [macro]
               | "LOG_SIZE_EXCEEDED" [macro]
               | "GLOBAL_BYTES_EXCEEDED" [macro]
               | "GLOBAL_INTS_EXCEEDED" [macro]
               | "LOCAL_BYTES_EXCEEDED" [macro]
               | "LOCAL_INTS_EXCEEDED" [macro]
               | "STACK_OVERFLOW" [macro]
               | "STACK_UNDERFLOW" [macro]
               | "ASSERTION_VIOLATION" [macro]
               | "IMPOSSIBLE_NEGATIVE_NUMBER" [macro]
               | "DUPLICATE_LABEL" [macro]
               | "CALLSTACK_UNDERFLOW" [macro]
               | "CALLSTACK_OVERFLOW" [macro]
               | "INVALID_ARGUMENT" [macro]
               | "ITXN_REENTRY" [macro]
               | "MATH_BYTES_ARG_TOO_LONG" [macro]
               | "INSUFFICIENT_FUNDS" [macro]
               | "KEY_TOO_LARGE" [macro]
               | "BYTE_VALUE_TOO_LARGE" [macro]
               | "KEY_VALUE_TOO_LARGE" [macro]
               | "BOX_TOO_LARGE" [macro]
               | "CHANGED_BOX_SIZE" [macro]
               | "BOX_NOT_FOUND" [macro]
               | "BOX_UNAVAILABLE" [macro]
               | "BOX_WRONG_LENGTH" [macro]
               | "BOX_OUT_OF_BOUNDS" [macro]
               | "BOX_CREATE_EXTERNAL" [macro]
               | "MIN_BALANCE_VIOLATION" [macro]
               | "UNSUPPORTED_TXN_TYPE" [macro]
               | "ASSET_FROZEN" [macro]
               | "ASSET_NOT_OPT_IN" [macro]
               | "UNKNOWN_ADDRESS" [macro]
               | "ASSET_NO_PERMISSION" [macro]
               | "TXN_DEQUE_ERROR" [macro]
               | "ASSET_NOT_FOUND" [macro]
               | "MISSING_APP_CREATOR" [macro]
               | "APP_ALREADY_ACTIVE" [macro]
               | "INSUFFICIENT_ASSET_BALANCE" [macro]
```

The macro production above translate to the following integer panic codes:

```k
  rule SUCCESS                    => 0
  rule ZERO_STACK                 => 1
  rule BAD_STACK                  => 2
  rule INTERNAL_ERROR             => 3
  rule STUCK                      => 4
  rule INVALID_JSON               => 5

  rule INVALID_OP_FOR_MODE        => 6
  rule ERR_OPCODE                 => 7
  rule INT_OVERFLOW               => 8
  rule INT_UNDERFLOW              => 9
  rule DIV_BY_ZERO                => 10
  rule BYTES_OVERFLOW             => 11
  rule TXN_ACCESS_FAILED          => 12
  rule TXN_INVALID                => 13
  rule INVALID_SCRATCH_LOC        => 14
  rule TXN_OUT_OF_BOUNDS          => 15
  rule FUTURE_TXN                 => 16
  rule INDEX_OUT_OF_BOUNDS        => 17
  rule ILLEGAL_JUMP               => 18
  rule ILL_TYPED_STACK            => 19
  rule LOG_CALLS_EXCEEDED         => 20
  rule LOG_SIZE_EXCEEDED          => 21
  rule GLOBAL_BYTES_EXCEEDED      => 22
  rule GLOBAL_INTS_EXCEEDED       => 23
  rule LOCAL_BYTES_EXCEEDED       => 24
  rule LOCAL_INTS_EXCEEDED        => 25
  rule INVALID_ARGUMENT           => 26
  rule STACK_OVERFLOW             => 27
  rule STACK_UNDERFLOW            => 28
  rule ASSERTION_VIOLATION        => 29
  rule DUPLICATE_LABEL            => 30
  rule IMPOSSIBLE_NEGATIVE_NUMBER => 31
  rule CALLSTACK_UNDERFLOW        => 32
  rule CALLSTACK_OVERFLOW         => 33
  rule ITXN_REENTRY               => 34
  rule MATH_BYTES_ARG_TOO_LONG    => 35
  rule INSUFFICIENT_FUNDS         => 36
  rule KEY_TOO_LARGE              => 37
  rule BYTE_VALUE_TOO_LARGE       => 38
  rule KEY_VALUE_TOO_LARGE        => 39
  rule TXN_DEQUE_ERROR            => 40
  rule BOX_TOO_LARGE              => 41
  rule CHANGED_BOX_SIZE           => 42
  rule BOX_NOT_FOUND              => 43
  rule BOX_UNAVAILABLE            => 44
  rule BOX_WRONG_LENGTH           => 45
  rule BOX_OUT_OF_BOUNDS          => 46
  rule BOX_CREATE_EXTERNAL        => 47
  rule MIN_BALANCE_VIOLATION      => 48
  rule UNSUPPORTED_TXN_TYPE       => 49
  rule ASSET_FROZEN               => 50
  rule ASSET_NOT_OPT_IN           => 51
  rule UNKNOWN_ADDRESS            => 52
  rule ASSET_NO_PERMISSION        => 53
  rule ASSET_NOT_FOUND            => 54
  rule MISSING_APP_CREATOR        => 55
  rule APP_ALREADY_ACTIVE         => 56
  rule INSUFFICIENT_ASSET_BALANCE => 57
```

The `returnDesc` function builds the human-readable description of the panic codes:

```k
  syntax String ::= returnDesc(Int) [function]
  //------------------------------------------
  rule returnDesc(INVALID_OP_FOR_MODE)        => "invalid opcode for current execution mode"
  rule returnDesc(ERR_OPCODE)                 => "err opcode encountered"
  rule returnDesc(INT_OVERFLOW)               => "integer overflow"
  rule returnDesc(INT_UNDERFLOW)              => "integer underflow"
  rule returnDesc(DIV_BY_ZERO)                => "division by zero"
  rule returnDesc(BYTES_OVERFLOW)             => "resulting byte array too large"
  rule returnDesc(TXN_ACCESS_FAILED)          => "transaction field access failed"
  rule returnDesc(TXN_INVALID)                => "a transaction is malformed"
  rule returnDesc(INVALID_SCRATCH_LOC)        => "invalid scratch space location"
  rule returnDesc(TXN_OUT_OF_BOUNDS)          => "transaction index out of bounds"
  rule returnDesc(FUTURE_TXN)                 => "tried to access transaction that hasn't executed yet"
  rule returnDesc(INDEX_OUT_OF_BOUNDS)        => "array index out of bounds"
  rule returnDesc(ILLEGAL_JUMP)               => "illegal branch to a non-existing label"
  rule returnDesc(ILL_TYPED_STACK)            => "wrong argument type(s) for opcode"
  rule returnDesc(LOG_CALLS_EXCEEDED)         => "too many log calls in transaction"
  rule returnDesc(LOG_SIZE_EXCEEDED)          => "total size of log calls in transaction is too large"
  rule returnDesc(GLOBAL_BYTES_EXCEEDED)      => "tried to store too many byte values in global storage"
  rule returnDesc(GLOBAL_INTS_EXCEEDED)       => "tried to store too many int values in global storage"
  rule returnDesc(LOCAL_BYTES_EXCEEDED)       => "tried to store too many byte values in local storage"
  rule returnDesc(LOCAL_INTS_EXCEEDED)        => "tried to store too many int values in local storage"
  rule returnDesc(INVALID_ARGUMENT)           => "wrong argument range(s) for opcode"
  rule returnDesc(STACK_OVERFLOW)             => "stack overflow"
  rule returnDesc(STACK_UNDERFLOW)            => "stack underflow"
  rule returnDesc(ASSERTION_VIOLATION)        => "assertion violation"
  rule returnDesc(DUPLICATE_LABEL)            => "duplicate label"
  rule returnDesc(IMPOSSIBLE_NEGATIVE_NUMBER) => "impossible happened: negative number on stack"
  rule returnDesc(CALLSTACK_UNDERFLOW)        => "call stack underflow: illegal retsub"
  rule returnDesc(CALLSTACK_OVERFLOW)         => "call stack overflow: recursion is too deep"
  rule returnDesc(ITXN_REENTRY)               => "application called from itself"
  rule returnDesc(MATH_BYTES_ARG_TOO_LONG)    => "math attempted on large byte-array"
  rule returnDesc(INSUFFICIENT_FUNDS)         => "negative balance reached"
  rule returnDesc(KEY_TOO_LARGE)              => "key is too long"
  rule returnDesc(BYTE_VALUE_TOO_LARGE)       => "tried to store too large of a byte value"
  rule returnDesc(KEY_VALUE_TOO_LARGE)        => "sum of key length and value length is too high"
  rule returnDesc(ASSERTION_VIOLATION)        => "assertion violation"
  rule returnDesc(BOX_TOO_LARGE)              => "tried to create a box which is too large"
  rule returnDesc(CHANGED_BOX_SIZE)           => "called box_create on existing box with a different size"
  rule returnDesc(BOX_NOT_FOUND)              => "tried to access a box name that doesn't exist"
  rule returnDesc(BOX_UNAVAILABLE)            => "tried to access box not referenced in any transaction in this group"
  rule returnDesc(BOX_WRONG_LENGTH)           => "tried to replace a box byte array with one of a different length"
  rule returnDesc(BOX_OUT_OF_BOUNDS)          => "tried to access out of bounds of a box byte array"
  rule returnDesc(BOX_CREATE_EXTERNAL)        => "tried to create a box for which a reference already exists tied to another application"
  rule returnDesc(MIN_BALANCE_VIOLATION)      => "account's balance falls below its allowed minimum balance"
  rule returnDesc(UNSUPPORTED_TXN_TYPE)       => "attempt to execute an unsupported transaction type"
  rule returnDesc(ASSET_FROZEN)               => "attempt to send frozen asset holdings"
  rule returnDesc(ASSET_NOT_OPT_IN)           => "either sender or receiver have not opted into asset"
  rule returnDesc(UNKNOWN_ADDRESS)            => "address is not in the <accountsMap>"
  rule returnDesc(ASSET_NO_PERMISSION)        => "sender does not have permission to modify asset"
  rule returnDesc(TXN_DEQUE_ERROR)            => "txn deque error"
  rule returnDesc(ASSET_NOT_FOUND)            => "tried to modify an asset which hasn't been created"
  rule returnDesc(MISSING_APP_CREATOR)        => "Found app that is missing for <appCreator>"
  rule returnDesc(APP_ALREADY_ACTIVE)         => "attempt to #initApp that already is in <activeApps>"
  rule returnDesc(INSUFFICIENT_ASSET_BALANCE) => "tried to transfer more of an asset than owned"
```

```k
  syntax KItem ::= #panic(Int)
                 | #panic(Int, KItem)
  syntax KItem ::= #stopIfError(KItem)

  rule [panic]:
       <k> #panic(S) => #stopIfError(#panic(S)) ... </k>
       <returncode> _ => S </returncode>
       <returnstatus> _ => returnDesc(S) </returnstatus>

  rule [richPanic]:
       <k> #panic(S, ARGS) => #stopIfError(#panic(S, ARGS)) ... </k>
       <returncode> _ => S </returncode>
       <returnstatus> _ => returnDesc(S) </returnstatus>

  // Leave the testing commands on the K cell
  rule <k> #stopIfError(ERR) ~> X:TestingCommand => X:TestingCommand ~> #stopIfError(ERR) ... </k>

  // Consume the rest of the K cell if the execution terminated with an error
  rule <k> #stopIfError(_) ~> (ITEM:KItem => .K) ... </k>
       <returncode> RETURN_CODE </returncode>
    requires RETURN_CODE =/=Int 0
     andBool notBool(isTestingCommand(ITEM))
```

```k
endmodule
```
