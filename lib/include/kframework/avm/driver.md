```k
requires "blockchain-k-plugin/krypto.md"

requires "../common/teal-syntax.md"
requires "../common/blockchain.md"
requires "../common/args.md"
requires "teal-stack.md"
requires "env-init.md"
```

TEAL Interpreter State
======================

```k
module TEAL-INTERPRETER-STATE
  imports ALGO-BLOCKCHAIN
  imports TXN-ARGS
  imports TEAL-SYNTAX
  imports TEAL-STACK
```

Stateless and stateful TEAL programs are parameterized by slightly different
input state. All TEAL programs have access to the:

-   stack
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

We also maintain a list of labels seen so far in a program to check for
illegal backward jumps.

```k
  syntax LabelList ::= List{Label, ""}

  syntax Bool ::= Label "in_labels" LabelList [function]
  // --------------------------------------------
  rule L in_labels (L  _     ) => true
  rule L in_labels (L' LL    ) => L in_labels LL requires L =/=K L'
  rule _ in_labels .LabelList => false
```

```k
  configuration
    <teal>
      <globals/>
      <txGroup/>
      <blockchain/>
      <args/>
      <driver>
        <k> initGlobals
         ~> initArgs
         ~> initTxnGroup
         ~> initBlockchain
         ~> $PGM:TealInputPgm </k>           // TODO: init* items for testing only
        <mode> stateless </mode>             // for testing purposes
        <version> 2 </version>               // the default TEAL version is 2
        <stack> .TStack </stack>                  // stores UInt64 or Bytes
        <stacksize> 0 </stacksize>           // current stack size
        <labels> .LabelList </labels>        // a list of labels seen so far in a program
        <scratch> .Map </scratch>            // Int |-> TValue
        <intcblock> .Map </intcblock>        // (currently not used)
        <bytecblock> .Map </bytecblock>      // (currently not used)
        <returncode exit=""> 4 </returncode> // the program exit code
        <returnstatus>                       // the program exit status message
          "Failure - program is stuck"
        </returnstatus>
      </driver>
    </teal>
```

### Environment Initializer Declaration

Note: these definitions can be found in the `TEAL-ENVIRONMENT-INITIALIZATION`
module.

```k
  syntax KItem ::= "initGlobals"
                 | "initArgs"
                 | "initTxnGroup"
                 | "initBlockchain"
```

```k
endmodule
```

TEAL Interpreter Syntax
=======================

The TEAL interpreter is parameterized by several constants which define total
program and cost. We define those constants here.

```k
module TEAL-DRIVER-SYNTAX
  imports TEAL-SYNTAX

  // Size limits
  syntax Int ::= "MAX_STACK_DEPTH"   [macro]
  syntax Int ::= "MAX_SCRATCH_SIZE"  [macro]
  syntax Int ::= "LogicSigMaxSize"   [macro]
  syntax Int ::= "LogicSigMaxCost"   [macro]
  syntax Int ::= "MaxAppProgramLen"  [macro]
  syntax Int ::= "MaxAppProgramCost" [macro]
  syntax Int ::= "MAX_BYTEARRAY_LEN" [macro]
  // ---------------------------------------
  rule MAX_STACK_DEPTH   => 1000
  rule MAX_SCRATCH_SIZE  => 256
  rule LogicSigMaxSize   => 1000
  rule LogicSigMaxCost   => 20000
  rule MaxAppProgramLen  => 1024
  rule MaxAppProgramCost => 700
  rule MAX_BYTEARRAY_LEN => 4096
endmodule
```

TEAL Interpreter Definition
===========================

```k
module TEAL-DRIVER
  imports TEAL-INTERPRETER-STATE
  imports TEAL-ENVIRONMENT-INITIALIZATION
  imports TEAL-DRIVER-SYNTAX
  imports TEAL-STACK
  imports KRYPTO
```

TEAL Interpreter Initialization
-------------------------------

```k
  // Note: Do we need to maintain the stack size? Can't we just compute it when needed?

  rule <k> Rs:TealPragmas P:TealPgm => Rs ~> #LoadPgm(P, .K) </k>
  rule <k> R:TealPragma Rs:TealPragmas => R ~> Rs ... </k>

  rule <k> #pragma mode M:TealMode => .K ...  </k>
       <mode> _ => M </mode>

  rule <k> #pragma version V => . ... </k>
       <version> _ => V </version>

  rule <k> #pragma txn V => . ... </k>
       <currentTx> _ => V </currentTx>

  syntax KItem ::= #LoadPgm(TealPgm, K)
  // ----------------------------------
  rule <k> #LoadPgm( Op Pgm, VPgm ) => #LoadPgm( Pgm, VPgm ~> Op ) </k>
       <mode> Mode </mode>
    requires #ValidOpForMode( Mode, Op )

  rule <k> #LoadPgm( Op, VPgm ) => VPgm ~> Op </k>
       <mode> Mode </mode>
    requires #ValidOpForMode( Mode, Op )

  rule <k> #LoadPgm( Op _, _ ) => panic(INVALID_OP_FOR_MODE) </k>
       <mode> Mode </mode>
    requires notBool #ValidOpForMode( Mode, Op )

  rule <k> #LoadPgm( Op, _ ) => panic(INVALID_OP_FOR_MODE) </k>
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

Panic Behaviors
---------------

A TEAL program may panic for one of the following reasons:

1.  Opcode used not valid for current mode of execution

2.  The `err` opcode is encountered

3.  Integer overflow

4.  Integer undeflow

5.  Division by zero

6.  `concat`: The resulting byte array is too large (> 4k bytes)

7.  `txn`/`txna`: Accessing a transaction field failed
    - The transaction does not exist
    - The transaction type is invalid
    - The requested field is invalid for the transaction type
    - Indexing an array field out of bounds

8.  An opcode attempts to write to or read from an invalid scratch space
    location

9.  An opcode attempts to use an invalid index for a byte array (`substring*`,
    `arg`)

10. branching beyond the end of the program or brcnhing backwards (`b*`)

11. An input in the stack is not of the expected type

12. An opcode attempts to push to a full stack

13. An opcode attempts to pop from an empty stack

14. An assertion is violated, i.e. the asserted expression evaluates to zero

15. A negative number is supplied on stack. That panic behavior is impossible in concrete
    execution, but is helpful in some symbolic execution scenarios.

Other reasons for panic behavior, which do not apply to this specification
of TEAL, include:

16. `global`: Wrong global field (rejected by our TEAL parser; syntax
    definition disallows invalid fields)

17. `txn/txna`: wrong type argument (rejected by our TEAL parser; syntax
    definition disallows invalid fields)

18. Loading constants from beyond the bytecblock or the intcblock of the
    program (This is specific to post-assembly TEAL and does not apply to our
    abstract semantics)

 19. Invalid opcode (rejected by our TEAL parser; syntax definition disallows
    invalid opcodes)

Panic conditions (1 -- 15 above) are captured by the `panic` computation,
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
  syntax String ::= "INDEX_OUT_OF_BOUNDS"        [macro]
  syntax String ::= "ILLEGAL_JUMP"               [macro]
  syntax String ::= "ILL_TYPED_STACK"            [macro]
  syntax String ::= "STACK_OVERFLOW"             [macro]
  syntax String ::= "STACK_UNDERFLOW"            [macro]
  syntax String ::= "ASSERTION_VIOLATION"        [macro]
  syntax String ::= "IMPOSSIBLE_NEGATIVE_NUMBER" [macro]
  //----------------------------------------------------
  rule INVALID_OP_FOR_MODE => "invalid opcode for current execution mode"
  rule ERR_OPCODE          => "err opcode encountered"
  rule INT_OVERFLOW        => "integer overflow"
  rule INT_UNDERFLOW       => "integer underflow"
  rule DIV_BY_ZERO         => "Division by zero"
  rule BYTES_OVERFLOW      => "Resulting byte array too large"
  rule TXN_ACCESS_FAILED   => "Transaction field access failed"
  rule INVALID_SCRATCH_LOC => "Invalid scratch space location"
  rule INDEX_OUT_OF_BOUNDS => "array index out of bounds"
  rule ILLEGAL_JUMP        => "illegal branch beyond program end or backward branch"
  rule ILL_TYPED_STACK     => "wrong argument type(s) for opcode"
  rule STACK_OVERFLOW      => "stack overflow"
  rule STACK_UNDERFLOW     => "stack underflow"
  rule ASSERTION_VIOLATION => "assertion violation"
  rule IMPOSSIBLE_NEGATIVE_NUMBER => "Impossible happened: negative number on stack"
  //--------------------------------------------------------------------------------

  syntax KItem ::= panic(String)
  // ---------------------------
  rule <k> panic(S) ~> _ => .K </k>
       <stack> _ => .TStack </stack>
       <stacksize> _ => 0 </stacksize>
       <returncode> 4 => 3 </returncode>
       <returnstatus> _ => "Failure - panic: " +String S </returnstatus>
```

TEAL Interpreter Finalization
-----------------------------

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
  rule <k> .K </k>
       <stack> I : .TStack </stack>
       <stacksize> SIZE </stacksize>
       <returncode> 4 => 0 </returncode>
       <returnstatus> _ => "Success - positive-valued singleton stack" </returnstatus>
    requires I >Int 0 andBool SIZE ==Int 1

  rule <k> .K </k>
       <stack> I : .TStack => I : .TStack </stack>
       <stacksize> _ </stacksize>
       <returncode> 4 => 1 </returncode>
       <returnstatus> _ => "Failure - zero-valued singleton stack" </returnstatus>
    requires I <=Int 0

  rule <k> .K </k>
       <stack> _ </stack>
       <stacksize> SIZE </stacksize>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - stack size greater than 1" </returnstatus>
    requires SIZE >Int 1

  rule <k> .K </k>
       <stack> .TStack </stack>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - empty stack" </returnstatus>

  rule <k> .K </k>
       <stack> (_:Bytes) : .TStack </stack>
       <stacksize> _ </stacksize>
       <returncode> 4 => 2 </returncode>
       <returnstatus> _ => "Failure - singleton stack with byte array type" </returnstatus>
```

Generic TEAL Operations
-----------------------

### Special Operations

*Internal NoOp*
```k
  rule <k> NoOpCode => .K ... </k>
```

*The `err` Opcode*
```k
  rule <k> err => panic(ERR_OPCODE) ... </k>
```

### Cryptographic Operations

```k
  rule <k> sha256 => .K ... </k>
       <stack> B : XS => String2Bytes(Sha256raw(Bytes2String(B))) : XS </stack>

  rule <k> keccak256 => .K ... </k>
       <stack> B : XS => String2Bytes(Keccak256raw(Bytes2String(B))) : XS </stack>

  rule <k> sha512_256 => .K ... </k>
       <stack> B : XS => String2Bytes(Sha512_256raw(Bytes2String(B))) : XS </stack>
```

### Arithmetic Operations

*Addition*
```k
  rule <k> + => .K ... </k>
       <stack> I2 : I1 : XS => (I1 +Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 +Int I2 <=Int MAX_UINT64

  rule <k> + => panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 +Int I2 >Int MAX_UINT64
```

*Subtraction*
```k
  rule <k> - => .K ... </k>
       <stack> I2 : I1 : XS => (I1 -Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 >=Int I2

  rule <k> - => panic(INT_UNDERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 <Int I2
```

*Multiplication*
```k
  rule <k> * => .K ... </k>
       <stack> I2 : I1 : XS => (I1 *Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 *Int I2 <=Int MAX_UINT64

  rule <k> * => panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 *Int I2 >Int MAX_UINT64
```

*Division*
```k
  rule <k> / => .K ... </k>
       <stack> I2 : I1 : XS => (I1 /Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >Int 0

  rule <k> / => panic(DIV_BY_ZERO) ... </k>
       <stack> I2 : (_:TValue) : _ </stack>
    requires I2 <=Int 0
```

*Remainder*
```k
  rule <k> % => .K ... </k>
       <stack> I2 : I1 : XS => (I1 %Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >Int 0

  rule <k> % => panic(DIV_BY_ZERO) ... </k>
       <stack> I2 : (_:TValue) : _ </stack>
    requires I2 <=Int 0
```

*Wide 128-bit Addition*
```k
  rule <k> addw => .K ... </k>
       <stack> I2 : I1 : XS => lowerU64(I1 +Int I2) : upperU64(I1 +Int I2) : XS </stack>
```

*Wide 128-bit Multiplication*
```k
  rule <k> mulw => .K ... </k>
       <stack> I2 : I1 : XS => lowerU64(I1 *Int I2) : upperU64(I1 *Int I2) : XS </stack>
```

### Relational Operations

```k
  rule <k> < => .K ... </k>
       <stack> I2 : I1 : XS => (#if I1 <Int I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> > => .K ... </k>
       <stack> I2 : I1 : XS => (#if I1 >Int I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> <= => .K ... </k>
       <stack> I2 : I1 : XS => (#if I1 <=Int I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> >= => .K ... </k>
       <stack> I2 : I1 : XS => (#if I1 >=Int I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> == => .K ... </k>
       <stack> (I2:Int) : (I1:Int) : XS => (#if I1 ==Int I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> == => .K ... </k>
       <stack> (B2:Bytes) : (B1:Bytes) : XS => (#if B1 ==K B2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> != => .K ... </k>
       <stack> (I2:Int) : (I1:Int) : XS => (#if I1 =/=K I2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> != => .K ... </k>
       <stack> (B2:Bytes) : (B1:Bytes) : XS =>
               (#if B1 =/=K B2 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
```

### Logical Operations

```k
  rule <k> && => .K ... </k>
       <stack> I2 : I1 : XS =>
               (#if I1 >Int 0 andBool I2 >Int 0 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> || => .K ... </k>
       <stack> I2 : I1 : XS =>
               (#if I1 >Int 0 orBool I2 >Int 0 #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> ! => .K ... </k>
       <stack> I : XS => (#if I ==Int 0 #then 1 #else 0 #fi) : XS </stack>
```

### Bitwise Operations

```k
  rule <k> | => .K ... </k>
       <stack> I2 : I1 : XS => (I1 |Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> & => .K ... </k>
       <stack> I2 : I1 : XS => (I1 &Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> ^ => .K ... </k>
       <stack> I2 : I1 : XS => (I1 xorInt I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> ~ => .K ... </k>
       <stack> I : XS => (~Int I) : XS </stack>
```

### Byte Array Operations

*Bytes length*
```k
  rule <k> len => .K ... </k>
       <stack> B : XS => lengthBytes(B) : XS </stack>
```

*Int-to-bytes conversion*
```k
  rule <k> itob => .K ... </k>
       <stack> I : XS => Int2Bytes(I, BE, Unsigned) : XS </stack>
```

*Bytes-to-int conversion*
```k
  rule <k> btoi => .K ... </k>
       <stack> B : XS => Bytes2Int(B, BE, Unsigned) : XS </stack>
```

*Bytes concatenation*
```k
  rule <k> concat => .K ... </k>
       <stack> B2 : B1 : XS => (B1 +Bytes B2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> concat => panic(BYTES_OVERFLOW) ... </k>
       <stack> B2 : B1 : _ </stack>
    requires lengthBytes(B1 +Bytes B2) >Int MAX_BYTEARRAY_LEN
```

*Bytes Substring*
```k
  rule <k> substring START END => .K ... </k>
       <stack> B : XS => substrBytes(B, START, END) : XS </stack>
    requires 0 <=Int START andBool START <=Int END andBool END <=Int lengthBytes(B)

  rule <k> substring START END => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> (B:Bytes) : _ </stack>
    requires 0 >Int START orBool START >Int END orBool END >Int lengthBytes(B)


  rule <k> substring3 => .K ... </k>
       <stack> B : START : END : XS => substrBytes(B, START, END) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int START andBool START <=Int END andBool END <=Int lengthBytes(B)

  rule <k> substring3 => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> (B:Bytes) : START : END : _ </stack>
    requires 0 >Int START orBool START >Int END orBool END >Int lengthBytes(B)
```

*Byte-array access and modification*

```k
  rule <k> getbyte => .K ... </k>
       <stack> B : ARRAY : XS => ARRAY[B] : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)

  rule <k> getbyte => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => .K ... </k>
       <stack> C : B : ARRAY : XS => ARRAY[B <- C] : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)
             andBool 0 <=Int C andBool C <=Int MAX_UINT8

  rule <k> setbyte => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => panic(ILL_TYPED_STACK) ... </k>
       <stack> C : _ : _ : _ </stack>
    requires 0 >Int C orBool C >Int MAX_UINT8
```

### Bit-precise access and modification operations (byte-array and uint64)

#### `setbit`

We recite the [specification](https://developer.algorand.org/docs/get-details/dapps/avm/teal/opcodes/?from_query=getbit#setbit) of bit order from Algorand Developer Portal.

> When A is a byte array, index 0 is the leftmost bit of the leftmost byte. Setting bits 0 through 11 to 1 in a 4-byte-array of 0s yields the byte array 0xfff00000. Setting bit 3 to 1 on the 1-byte-array 0x00 yields the byte array 0x10.

```k
 rule <k> setbit => .K ... </k>
      <stack> C : B : ARRAY:Bytes : XS => setBitInBytes(ARRAY, B, C) : XS </stack>
      <stacksize> S => S -Int 2 </stacksize>
   requires 0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8
    andBool 0 <=Int C andBool C <Int 2

 rule <k> setbit => panic(ILL_TYPED_STACK) ... </k>
      <stack> C : _ : _:Bytes : _ </stack>
   requires notBool (0 <=Int C andBool C <Int 2)

 rule <k> setbit => panic(INDEX_OUT_OF_BOUNDS) ... </k>
      <stack> _ : B : ARRAY:Bytes : _ </stack>
   requires notBool (0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8)

  syntax Bytes ::= setBitInBytes(Bytes, Int, Int) [function]
  //------------------------------------------------------------
  rule setBitInBytes(ARRAY, B, V) =>
         ARRAY[B divInt 8 <- setBitUInt8( ARRAY[B divInt 8]
                                        , 7 -Int B modInt 8
                                        , V)]

  // Setting and unsetting signle bits in integers via bitwise and/or.
  // If the `requires` clauses are not satisfied, the semantics will
  // get stuck. This should not happen though, since the upstream code
  // panics on invalid arguments.
  syntax Int ::= setBitUInt8 (Int, Int, Int) [function]
               | setBitUInt64(Int, Int, Int) [function]
  //------------------------------------------------------------
  // to unset a bit, shift 1 to the desired position and conjunct
  rule setBitUInt8(X, B, 0) => X &Int (~Int (1 <<Int B))
   requires 0 <=Int X andBool X <=Int MAX_UINT8
    andBool 0 <=Int B andBool B <Int 8

  // to set a bit, shift 1 to the desired position and disjunct
  rule setBitUInt8(X, B, 1) => X |Int (1 <<Int B)
   requires 0 <=Int X andBool X <=Int MAX_UINT8
    andBool 0 <=Int B andBool B <Int 8

  // to unset a bit, shift 1 to the desired position and conjunct
  rule setBitUInt64(X, B, 0) => X &Int (~Int (1 <<Int B))
   requires 0 <=Int X andBool X <=Int MAX_UINT64
    andBool 0 <=Int B andBool B <Int 64

  // to set a bit, shift 1 to the desired position and disjunct
  rule setBitUInt64(X, B, 1) => X |Int (1 <<Int B)
   requires 0 <=Int X andBool X <=Int MAX_UINT64
    andBool 0 <=Int B andBool B <Int 64
```

> When A is a `uint64`, index 0 is the least significant bit. Setting bit 3 to 1 on the integer 0 yields 8, or 2^3.

```k
  rule <k> setbit => .K ... </k>
       <stack> C : B : I:Int : XS => setBitUInt64(I, B, C) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int I andBool I <=Int MAX_UINT64
     andBool 0 <=Int B andBool B <Int 64
     andBool 0 <=Int C andBool C <Int 2

  rule <k> setbit => panic(ILL_TYPED_STACK) ... </k>
       <stack> C : _ : _:Int : _ </stack>
    requires notBool (0 <=Int C andBool C <Int 2)

  rule <k> setbit => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> _ : B : _:Int : _ </stack>
    requires notBool (0 <=Int B andBool B <Int 64)
```

#### `getbit`

```k
 rule <k> getbit => .K ... </k>
      <stack> B : ARRAY:Bytes : XS => getBitFromBytes(ARRAY, B) : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8

 rule <k> getbit => panic(INDEX_OUT_OF_BOUNDS) </k>
      <stack> B : ARRAY:Bytes : _ </stack>
    requires notBool (0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8)

  syntax Int ::= getBitFromBytes(Bytes, Int) [function]
  //------------------------------------------------------------
  // TODO: alternatively, we could use a bitmask here like in `setbit`.
  // Let's see which way causes more problems down the road.
  rule getBitFromBytes(ARRAY, B) =>
      bitRangeInt( ARRAY[B divInt 8]
                 , 7 -Int B modInt 8
                 , 1)

  rule <k> getbit => .K ... </k>
       <stack> B : I:Int : XS => bitRangeInt(I, B, 1) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int I andBool I <=Int MAX_UINT64 andBool
             0 <=Int B andBool B <Int 64

  rule <k> getbit => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : _:Int : _  </stack>
    requires notBool (0 <=Int B andBool B <Int 64)
```

### Constant Loading Operations

The specs currently define abstractly the semantics of TEAL's pseudo-ops,
without considering the construction of constant blocks `intcblock` and
`bytecblock` and the injection of `intc` and `bytec` opcodes. The following
rules are thus not used and are kept for reference only.

```k
  rule <k> intcblock N VL => .K ... </k>
       <intcblock> _ => genIntcBlockMap(N, 0, VL) </intcblock>

  rule <k> intc I => .K ... </k>
       <intcblock> INTS  </intcblock>
       <stack> XS => ({INTS[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (I:Int in_keys(INTS))

  rule <k> intc_0 => intc 0 ... </k>
  rule <k> intc_1 => intc 1 ... </k>
  rule <k> intc_2 => intc 2 ... </k>
  rule <k> intc_3 => intc 3 ... </k>

  rule <k> bytecblock N VPL => .K ... </k>
       <bytecblock> _ => genBytecBlockMap(N, 0, VPL) </bytecblock>

  rule <k> bytec I => .K ... </k>
       <bytecblock> I |-> V ... </bytecblock>
       <stack> XS => V : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> bytec_0 => bytec 0 ... </k>
  rule <k> bytec_1 => bytec 1 ... </k>
  rule <k> bytec_2 => bytec 2 ... </k>
  rule <k> bytec_3 => bytec 3 ... </k>
```

The `pushbytes` and `pushint` opcodes push an immediate constant onto stack.
The constants are not added into `bytecblock`/`intcblock` during assembly.
In our spec, `pushbytes` and `pushint` are equivalent to `byte` and `int`.

```k
  rule <k> pushint I => .K ... </k>
       <stack> XS => normalizeI(I) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> pushbytes B => .K ... </k>
       <stack> XS => normalize(B) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
```

#### Constant Loading Pseudo-Ops

```k
  rule <k> addr B => .K ... </k>
       <stack> XS => normalize(B) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> int I => .K ... </k>
       <stack> XS => normalizeI(I) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> byte B => .K ... </k>
       <stack> XS => normalize(B) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> _:PseudoOpCode => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```

#### Constant Loading Auxiliary Functions

```k
  syntax Map ::= genIntcBlockMap(Int, Int, TValueList) [function]
  //------------------------------------------------------------
  rule genIntcBlockMap(N, I, V VL) =>
         I |-> V
         genIntcBlockMap(N -Int 1, I +Int 1, VL)
    requires N >Int 1

  rule genIntcBlockMap(1, I, V) => I |-> V

  syntax Map ::= genBytecBlockMap(Int, Int, TValuePairList) [function]
  //-----------------------------------------------------------------
  // Note: byte array size is ignored
  rule genBytecBlockMap(N, I, (_, V) VPL) =>
         I |-> V
         genBytecBlockMap(N -Int 1, I +Int 1, VPL)
    requires N >Int 1

  rule genBytecBlockMap(1, I, (_, V)) => I |-> V
```

### Flow Control

```k
  rule <k> bnz L => jump(L) ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I >Int 0

  rule <k> bnz _ => .K ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I <=Int 0

  rule <k> bnz L => panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires L in_labels LL


  rule <k> bz L => jump(L) ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I <=Int 0

  rule <k> bz _ => .K ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I >Int 0

  rule <k> bz L => panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires L in_labels LL


  rule <k> b L => jump(L) ... </k>

  rule <k> b L => panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires L in_labels LL


  rule <k> return ~> _ => .K </k>
       <stack> (I:Int) : XS => I:XS </stack>
       <stacksize> _ => 1 </stacksize>


  rule <k> L: => .K ... </k>
       <labels> LL => L LL </labels>

  rule <k> assert => .K ... </k>
       <stack> (X:Int) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires X >Int 0

  rule <k> assert => panic(ASSERTION_VIOLATION) ... </k>
       <stack> (X:Int) : _ </stack>
    requires X ==Int 0

  rule <k> assert => panic(IMPOSSIBLE_NEGATIVE_NUMBER) ... </k>
       <stack> (X:Int) : _ </stack>
    requires X <Int 0


  syntax KItem ::= jump(Label)
  //--------------------------
  rule <k> jump(L) ~> L:            => .K      ... </k>
       <labels> LL => L LL </labels>

  rule <k> jump(L) ~> L':           => jump(L) ... </k>
       <labels> LL => L' LL </labels>
    requires L =/=K L'

  rule <k> jump(L) ~> _:TealOpCode  => jump(L) ... </k>

  rule <k> jump(_) => panic(ILLEGAL_JUMP) </k>
```

### Stack Manipulation
```k
  rule <k> pop => .K ... </k>
       <stack> _ : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> dup => .K ... </k>
       <stack> X : XS => X : X : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> dup => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> dup2 => .K ... </k>
       <stack> V2 : V1 : XS => V2 : V1 : V2 : V1 : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
    requires S +Int 1 <Int MAX_STACK_DEPTH

  rule <k> dup2 => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S +Int 1 >=Int MAX_STACK_DEPTH

  rule <k> dig N => .K ... </k>
       <stack> STACK => STACK[N]:STACK </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH andBool
             0 <=Int N andBool N <Int S

  rule <k> dig _ => panic(STACK_OVERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> dig N => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> swap => .K ... </k>
       <stack> X : Y : XS => Y : X : XS </stack>

  rule <k> swap => panic(STACK_UNDERFLOW) ... </k>
       <stack> _:.TStack </stack>

  rule <k> select => .K ... </k>
       <stack> A : B : C : XS =>
               (#if C =/=Int 0 #then B #else A #fi) : XS
       </stack>
       <stacksize> S => S -Int 2 </stacksize>
```

### Blockchain State Accessors

```k
  rule <k> txn I => .K ... </k>
       <stack> XS => ({getTxnField(getCurrentTxn(), I)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> txn I J => txna I J ... </k>

  rule <k> gtxn G I => .K ... </k>
       <stack> XS => ({getTxnField(G, I)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> gtxns I => .K ... </k>
       <stack> G : XS => ({getTxnField(G, I)}:>TValue) : XS </stack>
       <stacksize> _ </stacksize>

  rule <k> txna I J => .K ... </k>
       <stack> XS => ({getTxnField(getCurrentTxn(), I, J)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> gtxna G I J => .K ... </k>
       <stack> XS => ({getTxnField(G, I, J)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> gtxnsa I J => .K ... </k>
       <stack> G : XS => ({getTxnField(G, I, J)}:>TValue) : XS </stack>
       <stacksize> _ </stacksize>

  rule <k> global I => .K ... </k>
       <stack> XS => getGlobalField(I) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> _:BlockchainOpCode => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```

```k
  rule <k> load I => .K ... </k>
       <stack> XS => ({M[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <scratch> M </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)
     andBool S <Int MAX_STACK_DEPTH

  rule <k> store I => .K ... </k>
       <stack> V : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <scratch> M => M[I <- V] </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE

  rule <k> load I => panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> store I => panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> _:ScratchOpCode => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```

Stateless TEAL Operations
-------------------------

### Logic Signature Argument Accessors

```k
  rule <k> arg I => .K ... </k>
       <stack> XS => ({getArgument(I)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool isTValue(getArgument(I))

  rule <k> arg I => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool notBool (isTValue(getArgument(I)))

  rule <k> arg _ => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> arg_0 => arg 0 ... </k>
  rule <k> arg_1 => arg 1 ... </k>
  rule <k> arg_2 => arg 2 ... </k>
  rule <k> arg_3 => arg 3 ... </k>
```

Stateful TEAL Operations
------------------------

### Application State Accessors

*balance*

```k
  rule <k> balance => .K ... </k>
       <stack> (I:Int) : XS => getBalance({getAccountAddressAt(I)}:>TValue) : XS </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> balance => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))
```

*app_opted_in*

```k
  rule <k> app_opted_in =>
           #app_opted_in hasOptedInApp(APP, {getAccountAddressAt(I)}:>TValue) ... </k>
       <stack> (APP:Int) : (I:Int) : _ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> app_opted_in  => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Int) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))

  syntax KItem ::= "#app_opted_in" Bool
  //-----------------------------------
  rule <k> #app_opted_in B => .K ... </k>
       <stack> _ : _ : XS => (#if B #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
```

*app_local_get*

```k
  rule <k> app_local_get =>
           #app_local_get getAppLocal({getAccountAddressAt(I)}:>TValue
                                     , getGlobalField(CurrentApplicationID), KEY) ... </k>
       <stack> (KEY:Bytes) : (I:Int) : _ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> app_local_get => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))

  syntax KItem ::= "#app_local_get" TValue
  //-------------------------------------
  rule <k> #app_local_get V => .K ... </k>
       <stack> (_:Bytes) : ( _:Int) : XS => V : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  syntax KItem ::= "#app_local_get" TValue
  //-------------------------------------
  rule <k> #app_local_get V => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : XS => 0 : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_local_get_ex*

```k
  rule <k> app_local_get_ex =>
           #app_local_get_ex getAppLocal({getAccountAddressAt(I)}:>TValue, APP, KEY) ... </k>
       <stack> (KEY:Bytes) : (APP:Int) : (I:Int) : _ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> app_local_get_ex => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (_:Int) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))


  syntax KItem ::= "#app_local_get_ex" TValue
  //----------------------------------------
  rule <k> #app_local_get_ex V => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : (_:Int) : XS => 1 : V : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_local_get_ex V => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : (_:Int) : XS => 0 : 0 : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_local_put*

```k
  rule <k> app_local_put => #app_local_put {getAccountAddressAt(I)}:>TValue
                                           getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (I:Int) : _ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> app_local_put => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))

  syntax KItem ::= "#app_local_put" TValue TValue
  //-------------------------------------------
  rule <k> #app_local_put ADDR APP => .K ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localStorage> M => M[KEY <- NEWVAL] </localStorage> ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>

  // if the account exists but is not opted in, do nothing
  rule <k> #app_local_put ADDR APP => .K ... </k>
       <stack> (_:TValue) : (_:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, do nothing
  rule <k> #app_local_put ADDR _ => .K ... </k>
       <stack> (_:TValue) : (_:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))
```

*app_local_del*

```k
  rule <k> app_local_del => #app_local_del {getAccountAddressAt(I)}:>TValue
                                           getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:Bytes) : (I:Int) : _ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> app_local_del => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes ) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))


  syntax KItem ::= "#app_local_del" TValue TValue
  //-------------------------------------------
  rule <k> #app_local_del ADDR APP => .K ... </k>
       <stack> (KEY:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localStorage> M => M[KEY <- undef] </localStorage> ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>

  // if the account exists but is not opted in, do nothing
  rule <k> #app_local_del ADDR APP => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, do nothing.
  rule <k> #app_local_del ADDR _ => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))
```

*app_global_get*

```k
  rule <k> app_global_get =>
           #app_global_get getAppGlobal(getGlobalField(CurrentApplicationID), KEY) ... </k>
       <stack> (KEY:Bytes) : _ </stack>

  syntax KItem ::= "#app_global_get" TValue
  //--------------------------------------
  rule <k> #app_global_get V => .K ... </k>
       <stack> (_:Bytes) : XS => V : XS </stack>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_global_get V => .K ... </k>
       <stack> (_:Bytes) : XS => 0 : XS </stack>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_global_get_ex*

```k
  rule <k> app_global_get_ex =>
           #app_global_get_ex getAppGlobal({getForeignAppAt(I)}:>TValue, KEY) ... </k>
       <stack> (KEY:Bytes) : (I:Int) : _ </stack>
    requires isTValue(getForeignAppAt(I))

  rule <k> app_global_get_ex => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (I:Int) : _ </stack>
    requires notBool isTValue(getForeignAppAt(I))

  syntax KItem ::= "#app_global_get_ex" TValue
  //-----------------------------------------
  rule <k> #app_global_get_ex V  => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : XS => 1 : V : XS </stack>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_global_get_ex V => .K ... </k>
       <stack> (_:Bytes) : (_:Int) : XS => 0 : 0 : XS </stack>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_global_put*

```k
  rule <k> app_global_put => #app_global_put getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:TValue) : (_:Bytes) : _ </stack>

  syntax KItem ::= "#app_global_put" TValue
  //--------------------------------------
  rule <k> #app_global_put APP => .K ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <appsCreated>
         <app>
           <appID> APP </appID>
           <globalState>
             <globalStorage> M => M[KEY <- NEWVAL] </globalStorage>
             ...
           </globalState>
           ...
         </app>
         ...
       </appsCreated>

  // if the app doesn't exist, do nothing
  rule <k> #app_global_put APP => .K ... </k>
       <stack> (_:TValue) : (_:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (APP in_apps(<accountsMap> AMAP </accountsMap>))
```

*app_global_del*

```k
  rule <k> app_global_del => #app_global_del getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:Bytes) : _ </stack>

  syntax KItem ::= "#app_global_del" TValue
  //--------------------------------------
  rule <k> #app_global_put APP => .K ... </k>
       <stack> (KEY:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <appsCreated>
         <app>
           <appID> APP </appID>
           <globalState>
             <globalStorage> M => M[KEY <- undef] </globalStorage>
             ...
           </globalState>
           ...
         </app>
         ...
       </appsCreated>

  // if the app doesn't exist, do nothing
  rule <k> #app_global_del APP => .K ... </k>
       <stack> (_:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (APP in_apps(<accountsMap> AMAP </accountsMap>))

```

*asset_holding_get*

```k
  rule <k> asset_holding_get FIELD =>
           #asset_holding_get getOptInAssetField(FIELD,
                                {getAccountAddressAt(I)}:>TValue, ASSET) ... </k>
       <stack> (ASSET:Int) : (I:Int):_ </stack>
    requires isTValue(getAccountAddressAt(I))

  rule <k> asset_holding_get _ => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Int) : (I:Int) : _ </stack>
    requires notBool isTValue(getAccountAddressAt(I))

  syntax KItem ::= "#asset_holding_get" TValue
  // ----------------------------------------
  rule <k> #asset_holding_get RET => .K ... </k>
       <stack> (_:Int) : (_:Int) : XS => 1 : RET : XS </stack>
    requires {RET}:>Int >=Int 0

  // Return 0 if not opted in ASSET or the account is not found
  rule <k> #asset_holding_get RET => .K ... </k>
       <stack> (_:Int) : (_:Int) : XS => 0 : 0 : XS </stack>
    requires {RET}:>Int <Int 0
```

*asset_params_get*

```k
  rule <k> asset_params_get FIELD =>
           #asset_params_get getAssetParamsField(FIELD, {getForeignAssetAt(I)}:>TValue)
       ...
       </k>
       <stack> (I:Int) : _ </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool isTValue(getForeignAssetAt(I))

  rule <k> asset_params_get _ => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (I:Int) : _ </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (notBool isTValue(getForeignAssetAt(I)))

  rule <k> asset_params_get _ => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  syntax KItem ::= "#asset_params_get" TValue
  // ---------------------------------------
  rule <k> #asset_params_get RET => .K ... </k>
       <stack> (_:Int) : XS => 1 : RET : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires {RET}:>Int >=Int 0
     andBool S <Int MAX_STACK_DEPTH

  rule <k> #asset_params_get RET => .K ... </k>
       <stack> (_:Int) : XS => 0 : 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires {RET}:>Int <Int 0
     andBool S <Int MAX_STACK_DEPTH
```

Panic Behaviors due to Ill-typed Stack Arguments
------------------------------------------------

### Crypto Opcodes

### Arithmetic/relational/logical/Bitwise Opcodes

```k
  rule <k> Op:OpCode => panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires (isArithOpCode(Op)         orBool
              isInequalityOpCode(Op)    orBool
              isBinaryLogicalOpCode(Op) orBool
              isBinaryBitOpCode(Op))
     andBool (isBytes(V2) orBool isBytes(V1))

  rule <k> Op:OpCode => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>
    requires isUnaryLogicalOpCode(Op) orBool isUnaryBitOpCode(Op)

  rule <k> _:EqualityOpCode => panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires (isBytes(V1) andBool isInt(V2))
      orBool (isBytes(V2) andBool isInt(V1))
```

### Byte Opcodes
```k
  rule <k> len => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> itob => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>

  rule <k> btoi => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> concat => panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires isInt(V2) orBool isInt(V1)

  rule <k> substring _ _ => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> substring3 => panic(ILL_TYPED_STACK) ... </k>
       <stack> (V:TValue) : (START:TValue) : (END:TValue) : _ </stack>
    requires isInt(V) orBool isBytes(START) orBool isBytes(END)
```

### Flow Control Opcodes
```k
  rule <k> Op:OpCode => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>
    requires isCondBranchOpCode(Op) orBool isReturnOpCode(Op)
```

### Application State Opcodes
```k
  rule <k> balance => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>

  rule <k> app_opted_in => panic(ILL_TYPED_STACK) ... </k>
       <stack> (APP:TValue) : (I:TValue) : _ </stack>
    requires isBytes(APP) orBool isBytes(I)

  rule <k> app_local_get => panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (I:TValue) : _ </stack>
    requires isInt(KEY) orBool isBytes(I)

  rule <k> app_local_get_ex => panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (APP:TValue) : (I:TValue) : _ </stack>
    requires isInt(KEY) orBool isBytes(APP) orBool isBytes(I)

  rule <k> app_local_put => panic(ILL_TYPED_STACK) ...  </k>
       <stack> (_:TValue) : (KEY:TValue) : (I:TValue) : _ </stack>
    requires isInt(KEY) orBool isBytes(I)

  rule <k> app_local_del => panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (I:TValue) : _ </stack>
    requires isInt(KEY) orBool isBytes(I)

  rule <k> app_global_get => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> app_global_get_ex => panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (I:TValue):_ </stack>
    requires isInt(KEY) orBool isBytes(I)

  rule <k> app_global_put => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:TValue) : (_:Int):_ </stack>

  rule <k> app_global_del => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> asset_holding_get _ => panic(ILL_TYPED_STACK) ... </k>
       <stack> (ASSET:TValue) : (I:TValue) : _ </stack>
    requires isBytes(ASSET) orBool isBytes(I)

  rule <k> asset_params_get _ => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>
```

### Signature Verification Opcode

Panic Behaviors due to Insufficient Stack Arguments
---------------------------------------------------

```k
  // Opcodes requiring at least three stack elements
  rule <k> Op:OpCode => panic(STACK_UNDERFLOW) ... </k>
       <stack> (_:TValue) : (_:TValue) : .TStack </stack>
       <stacksize> 2 </stacksize>
    requires isTernaryStateOpCode(Op)
      orBool isTernaryByteOpCode(Op)
      orBool isSigVerOpCode(Op)
      orBool isTernaryStackOpCode(Op)

  // Opcodes requiring at least two stack elements
  rule <k> Op:OpCode => panic(STACK_UNDERFLOW) ... </k>
       <stack> (_:TValue) : .TStack </stack>
       <stacksize> 1 </stacksize>
    requires isArithOpCode(Op)
      orBool isBinaryBitOpCode(Op)
      orBool isRelationalOpCode(Op)
      orBool isBinaryLogicalOpCode(Op)
      orBool isBinaryByteOpCode(Op)
      orBool isTernaryByteOpCode(Op)
      orBool isBinaryStackOpCode(Op)
      orBool isSigVerOpCode(Op)
      orBool isBinaryStateOpCode(Op)
      orBool isTernaryStateOpCode(Op)

  // Opcodes requiring at least one stack element
  rule <k> Op:OpCode => panic(STACK_UNDERFLOW) ... </k>
       <stack> .TStack </stack>
       <stacksize> 0 </stacksize>
    requires isCryptoOpCode(Op)
      orBool isArithOpCode(Op)
      orBool isBitOpCode(Op)
      orBool isRelationalOpCode(Op)
      orBool isLogicalOpCode(Op)
      orBool isByteOpCode(Op)
      orBool isStoreOpCode(Op)
      orBool isCondBranchOpCode(Op)
      orBool isReturnOpCode(Op)
      orBool isStackOpCode(Op)
      orBool isStateOpCode(Op)
      orBool isSigVerOpCode(Op)

endmodule
```
