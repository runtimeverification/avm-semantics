```k
requires "krypto.md"

requires "avm/blockchain.md"
requires "avm/args.md"
requires "avm/avm-configuration.md"
requires "avm/avm-limits.md"
requires "avm/itxn.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-stack.md"
requires "avm/teal/teal-execution.md"
requires "avm/panics.md"
```

TEAL Interpreter
================

```k
module TEAL-DRIVER
  imports AVM-CONFIGURATION
  imports AVM-LIMITS
  imports ALGO-ITXN
  imports GLOBALS
  imports TEAL-INTERPRETER-STATE
  imports TEAL-EXECUTION
  imports TEAL-STACK
  imports KRYPTO
  imports AVM-PANIC
```

This module describes the semantics of TEAL opcodes.

See `teal-execution.md` for the initialization, execution flow and finalization semantics:
* [Interpreter Initialization](./teal-execution.md#teal-interpreter-initialization)
* [Execution](./teal-execution.md#teal-execution)
* [Interpreter Finalization](./teal-execution.md#teal-interpreter-finalization)
* [TEAL Panic Behaviors](./teal-execution.md#panic-behaviors)

Opcode Semantics
================

### Special Operations

*Internal NoOp*
```k
  rule <k> NoOpCode  => .K ... </k>
```

*The `err` Opcode*
```k
  rule <k> err => #panic(ERR_OPCODE) ... </k>
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

  rule <k> + => #panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 +Int I2 >Int MAX_UINT64
```

*Subtraction*
```k
  rule <k> - => .K ... </k>
       <stack> I2 : I1 : XS => (I1 -Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 >=Int I2

  rule <k> - => #panic(INT_UNDERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 <Int I2
```

*Multiplication*
```k
  rule <k> * => .K ... </k>
       <stack> I2 : I1 : XS => (I1 *Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 *Int I2 <=Int MAX_UINT64

  rule <k> * => #panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 *Int I2 >Int MAX_UINT64
```

*Division*
```k
  rule <k> / => .K ... </k>
       <stack> I2 : I1 : XS => (I1 /Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >Int 0

  rule <k> / => #panic(DIV_BY_ZERO) ... </k>
       <stack> I2 : (_:TValue) : _ </stack>
    requires I2 <=Int 0
```

*Remainder*
```k
  rule <k> % => .K ... </k>
       <stack> I2 : I1 : XS => (I1 %Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >Int 0

  rule <k> % => #panic(DIV_BY_ZERO) ... </k>
       <stack> I2 : (_:TValue) : _ </stack>
    requires I2 <=Int 0
```

*Exponentiation*
```k
  rule <k> exp => .K ... </k>
       <stack> I2 : I1 : XS => (I1 ^Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 ^Int I2 <=Int MAX_UINT64
     andBool notBool (I1 ==Int 0 andBool I2 ==Int 0)

  rule <k> exp => #panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ==Int 0 andBool I2 ==Int 0

  rule <k> exp => #panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ^Int I2 >Int MAX_UINT64
```

*Wide 128-bit Division and Modulus*
```k
  rule <k> divmodw => .K ... </k>
       <stack> I4 : I3 : I2 : I1 : XS =>
               #fun(NUMERATOR
            => #fun(DENOMINATOR
            => #fun(QUOTIENT
            => #fun(REMAINDER
            =>   lowerU64(REMAINDER) : upperU64(REMAINDER) :
                 lowerU64(QUOTIENT)  : upperU64(QUOTIENT)  : XS
               )(NUMERATOR %Int DENOMINATOR)
               )(NUMERATOR /Int DENOMINATOR)
               )(asUInt128(I3, I4))
               )(asUInt128(I1, I2))
       </stack>
    requires notBool (I4 ==Int 0 andBool I3 ==Int 0)

  rule <k> divmodw => #panic(DIV_BY_ZERO) ... </k>
       <stack> I4 : I3 : _ : _ : _ </stack>
    requires I4 ==Int 0 andBool I3 ==Int 0

  rule <k> divw => .K ... </k>
       <stack> I3 : I2 : I1 : XS =>
               #fun(NUMERATOR
            => #fun(DENOMINATOR
            => #fun(QUOTIENT
            => QUOTIENT : XS
               )(NUMERATOR /Int DENOMINATOR)
               )(I3)
               )(asUInt128(I1, I2))
       </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires I3 =/=Int 0
     andBool (asUInt128(I1, I2) /Int I3) <=Int MAX_UINT64

  rule <k> divw => #panic(INT_OVERFLOW) ... </k>
       <stack> I3 : I2 : I1 : _ </stack>
    requires I3 =/=Int 0
     andBool (asUInt128(I1, I2) /Int I3) >Int MAX_UINT64

  rule <k> divw => #panic(DIV_BY_ZERO) ... </k>
       <stack> 0 : _ : _ : _ </stack>

  rule <k> divw => #panic(ILL_TYPED_STACK) ... </k>
       <stack> I3 : I2 : I1 : _ </stack>
    requires isBytes(I1) orBool isBytes(I2) orBool isBytes(I3)

  // Auxilary funtion that interprets two `UInt64` as one Int, big-endian
  syntax Int ::= asUInt128(TUInt64, TUInt64) [function, total]
  // --------------------------------------------------------------
  rule asUInt128(I1, I2) => (I1 <<Int 64) +Int I2

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

*Wide 128-bit Exponentiation*
```k
  rule <k> expw => .K ... </k>
       <stack> I2 : I1 : XS => lowerU64(I1 ^Int I2) : upperU64(I1 ^Int I2) : XS </stack>
    requires I1 ^Int I2 <=Int MAX_UINT128
     andBool notBool (I1 ==Int 0 andBool I2 ==Int 0)

  rule <k> expw => #panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ==Int 0 andBool I2 ==Int 0

  rule <k> expw => #panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ^Int I2 >Int MAX_UINT128
```

*Square root*

The largest integer B such that B^2 <= X

```k
  rule <k> sqrt => .K ... </k>
       <stack> X : XS => sqrtTUInt64(X) : XS </stack>
    requires X >=Int 0 andBool X <=Int MAX_UINT64

  rule <k> sqrt => #panic(INVALID_ARGUMENT) ... </k>
       <stack> X : _ </stack>
    requires notBool( X >=Int 0 andBool X <=Int MAX_UINT64)
```

*Binary square root*

The largest integer B such that B^2 <= X

```k
  rule <k> bsqrt => .K ... </k>
       <stack> B:Bytes : XS => Int2Bytes(sqrtUInt(Bytes2Int(B, BE, Unsigned)), BE, Unsigned) : XS </stack>

  rule <k> bsqrt => #panic(INVALID_ARGUMENT) ... </k>
       <stack> _:Int : _ </stack>
```

The `sqrtTUInt64` function implements the integer square root algorithms described by the following excerpt
from the [reference TEAL interpreter](https://github.com/algorand/go-algorand/blob/ca3e87734833123284d3a7d87fcc9eaaede8f32a/data/transactions/logic/eval.go#L1202):

```go
last := len(cx.stack) - 1
sq := cx.stack[last].Uint
var rem uint64 = 0
var root uint64 = 0
for i := 0; i < 32; i++ {
	root <<= 1
	rem = (rem << 2) | (sq >> (64 - 2))
	sq <<= 2
	if root < rem {
		rem -= root | 1
		root += 2
	}
}
cx.stack[last].Uint = root >> 1
```

`https://en.wikipedia.org/wiki/Integer_square_root#Example_implementation_in_C`

```k
  syntax Int ::= sqrtUInt(Int)           [function]
  syntax Int ::= sqrtUInt(Int, Int, Int) [function]

  rule sqrtUInt(X) => X requires X <=Int 1 andBool X >=Int 0
  rule sqrtUInt(X) => sqrtUInt(X, X /Int 2, ((X /Int 2) +Int (X /Int (X /Int 2))) /Int 2) requires X >Int 1

  rule sqrtUInt(_, X0, X1) => X0 requires X1 >=Int X0
  rule sqrtUInt(X, X0, X1) => sqrtUInt(X, X1, (X1 +Int (X /Int X1)) /Int 2) requires X1 <Int X0
```

Note that we need to perform the left shift modulo `MAX_UINT64 + 1`, otherwise the `SQ` variable will exceed `MAX_UINT64` in the last iteration.

```k
  syntax Int ::= sqrtTUInt64(TUInt64)                        [function]
               | sqrtTUInt64(TUInt64, TUInt64, TUInt64, Int) [function]
  // ------------------------------------------------------------------
  rule sqrtTUInt64(SQ) => sqrtTUInt64(SQ, 0, 0, 0)
    requires SQ >=Int 0 andBool SQ <=Int MAX_UINT64

  rule sqrtTUInt64(SQ, REM, ROOT, I) =>
       #fun(ROOT'
    => #fun(REM'
    => #if   ROOT' <Int REM'
       #then sqrtTUInt64((SQ <<Int 2) %Int (MAX_UINT64 +Int 1)
                        , REM' -Int (ROOT' |Int 1)
                        , ROOT' +Int 2
                        , I +Int 1)
       #else sqrtTUInt64((SQ <<Int 2) %Int (MAX_UINT64 +Int 1)
                        , REM'
                        , ROOT'
                        , I +Int 1)
       #fi
       )((REM <<Int 2) |Int (SQ >>Int (64 -Int 2)))
       )(ROOT <<Int 1)
    requires I >=Int 0 andBool I <Int 32
  rule sqrtTUInt64(_, _  , ROOT, I) => ROOT >>Int 1
    requires I >=Int 32
```

### Relational Operations

```k
  rule <k> < => .K ... </k>
       <stack> I2 : I1 : XS => bool2Int (I1 <Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> > => .K ... </k>
       <stack> I2 : I1 : XS => bool2Int (I1 >Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> <= => .K ... </k>
       <stack> I2 : I1 : XS => bool2Int (I1 <=Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> >= => .K ... </k>
       <stack> I2 : I1 : XS => bool2Int (I1 >=Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> == => .K ... </k>
       <stack> (I2:Int) : (I1:Int) : XS => bool2Int (I1 ==Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> == => .K ... </k>
       <stack> (B2:Bytes) : (B1:Bytes) : XS => bool2Int (B1 ==K B2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> != => .K ... </k>
       <stack> (I2:Int) : (I1:Int) : XS => bool2Int (I1 =/=K I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> != => .K ... </k>
       <stack> (B2:Bytes) : (B1:Bytes) : XS =>
               bool2Int (B1 =/=K B2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
```

### Logical Operations

```k
  rule <k> && => .K ... </k>
       <stack> I2 : I1 : XS =>
               bool2Int (I1 >Int 0 andBool I2 >Int 0) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> || => .K ... </k>
       <stack> I2 : I1 : XS =>
               bool2Int (I1 >Int 0 orBool I2 >Int 0) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> ! => .K ... </k>
       <stack> I : XS => bool2Int (I ==Int 0) : XS </stack>
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

  rule <k> shl => .K ... </k>
       <stack> I2 : I1 : XS => ((I1 <<Int I2) %Int (MAX_UINT64 +Int 1)) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >=Int 0 andBool I2 <Int 64

  rule <k> shl => #panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : _ : _ </stack>
    requires notBool (I2 >=Int 0 andBool I2 <Int 64)

  rule <k> shr => .K ... </k>
       <stack> I2 : I1 : XS => (I1 >>Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >=Int 0 andBool I2 <Int 64

  rule <k> shr => #panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : _ : _ </stack>
    requires notBool (I2 >=Int 0 andBool I2 <Int 64)

  rule <k> ~ => .K ... </k>
       <stack> I : XS => (I xorInt MAX_UINT64) : XS </stack>

  rule <k> ~ => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:Bytes : _ </stack>
```

`bitlen` computes the highest set bit in X, indexed from one. Can be used for both integers and byte-arrays.
If X is a byte-array, it is interpreted as a big-endian unsigned integer. bitlen of 0 is 0, bitlen of 8 is 4.

```k
  rule <k> bitlen => .K ... </k>
       <stack> (I:Int) : XS => 0 : XS </stack>
    requires I ==Int 0

  rule <k> bitlen => .K ... </k>
       <stack> (I:Int) : XS => log2Int(I) +Int 1 : XS </stack>
    requires 0 <Int I andBool I <=Int MAX_UINT64

//  rule <k> bitlen => #panic(INVALID_ARGUMENT) ... </k>
//       <stack> (I:Int) : _ </stack>
//    requires notBool (0 <=Int I andBool I <=Int MAX_UINT64)

  rule <k> bitlen => .K ... </k>
       <stack> (B:Bytes) : XS => 0 : XS </stack>
    requires lengthBytes(B) <=Int MAX_BYTEARRAY_LEN
     andBool Bytes2Int(B, BE, Unsigned) ==Int 0

  rule <k> bitlen => .K ... </k>
       <stack> (B:Bytes) : XS => log2Int(Bytes2Int(B, BE, Unsigned)) +Int 1 : XS </stack>
    requires lengthBytes(B) <=Int MAX_BYTEARRAY_LEN
     andBool Bytes2Int(B, BE, Unsigned) >Int 0

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
       <stack> I : XS => padLeftBytes(Int2Bytes(I, BE, Unsigned), 8, 0) : XS </stack>
```

*Bytes-to-int conversion*
```k
  rule <k> btoi => .K ... </k>
       <stack> B : XS => Bytes2Int(B, BE, Unsigned) : XS </stack>
    requires Bytes2Int(B, BE, Unsigned) <=Int MAX_UINT64

  rule <k> btoi => #panic(INT_OVERFLOW) ... </k>
       <stack> B : _ </stack>
    requires Bytes2Int(B, BE, Unsigned) >Int MAX_UINT64
```

*Bytes concatenation*
```k
  rule <k> concat => .K ... </k>
       <stack> B2 : B1 : XS => (B1 +Bytes B2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(B1 +Bytes B2) <=Int MAX_BYTEARRAY_LEN

  rule <k> concat => #panic(BYTES_OVERFLOW) ... </k>
       <stack> B2 : B1 : _ </stack>
    requires lengthBytes(B1 +Bytes B2) >Int MAX_BYTEARRAY_LEN
```

*Bytes Substring*
```k
  rule <k> substring START END => .K ... </k>
       <stack> B : XS => substrBytes(B, START, END) : XS </stack>
    requires 0 <=Int START andBool START <=Int END andBool END <=Int lengthBytes(B)

  rule <k> substring START END => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> (B:Bytes) : _ </stack>
    requires 0 >Int START orBool START >Int END orBool END >Int lengthBytes(B)


  rule <k> substring3 => .K ... </k>
       <stack> B : START : END : XS => substrBytes(B, START, END) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int START andBool START <=Int END andBool END <=Int lengthBytes(B)

  rule <k> substring3 => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> (B:Bytes) : START : END : _ </stack>
    requires 0 >Int START orBool START >Int END orBool END >Int lengthBytes(B)
```

*Zero bytes*
```k
  rule <k> bzero => .K ... </k>
       <stack> X : XS => padLeftBytes(.Bytes, X, 0) : XS </stack>
    requires X <=Int MAX_BYTEARRAY_LEN

  rule <k> bzero => #panic(INVALID_ARGUMENT) ... </k>
       <stack> X : _ </stack>
    requires X >Int MAX_BYTEARRAY_LEN
```

*Byte-array sub-array extraction*

```k
  rule <k> extract S L => .K ... </k>
       <stack> ARRAY : XS => substrBytes(ARRAY, S, S +Int L) : XS </stack>
    requires 0 <=Int S andBool S <=Int 255
     andBool 0 <Int L andBool L <=Int 255
     andBool L <=Int lengthBytes(ARRAY)
     andBool S +Int L <=Int lengthBytes(ARRAY)

  // If L is 0, then extract to the end of the byte-array.
  rule <k> extract S L => .K ... </k>
       <stack> ARRAY : XS => substrBytes(ARRAY, S, lengthBytes(ARRAY)) : XS </stack>
    requires 0 <=Int S andBool S <=Int 255
     andBool 0 ==Int L
     andBool S <=Int lengthBytes(ARRAY)

  rule <k> extract S L => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> ARRAY : _ </stack>
      requires S >Int lengthBytes(ARRAY)
        orBool S +Int L >Int lengthBytes(ARRAY)

  rule <k> extract S L => #panic(INVALID_ARGUMENT) ... </k>
      requires 0 >Int S orBool S >Int MAX_UINT8
       orBool  0 >Int L orBool L >Int MAX_UINT8
```

```k
  rule <k> extract3 => .K ... </k>
       <stack> C : B : ARRAY : XS => substrBytes(ARRAY, B, B +Int C) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires B <=Int lengthBytes(ARRAY)
     andBool B +Int C <=Int lengthBytes(ARRAY)

  rule <k> extract3 => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> C : B : ARRAY : _ </stack>
      requires B >Int lengthBytes(ARRAY)
        orBool B +Int C >Int lengthBytes(ARRAY)
```

*Byte-array uint extraction*

```k
  rule <k> extract_uint16 => .K ... </k>
       <stack> B : ARRAY : XS =>
               Bytes2Int(substrBytes(ARRAY, B, B +Int 2), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires B <=Int lengthBytes(ARRAY)
     andBool B +Int 2 <=Int lengthBytes(ARRAY)

  rule <k> extract_uint16 => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
      requires B >Int lengthBytes(ARRAY)
        orBool B +Int 2 >Int lengthBytes(ARRAY)
```

```k
  rule <k> extract_uint32 => .K ... </k>
       <stack> B : ARRAY : XS =>
               Bytes2Int(substrBytes(ARRAY, B, B +Int 4), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires B <=Int lengthBytes(ARRAY)
     andBool B +Int 4 <=Int lengthBytes(ARRAY)

  rule <k> extract_uint32 => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
      requires B >Int lengthBytes(ARRAY)
        orBool B +Int 4 >Int lengthBytes(ARRAY)
```

```k
  rule <k> extract_uint64 => .K ... </k>
       <stack> B : ARRAY : XS =>
               Bytes2Int(substrBytes(ARRAY, B, B +Int 8), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires B <=Int lengthBytes(ARRAY)
     andBool B +Int 8 <=Int lengthBytes(ARRAY)

  rule <k> extract_uint64 => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
      requires B >Int lengthBytes(ARRAY)
        orBool B +Int 8 >Int lengthBytes(ARRAY)
```

*bytes replacement*

```k
  rule <k> replace2 START:Int => . ... </k>
       <stack> B:Bytes : A:Bytes : XS => replaceAtBytes(A, START, B) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires START +Int lengthBytes(B) <=Int lengthBytes(A)

  rule <k> replace2 START:Int => #panic(BYTES_OVERFLOW) ... </k>
       <stack> B:Bytes : A:Bytes : _ </stack>
       <stacksize> _ </stacksize>
    requires START +Int lengthBytes(B) >Int lengthBytes(A)

  rule <k> replace3 => . ... </k>
       <stack> B:Bytes : START:Int : A:Bytes : XS => replaceAtBytes(A, START, B) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires START +Int lengthBytes(B) <=Int lengthBytes(A)

  rule <k> replace3 => #panic(BYTES_OVERFLOW) ... </k>
       <stack> B:Bytes : START:Int : A:Bytes : _ </stack>
       <stacksize> _ </stacksize>
    requires START +Int lengthBytes(B) >Int lengthBytes(A)
```


#### Byte-arrays as big-endian unsigned integers


The length of the arguments is limited to `MAX_BYTE_MATH_SIZE`, but there is no restriction on the length of the result.

```k
  rule <k> OP:MathByteOpCode => #panic(MATH_BYTES_ARG_TOO_LONG) ... </k>
       <stack> B:Bytes : A:Bytes : _ </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires (lengthBytes(A) >Int MAX_BYTE_MATH_SIZE
      orBool lengthBytes(B) >Int MAX_BYTE_MATH_SIZE)
     andBool notBool(isUnaryLogicalMathByteOpCode(OP))

  rule <k> _OP:UnaryLogicalMathByteOpCode => #panic(MATH_BYTES_ARG_TOO_LONG) ... </k>
       <stack> A:Bytes : _ </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) >Int MAX_BYTE_MATH_SIZE
```


##### Byte-array arithmetic operations

*Byte-array addition*

```k
  rule <k> b+ => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               Int2Bytes(Bytes2Int(A, BE, Unsigned) +Int Bytes2Int(B, BE, Unsigned), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
```

*Byte-array subtraction*
```k
  rule <k> b- => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               Int2Bytes(Bytes2Int(A, BE, Unsigned) -Int Bytes2Int(B, BE, Unsigned), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
     andBool Bytes2Int(A, BE, Unsigned) -Int Bytes2Int(B, BE, Unsigned) >=Int 0

  rule <k> b- => #panic(INT_UNDERFLOW) ... </k>
       <stack> B:Bytes : A:Bytes : _ </stack>
    requires Bytes2Int(A, BE, Unsigned) -Int Bytes2Int(B, BE, Unsigned) <Int 0
```

*Byte-array division*
```k
  rule <k> b/ => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               Int2Bytes(Bytes2Int(A, BE, Unsigned) /Int Bytes2Int(B, BE, Unsigned), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
     andBool Bytes2Int(B, BE, Unsigned) >Int 0

  rule <k> b/ => #panic(DIV_BY_ZERO) ... </k>
       <stack> B:Bytes : _:Bytes : _  </stack>
    requires Bytes2Int(B, BE, Unsigned) ==Int 0
```

*Byte-array remainder*
```k
  rule <k> b% => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               Int2Bytes(Bytes2Int(A, BE, Unsigned) %Int Bytes2Int(B, BE, Unsigned), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
     andBool Bytes2Int(B, BE, Unsigned) >Int 0

  rule <k> b% => #panic(DIV_BY_ZERO) ... </k>
       <stack> B:Bytes : _:Bytes : _  </stack>
    requires Bytes2Int(B, BE, Unsigned) ==Int 0
```

*Byte-array multiplication*
```k
  rule <k> b* => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               Int2Bytes(Bytes2Int(A, BE, Unsigned) *Int Bytes2Int(B, BE, Unsigned), BE, Unsigned) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
```

##### Byte-array relational operations

```k
  rule <k> b< => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) <Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE

  rule <k> b> => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) >Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE

  rule <k> b<= => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) <=Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE

  rule <k> b>= => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) >=Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE

  rule <k> b== => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) ==Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE

  rule <k> b!= => .K ... </k>
       <stack> B:Bytes : A:Bytes : XS =>
               bool2Int (Bytes2Int(A, BE, Unsigned) =/=Int Bytes2Int(B, BE, Unsigned)) : XS
       </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) <=Int MAX_BYTE_MATH_SIZE
     andBool lengthBytes(B) <=Int MAX_BYTE_MATH_SIZE
```

##### Byte-array bit-wise boolean operations

In our model, we diverge form the [reference TEAL interpreter](https://github.com/algorand/go-algorand/blob/master/data/transactions/logic/eval.go) by computing the bit-wise logical operations on byte-arrays via interpreting the arrays as big-endian unsigned unbounded integers.

We implement the operations as follows:
* interpret the byte-arrays as unsigned big-endian unbounded integers;
* performing the bit-wise operation on the integers;
* convert the result into a byte-array;
* left-pad the result with zeroes to the length of the longest argument, if necessary.

```k
  rule <k> OP:BinaryLogicalMathByteOpCode => .K ... </k>
       <stack> B : A : XS => BytesBitwiseOp(A, B, OP) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  syntax Bytes ::= BytesBitwiseOp(Bytes, Bytes, BinaryLogicalMathByteOpCode) [function]

  rule BytesBitwiseOp(A, B, b|) =>
    padLeftBytes(Int2Bytes(Bytes2Int(A, BE, Unsigned) |Int Bytes2Int(B, BE, Unsigned), BE, Unsigned)
                , maxInt(lengthBytes(A), lengthBytes(B)), 0)

  rule BytesBitwiseOp(A, B, b&) =>
    padLeftBytes(Int2Bytes(Bytes2Int(A, BE, Unsigned) &Int Bytes2Int(B, BE, Unsigned), BE, Unsigned)
                , maxInt(lengthBytes(A), lengthBytes(B)), 0)

  rule BytesBitwiseOp(A, B, b^) =>
    padLeftBytes(Int2Bytes(Bytes2Int(A, BE, Unsigned) xorInt Bytes2Int(B, BE, Unsigned), BE, Unsigned)
                , maxInt(lengthBytes(A), lengthBytes(B)), 0)
```

We implement the bit-wise complement as the exclusive or of the argument with a byte-array with all bytes set to `0xff`:

```k
  rule <k> b~ => .K ... </k>
       <stack> A : XS => BytesBitwiseOp(A, padLeftBytes(.Bytes, lengthBytes(A), 255), b^) : XS </stack>
```

*Byte-array access and modification*

```k
  rule <k> getbyte => .K ... </k>
       <stack> B : ARRAY : XS => ARRAY[B] : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)

  rule <k> getbyte => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => .K ... </k>
       <stack> C : B : ARRAY : XS => ARRAY[B <- C] : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)
             andBool 0 <=Int C andBool C <=Int MAX_UINT8

  rule <k> setbyte => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => #panic(ILL_TYPED_STACK) ... </k>
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

 rule <k> setbit => #panic(ILL_TYPED_STACK) ... </k>
      <stack> C : _ : _:Bytes : _ </stack>
   requires notBool (0 <=Int C andBool C <Int 2)

 rule <k> setbit => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
      <stack> _ : B : ARRAY:Bytes : _ </stack>
   requires notBool (0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8)

  syntax Bytes ::= setBitInBytes(Bytes, Int, Int) [function]
  //--------------------------------------------------------
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
  //---------------------------------------------------
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

  rule <k> setbit => #panic(ILL_TYPED_STACK) ... </k>
       <stack> C : _ : _:Int : _ </stack>
    requires notBool (0 <=Int C andBool C <Int 2)

  rule <k> setbit => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> _ : B : _:Int : _ </stack>
    requires notBool (0 <=Int B andBool B <Int 64)
```

#### `getbit`

```k
 rule <k> getbit => .K ... </k>
      <stack> B : ARRAY:Bytes : XS => getBitFromBytes(ARRAY, B) : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8

 rule <k> getbit => #panic(INDEX_OUT_OF_BOUNDS) </k>
      <stack> B : ARRAY:Bytes : _ </stack>
    requires notBool (0 <=Int B andBool B <Int lengthBytes(ARRAY) *Int 8)

  syntax Int ::= getBitFromBytes(Bytes, Int) [function]
  //---------------------------------------------------
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

  rule <k> getbit => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
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

  rule <k> method METHOD => .K ... </k>
       <stack> XS => methodSelector(METHOD) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> _:PseudoOpCode => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```

#### Constant Loading Auxiliary Functions

```k
  syntax Map ::= genIntcBlockMap(Int, Int, TValueNeList) [function]
  //---------------------------------------------------------------
  rule genIntcBlockMap(N, I, V VL) =>
         I |-> V
         genIntcBlockMap(N -Int 1, I +Int 1, VL)
    requires N >Int 1

  rule genIntcBlockMap(1, I, V) => I |-> V

  syntax Map ::= genBytecBlockMap(Int, Int, TValuePairNeList) [function]
  //--------------------------------------------------------------------
  // Note: byte array size is ignored
  rule genBytecBlockMap(N, I, (_, V) VPL) =>
         I |-> V
         genBytecBlockMap(N -Int 1, I +Int 1, VPL)
    requires N >Int 1

  rule genBytecBlockMap(1, I, (_, V)) => I |-> V
```

Extract method selector from an API method description, see [the documentation](https://developer.algorand.org/docs/get-details/dapps/smart-contracts/ABI/?from_query=method#methods), and the [reference implementation](https://github.com/algorand/go-algorand/blob/0cb9a2e4f7470cbcb88039886d6e0f586102b545/data/transactions/logic/assembler.go#L804)

```k
  syntax TBytes ::= methodSelector(TBytes) [function, total]
  //------------------------------------------------------
  rule methodSelector(METHOD) => substrBytes(String2Bytes(Sha512_256raw(METHOD)), 0, 4)
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

  rule <k> bz L => jump(L) ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I <=Int 0

  rule <k> bz _ => .K ... </k>
       <stack> I : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I >Int 0

  rule <k> b L => jump(L) ... </k>

  // TODO: `return` used to consume the rest of the `<k>` cell. Now we have to preceed,
  //       but we will need to make sure that TEAL execution stops here, so
  //       we erase only the items of sort `TealExecutionOp`.
   rule <k> return ~> #incrementPC() ~> #fetchOpcode() => #finalizeExecution() ... </k>
        <stack> (I:Int) : _XS => I : .TStack </stack>
        <stacksize> _ => 1 </stacksize>

  rule <k> (_ :):LabelCode => .K ... </k>

  rule <k> assert => .K ... </k>
       <stack> (X:Int) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires X >Int 0

  rule <k> assert => #panic(ASSERTION_VIOLATION) ... </k>
       <stack> (X:Int) : _ </stack>
    requires X ==Int 0

  rule <k> assert => #panic(IMPOSSIBLE_NEGATIVE_NUMBER) ... </k>
       <stack> (X:Int) : _ </stack>
    requires X <Int 0
```

#### Jump internal rules

```k
  syntax KItem ::= jump(Label)
  //--------------------------
  rule <k> jump(L) => .K ... </k>
       <pc> _ => getLabelAddress(L) </pc>
       <jumped> _ => true </jumped>
       <labels> LL </labels>
    requires L in_labels LL

  rule <k> jump(L) => #panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires notBool (L in_labels LL)
```

### Subroutine call internal rules

A subroutine call in TEAL performs an unconditional jump to a target label and
records the next program counter value on the call stack.

Subroutines share the regular `<stack>` and `<scratch>` with the main TEAL program. Either could be used to pass arguments or return results.

```k
  //                          Next PC | Stack pointer | Num args | Num return vals
  syntax StackFrame ::= frame(Int,      Int,            Int,       Int           )
                      | frame(Int,      Int                                      )

  syntax Int ::= getStackPtr() [function]

  rule [[ getStackPtr() => PTR ]]
       <callStack> ListItem(frame(_, PTR, _, _)) ... </callStack>

  rule [[ getStackPtr() => PTR ]]
       <callStack> ListItem(frame(_, PTR)) ... </callStack>

  rule <k> callsub TARGET => callSubroutine(TARGET) ... </k>

  rule <k> retsub => returnSubroutine() ... </k>

  syntax KItem ::= callSubroutine(Label)
  //------------------------------------
  // TODO: what happens if the pc value after call is invalid? What to do? Terminate or panic?
  // For now we do nothing, and thus trigger termination via `#fetchInstruction()`.
  rule <k> callSubroutine(TARGET) => .K ... </k>
       <pc> PC => getLabelAddress(TARGET) </pc>
       <jumped> _ => true </jumped>
       <labels> LL </labels>
       <stack> S </stack>
       <callStack> XS => ListItem(frame(PC +Int 1, #sizeTStack(S))) XS </callStack>
    requires  (TARGET in_labels LL)
      andBool (size(XS) <Int MAX_CALLSTACK_DEPTH)

  rule <k> callSubroutine(_TARGET) => #panic(CALLSTACK_OVERFLOW) ... </k>
       <callStack> XS </callStack>
    requires size(XS) >=Int MAX_CALLSTACK_DEPTH

  rule <k> callSubroutine(TARGET) => #panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires notBool(TARGET in_labels LL)

  syntax KItem ::= returnSubroutine()
  //---------------------------------
  rule <k> returnSubroutine() => .K ... </k>
       <pc> _ => RETURN_PC </pc>
       <jumped> _ => true </jumped>
       <stack> S => #let CLRSTCK = #drop((#sizeTStack(S) -Int STACK_PTR) -Int RETS, S) #in
             (#take(RETS, CLRSTCK) #drop(ARGS +Int RETS, CLRSTCK))
       </stack>
       <stacksize> SIZE => SIZE -Int (#sizeTStack(S) -Int STACK_PTR) -Int RETS </stacksize>
       <callStack> ListItem(frame(RETURN_PC, STACK_PTR, ARGS, RETS)) XS => XS </callStack>

  rule <k> returnSubroutine() => .K ... </k>
       <pc> _ => RETURN_PC </pc>
       <jumped> _ => true </jumped>
       <callStack> ListItem(frame(RETURN_PC, _)) XS => XS </callStack>

  rule <k> returnSubroutine() => #panic(CALLSTACK_UNDERFLOW) ... </k>
       <pc> _ </pc>
       <callStack> .List </callStack>

  rule <k> proto ARGS RETS => . ... </k>
       <callStack> ListItem(frame(_, _, _ => ARGS, _ => RETS)) ... </callStack>
    requires (ARGS >=Int 0) andBool (RETS >=Int 0)

  rule <k> proto ARGS RETS => . ... </k>
       <callStack> ListItem(frame(RETURN_PC, STACK_PTR) => frame(RETURN_PC, STACK_PTR, ARGS, RETS)) ... </callStack>
    requires (ARGS >=Int 0) andBool (RETS >=Int 0)

  rule <k> frame_dig N => . ... </k>
       <stack> XS => XS{getStackPtr() +Int N} : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> frame_bury N => . ... </k>
       <stack> X : XS => XS{getStackPtr() +Int N <- X} </stack>
       <stacksize> S => S -Int 1 </stacksize>

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

  rule <k> dup => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> dup2 => .K ... </k>
       <stack> V2 : V1 : XS => V2 : V1 : V2 : V1 : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
    requires S +Int 1 <Int MAX_STACK_DEPTH

  rule <k> dup2 => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S +Int 1 >=Int MAX_STACK_DEPTH

  rule <k> dig N => .K ... </k>
       <stack> STACK => STACK[N]:STACK </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH andBool
             0 <=Int N andBool N <Int S

  rule <k> dig _ => #panic(STACK_OVERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> dig N => #panic(STACK_UNDERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> cover N => .K ... </k>
       <stack> X : STACK => #take(N, STACK) (X : #drop(N, STACK)) </stack>
       <stacksize> S </stacksize>
    requires 0 <=Int N andBool N <Int S

  rule <k> cover N => #panic(STACK_UNDERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> uncover N => .K ... </k>
       <stack> STACK => STACK [ N ] : (#take(N, STACK) #drop(N +Int 1, STACK)) </stack>
       <stacksize> S </stacksize>
    requires 0 <=Int N andBool N <Int S

  rule <k> uncover N => #panic(STACK_UNDERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> swap => .K ... </k>
       <stack> X : Y : XS => Y : X : XS </stack>

  rule <k> swap => #panic(STACK_UNDERFLOW) ... </k>
       <stack> _:.TStack </stack>

  rule <k> select => .K ... </k>
       <stack> A : B : _ : XS =>
               B : XS
       </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires int2Bool(A)

  rule <k> select => .K ... </k>
       <stack> A : _ : C : XS =>
               C : XS
       </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires notBool (int2Bool(A))

  rule <k> bury N:Int => . ... </k>
       <stack> A:TValue : STACK => (#take(N -Int 1, STACK) A : #drop(N, STACK)) </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires 0 <Int N andBool N <Int S

  rule <k> bury N:Int => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires notBool(0 <Int N andBool N <Int S)

  rule <k> popn N:Int => . ... </k>
       <stack> STACK => #drop(N, STACK) </stack>
       <stacksize> S => S -Int N </stacksize>
    requires N <=Int S

  rule <k> popn N:Int => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires N >Int S

  rule <k> dupn N => dupn (N -Int 1) ... </k>
       <stack> X : XS => X : X : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires N >Int 0
     andBool S <Int MAX_STACK_DEPTH

  rule <k> dupn 0 => . ... </k>

  rule <k> dupn N => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S +Int N >Int MAX_STACK_DEPTH
```

### Blockchain State Accessors

```k
  rule <k> txn I => gtxn getTxnGroupIndex(getCurrentTxn()) I ... </k>

  rule <k> txn I J => txna I J ... </k>

  rule <k> gtxn G I => loadFromGroup(G, I) ... </k>

  rule <k> gtxns I => loadFromGroup(G, I) ... </k>
       <stack> G : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> txna I J => gtxna getTxnGroupIndex(getCurrentTxn()) I J ... </k>

  rule <k> txnas I => gtxnas getTxnGroupIndex(getCurrentTxn()) I ... </k>

  rule <k> gtxna G I J => loadFromGroup(G, I, J) ... </k>

  rule <k> gtxnas G I => loadFromGroup(G, I, J) ... </k>
       <stack> J : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> gtxnsa I J => loadFromGroup(G, I, J) ... </k>
       <stack> G : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> gtxnsas I => loadFromGroup(G, I, J) ... </k>
       <stack> J : G : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>

  rule <k> global I => .K ... </k>
       <stack> XS => getGlobalField(I) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH

  rule <k> _:BlockchainOpCode => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  syntax KItem ::= loadFromGroup(Int, TxnField)
  //-------------------------------------------
  rule <k> loadFromGroup(GROUP_IDX, FIELD) => . ... </k>
       <stacksize> S => S +Int 1 </stacksize>
       <stack> XS => fromMaybeTVal(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD)) : XS </stack>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         <groupIdx> CURRENT_GROUP_IDX </groupIdx>
         ...
       </transaction>
    requires isTValue(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD))
    andBool    S <Int MAX_STACK_DEPTH
    andBool    (notBool(isTxnDynamicField(FIELD))
    orElseBool GROUP_IDX <Int (CURRENT_GROUP_IDX))

  rule <k> loadFromGroup(GROUP_IDX, _:TxnDynamicField) => #panic(FUTURE_TXN) ...</k>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupIdx> CURRENT_GROUP_IDX </groupIdx>
         ...
       </transaction>
    requires GROUP_IDX >=Int CURRENT_GROUP_IDX

  rule <k> loadFromGroup(_, _) => #panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> loadFromGroup(GROUP_IDX, FIELD) => #panic(TXN_ACCESS_FAILED) ...</k>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         ...
       </transaction>
    requires notBool(isTValue(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD)))

  syntax TValue ::= fromMaybeTVal(MaybeTValue) [function]

  rule fromMaybeTVal(V:TValue) => V

  syntax KItem ::= loadFromGroup(Int, TxnaField, Int)
  //-------------------------------------------------
  rule <k> loadFromGroup(GROUP_IDX, FIELD, IDX) => . ...</k>
       <stack> XS => fromMaybeTVal(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD, IDX)) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         <groupIdx> CURRENT_GROUP_IDX </groupIdx>
         ...
       </transaction>
    requires   isTValue(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD, IDX))
    andBool    S <Int MAX_STACK_DEPTH
    andBool    (notBool(isTxnaDynamicField(FIELD))
    orElseBool GROUP_IDX <Int CURRENT_GROUP_IDX)

  rule <k> loadFromGroup(GROUP_IDX, _:TxnaDynamicField, _) => #panic(FUTURE_TXN) ...</k>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupIdx> CURRENT_GROUP_IDX </groupIdx>
         ...
       </transaction>
    requires GROUP_IDX >=Int CURRENT_GROUP_IDX

  rule <k> loadFromGroup(_, _, _) => #panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> loadFromGroup(GROUP_IDX, FIELD, IDX) => #panic(TXN_ACCESS_FAILED) ...</k>
       <currentTx> CURRENT_TX_ID </currentTx>
       <transaction>
         <txID> CURRENT_TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         ...
       </transaction>
    requires   notBool(isTValue(getGroupFieldByIdx(GROUP_ID, GROUP_IDX, FIELD, IDX)))
```

```k
  rule <k> load I => .K ... </k>
       <stack> XS => ({M[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <scratch> M </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)
     andBool S <Int MAX_STACK_DEPTH

  rule <k> load I => .K ... </k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <scratch> M => M[I <- 0] </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool notBool (I in_keys(M))
     andBool S <Int MAX_STACK_DEPTH

  rule <k> store I => .K ... </k>
       <stack> V : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <scratch> M => M[I <- V] </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE

  rule <k> load I => #panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> load _ => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> store I => #panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> loads => .K ... </k>
       <stack> I : XS => ({M[I]}:>TValue) : XS </stack>
       <scratch> M </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)

  rule <k> loads => .K ... </k>
       <stack> I : XS => 0 : XS </stack>
       <scratch> M </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool notBool(I in_keys(M))

  rule <k> loads => #panic(INVALID_SCRATCH_LOC) ... </k>
       <stack> I : _ </stack>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> stores => .K ... </k>
       <stack> V : I : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <scratch> M => M[I <- V] </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE

  rule <k> stores => #panic(INVALID_SCRATCH_LOC) ... </k>
       <stack> _ : I : _ </stack>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

```

Stateless TEAL Operations
-------------------------

### Logic Signature Argument Accessors

```k
//  rule <k> arg I => .K ... </k>
//       <stack> XS => ({getArgument(I)}:>TValue) : XS </stack>
//       <stacksize> S => S +Int 1 </stacksize>
//    requires S <Int MAX_STACK_DEPTH
//     andBool isTValue(getArgument(I))
//
//  rule <k> args => .K ... </k>
//       <stack> I : XS => ({getArgument(I)}:>TValue) : XS </stack>
//    requires isTValue(getArgument(I))
//
//  rule <k> arg I => #panic(INDEX_OUT_OF_BOUNDS) ... </k>
//       <stacksize> S </stacksize>
//    requires S <Int MAX_STACK_DEPTH
//     andBool notBool (isTValue(getArgument(I)))
//
//  rule <k> arg _ => #panic(STACK_OVERFLOW) ... </k>
//       <stacksize> S </stacksize>
//    requires S >=Int MAX_STACK_DEPTH
//
//  rule <k> arg_0 => arg 0 ... </k>
//  rule <k> arg_1 => arg 1 ... </k>
//  rule <k> arg_2 => arg 2 ... </k>
//  rule <k> arg_3 => arg 3 ... </k>
```

Stateful TEAL Operations
------------------------

### Application State Accessors

*balance*

```k
  rule <k> balance => #balance getAccountParamsField(AcctBalance, {accountReference(A)}:>TValue) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> balance => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  syntax KItem ::= "#balance" MaybeTValue
  
  rule <k> #balance BAL:TUInt64 => . ...</k>
       <stack> _ : XS => BAL : XS </stack>
      
  rule <k> #balance _ => #panic(TXN_ACCESS_FAILED) </k>  [owise]
```

*min_balance*

```k
  rule <k> min_balance => #min_balance getAccountParamsField(AcctMinBalance, {accountReference(A)}:>TValue) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> min_balance => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  syntax KItem ::= "#min_balance" MaybeTValue
  
  rule <k> #min_balance MIN_BAL:TUInt64 => . ...</k>
       <stack> _ : XS => MIN_BAL : XS </stack>
      
  rule <k> #min_balance _ => #panic(TXN_ACCESS_FAILED) </k>  [owise]
```

*log*

```k
  rule <k> log => . ...</k>
       <stack> (MSG:TBytes : XS) => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <logData> LOG => append(MSG, LOG) </logData>
         <logSize> SIZE => SIZE +Int lengthBytes({MSG}:>Bytes) </logSize>
         ...
       </transaction>
    requires size(LOG) <Int PARAM_MAX_LOG_CALLS

   rule <k> log => #panic(ILL_TYPED_STACK) ...</k>
        <stack> _:TUInt64 : _ </stack>

   rule <k> log => #panic(LOG_CALLS_EXCEEDED) ...</k>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <logData> LOG </logData>
         ...
       </transaction>
    requires size(LOG) >=Int PARAM_MAX_LOG_CALLS

   rule <k> log => #panic(LOG_SIZE_EXCEEDED) ...</k>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <logSize> SIZE </logSize>
         ...
       </transaction>
    requires SIZE >=Int PARAM_MAX_LOG_SIZE
```

*app_opted_in*

```k
  rule <k> app_opted_in =>
           #app_opted_in hasOptedInApp({appReference(APP)}:>TValue, {accountReference(A)}:>TValue) ... </k>
       <stack> (APP:Int) : (A:TValue) : _ </stack>
    requires isTValue(appReference(APP)) andBool isTValue(accountReference(A))

  rule <k> app_opted_in  => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> APP:Int : A:TValue : _:TStack </stack>
    requires notBool (isTValue(appReference(APP)) andBool isTValue(accountReference(A)))

  rule <k> app_opted_in => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:TBytes : _:TValue : _:TStack </stack>

  syntax KItem ::= "#app_opted_in" Bool
  //-----------------------------------
  rule <k> #app_opted_in B => .K ... </k>
       <stack> _ : _ : XS => (#if B #then 1 #else 0 #fi) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
```

*app_local_get*

```k
  rule <k> app_local_get =>
           #app_local_get getAppLocal({accountReference(A)}:>TValue
                                     , getGlobalField(CurrentApplicationID), KEY) ... </k>
       <stack> (KEY:Bytes) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> app_local_get => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_get => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:TUInt64 : _ : _ </stack>

  syntax KItem ::= "#app_local_get" MaybeTValue
  //--------------------------------------
  rule <k> #app_local_get V:TValue => .K ... </k>
       <stack> _ : _ : XS => V : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  syntax KItem ::= "#app_local_get" MaybeTValue
  //--------------------------------------
  rule <k> #app_local_get V:TValue => .K ... </k>
       <stack> _ : _ : XS => 0 : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isInt(V) andThenBool {V}:>Int <Int 0

  rule <k> #app_local_get NoTValue => #panic(TXN_ACCESS_FAILED) ... </k>
```

*app_local_get_ex*

```k
  rule <k> app_local_get_ex =>
           #app_local_get_ex getAppLocal({accountReference(A)}:>TValue, {appReference(APP)}:>TValue, KEY) ... </k>
       <stack> (KEY:Bytes) : (APP:TUInt64) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A)) andBool isTValue(appReference(APP))

  rule <k> app_local_get_ex => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (APP:TUInt64) : (A:TValue) : _ </stack>
    requires notBool (isTValue(accountReference(A)) andBool isTValue(appReference(APP)))

  rule <k> app_local_get_ex => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (APP:TValue) : (_:TValue) : _ </stack>
    requires isInt(KEY) orBool isBytes(APP)

  syntax KItem ::= "#app_local_get_ex" MaybeTValue
  //-----------------------------------------
  rule <k> #app_local_get_ex V => .K ... </k>
       <stack> _ : _ : _ : XS => 1 : V : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_local_get_ex V => .K ... </k>
       <stack> _ : _ : _ : XS => 0 : 0 : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isInt(V) andThenBool {V}:>Int <Int 0

  rule <k> #app_local_get_ex NoTValue => #panic(TXN_ACCESS_FAILED) ... </k>
```

*app_local_put*

```k
  syntax Int ::= getLocalByteLimit(Int) [function]
  rule [[ getLocalByteLimit(APP) => X ]]
       <app>
         <appID> APP </appID>
         <localNumBytes> X </localNumBytes>
         ...
       </app>

  syntax Int ::= getLocalIntLimit(Int) [function]
  rule [[ getLocalIntLimit(APP) => X ]]
       <app>
         <appID> APP </appID>
         <localNumInts> X </localNumInts>
         ...
       </app>

  rule <k> app_local_put => #app_local_put {accountReference(A)}:>TValue
                                           getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> app_local_put => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_put => #panic(ILL_TYPED_STACK) ...  </k>
       <stack> _:TValue : _:TUInt64 : _:TValue : _ </stack>

  syntax KItem ::= "#app_local_put" TValue TValue
  //---------------------------------------------
  rule <k> #app_local_put ADDR APP => .K ... </k>
       <stack> (NEWVAL:Int) : (KEY:Bytes) : _ : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> MI => MI[KEY <- NEWVAL] </localInts>
             <localBytes> MB => MB[KEY <- undef]  </localBytes>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>
    requires size(MI[KEY <- NEWVAL]) <=Int getLocalIntLimit(APP)
     andBool lengthBytes(KEY) <=Int PARAM_MAX_KEY_SIZE
     andBool lengthBytes(KEY) +Int sizeInBytes(NEWVAL) <=Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_local_put ADDR APP => .K ... </k>
       <stack> (NEWVAL:Bytes) : (KEY:Bytes) : _ : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> MI => MI[KEY <- undef] </localInts>
             <localBytes> MB => MB[KEY <- NEWVAL] </localBytes>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>
    requires size(MB[KEY <- NEWVAL]) <=Int getLocalByteLimit(APP)
     andBool lengthBytes(KEY) <=Int PARAM_MAX_KEY_SIZE
     andBool lengthBytes(KEY) +Int sizeInBytes(NEWVAL) <=Int PARAM_MAX_SUM_KEY_VALUE_SIZE
     andBool lengthBytes(NEWVAL) <=Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_local_put _ _ => #panic(KEY_TOO_LARGE) ... </k>
       <stack> _ : (KEY:Bytes) : _ : _ </stack>
    requires lengthBytes(KEY) >Int PARAM_MAX_KEY_SIZE

  rule <k> #app_local_put _ _ => #panic(KEY_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : _ : _ </stack>
    requires lengthBytes(KEY) +Int sizeInBytes(NEWVAL) >Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_local_put _ _ => #panic(BYTE_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:Bytes) : _ : _ : _ </stack>
    requires lengthBytes(NEWVAL) >Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_local_put ADDR APP => #panic(LOCAL_INTS_EXCEEDED) ... </k>
       <stack> (NEWVAL:Int) : (KEY:Bytes) : _ : _ </stack>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> M </localInts>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>
    requires size(M[KEY <- NEWVAL]) >Int getLocalIntLimit(APP)

  rule <k> #app_local_put ADDR APP => #panic(LOCAL_BYTES_EXCEEDED) ... </k>
       <stack> (NEWVAL:Bytes) : (KEY:Bytes) : _ : _ </stack>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localBytes> M </localBytes>
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>
    requires size(M[KEY <- NEWVAL]) >Int getLocalByteLimit(APP)

  // if the account exists but is not opted in, panic
  rule <k> #app_local_put ADDR APP => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> _ : _ : _ : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, panic
  rule <k> #app_local_put ADDR _ => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> _ : _ : _ : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))
```

*app_local_del*

```k
  rule <k> app_local_del => #app_local_del {accountReference(A)}:>TValue
                                           getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:Bytes) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> app_local_del => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes ) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_del => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:TUInt64 : _ : _ </stack>


  syntax KItem ::= "#app_local_del" TValue TValue
  //---------------------------------------------
  rule <k> #app_local_del ADDR APP => .K ... </k>
       <stack> (KEY:Bytes) : _ : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn>
           <optInApp>
             <optInAppID> APP </optInAppID>
             <localInts> MI => MI[KEY <- undef] </localInts> 
             <localBytes> MB => MB[KEY <- undef] </localBytes> 
             ...
           </optInApp> ...
         </appsOptedIn> ...
       </account>

  // if the account exists but is not opted in, panic.
  rule <k> #app_local_del ADDR APP => #panic(TXN_ACCESS_FAILED) ... </k>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, panic.
  rule <k> #app_local_del ADDR _ => #panic(TXN_ACCESS_FAILED) ... </k>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))
```

*app_global_get*

```k
  rule <k> app_global_get =>
           #app_global_get getAppGlobal(getAppCell({AC[{getGlobalField(CurrentApplicationID)}:>Int]}:>Bytes, {getGlobalField(CurrentApplicationID)}:>Int), KEY) ... </k>
       <stack> (KEY:Bytes) : _ </stack>
       <appCreator>
         AC
       </appCreator>

  syntax KItem ::= "#app_global_get" TValue
  //---------------------------------------
  rule <k> #app_global_get V => .K ... </k>
       <stack> (_:Bytes) : XS => V : XS </stack>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_global_get V => .K ... </k>
       <stack> (_:Bytes) : XS => 0 : XS </stack>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_global_get_ex*

```k

  syntax KItem ::= testAbc(Bytes, Int)
  rule <k> testAbc(CREATOR_ADDR, APP_ID) => getAppCell(CREATOR_ADDR, APP_ID) ... </k>

  syntax AppCell ::= getAppCell(Bytes, Int) [function]
  rule [[ getAppCell(CREATOR_ADDR, APP_ID) => <app> <appID> APP_ID </appID> APP_DATA </app> ]]
       <account>
         <address> CREATOR_ADDR </address>
         <app>
           <appID> APP_ID </appID>
           APP_DATA
         </app>
         ...
       </account>

  rule getAppCell(_, APP_ID) => <app> <appID> APP_ID </appID> ... </app> [owise]


  rule <k> app_global_get_ex =>
           #app_global_get_ex getAppGlobal(getAppCell({AC[{appReference(APP)}:>Int]}:>Bytes, {appReference(APP)}:>Int), KEY) ... </k>
       <stack> (KEY:Bytes) : (APP:TUInt64) : _ </stack>
       <appCreator>
         AC
       </appCreator>

    requires isTValue(appReference(APP))

  rule <k> app_global_get_ex => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (APP:TUInt64) : _ </stack>
    requires notBool isTValue(appReference(APP))

  rule <k> app_global_get_ex => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (KEY:TValue) : (I:TValue):_ </stack>
    requires isInt(KEY) orBool isBytes(I)

  syntax KItem ::= "#app_global_get_ex" TValue
  //------------------------------------------
  rule <k> #app_global_get_ex V  => .K ... </k>
       <stack> (_:Bytes) : (_:TUInt64) : XS => 1 : V : XS </stack>
    requires (notBool isInt(V)) orElseBool {V}:>Int >=Int 0

  rule <k> #app_global_get_ex V => .K ... </k>
       <stack> (_:Bytes) : (_:TUInt64) : XS => 0 : 0 : XS </stack>
    requires isInt(V) andThenBool {V}:>Int <Int 0
```

*app_global_put*

```k
  rule <k> app_global_put => #app_global_put getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:TValue) : (_:Bytes) : _ </stack>

  syntax KItem ::= "#app_global_put" TValue
  //---------------------------------------
  rule <k> #app_global_put APP => .K ... </k>
       <stack> (NEWVAL:Int) : (KEY:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <app>
         <appID> APP </appID>
         <globalState>
           <globalInts> MI => MI[KEY <- NEWVAL] </globalInts>
           <globalBytes> MB => MB[KEY <- undef] </globalBytes>
           <globalNumInts>    GLOBAL_INTS </globalNumInts>
           ...
         </globalState>
         ...
       </app>
    requires size(MI[KEY <- NEWVAL]) <=Int GLOBAL_INTS
     andBool lengthBytes(KEY) <=Int PARAM_MAX_KEY_SIZE
     andBool lengthBytes(KEY) +Int sizeInBytes(NEWVAL) <=Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_global_put APP => .K ... </k>
       <stack> (NEWVAL:Bytes) : (KEY:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <app>
         <appID> APP </appID>
         <globalState>
           <globalInts> MI => MI[KEY <- undef] </globalInts>
           <globalBytes> MB => MB[KEY <- NEWVAL] </globalBytes>
           <globalNumBytes>   GLOBAL_BYTES </globalNumBytes>
           ...
         </globalState>
         ...
       </app>
    requires size(MB[KEY <- NEWVAL]) <=Int GLOBAL_BYTES
     andBool lengthBytes(KEY) <=Int PARAM_MAX_KEY_SIZE
     andBool lengthBytes(KEY) +Int sizeInBytes(NEWVAL) <=Int PARAM_MAX_SUM_KEY_VALUE_SIZE
     andBool lengthBytes(NEWVAL) <=Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_global_put _ => #panic(KEY_TOO_LARGE) ... </k>
       <stack> _ : (KEY:Bytes) : _ </stack>
    requires lengthBytes(KEY) >Int PARAM_MAX_KEY_SIZE

  rule <k> #app_global_put _ => #panic(KEY_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : _ </stack>
    requires lengthBytes(KEY) +Int sizeInBytes(NEWVAL) >Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_global_put _ => #panic(BYTE_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:Bytes) : _ : _ </stack>
    requires lengthBytes(NEWVAL) >Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_global_put APP => #panic(GLOBAL_INTS_EXCEEDED) ... </k>
       <stack> (NEWVAL:Int) : (KEY:Bytes) : _ </stack>
       <app>
         <appID> APP </appID>
         <globalState>
           <globalInts> M </globalInts>
           <globalNumInts>    GLOBAL_INTS </globalNumInts>
           <globalNumBytes>   _ </globalNumBytes>
           ...
         </globalState>
         ...
       </app>
    requires size(M[KEY <- NEWVAL]) >Int GLOBAL_INTS

  rule <k> #app_global_put APP => #panic(GLOBAL_BYTES_EXCEEDED) ... </k>
       <stack> (NEWVAL:Bytes) : (KEY:Bytes) : _ </stack>
       <app>
         <appID> APP </appID>
         <globalState>
           <globalBytes> M </globalBytes>
           <globalNumInts>    _ </globalNumInts>
           <globalNumBytes>   GLOBAL_BYTES </globalNumBytes>
           ...
         </globalState>
         ...
       </app>
    requires size(M[KEY <- NEWVAL]) >Int GLOBAL_BYTES

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
  //---------------------------------------
  rule <k> #app_global_del APP => .K ... </k>
       <stack> (KEY:Bytes) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
       <appsCreated>
         <app>
           <appID> APP </appID>
           <globalState>
             <globalInts> MI => MI[KEY <- undef] </globalInts>
             <globalBytes> MB => MB[KEY <- undef] </globalBytes>
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
                                {accountReference(A)}:>TValue, 
                                {asaReference(ASSET)}:>TValue) 
           ... 
       </k>
       <stack> (ASSET:TUInt64) : (A:TValue): _ </stack>
    requires isTValue(accountReference(A)) andBool isTValue(asaReference(ASSET))

  rule <k> asset_holding_get _ => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (ASSET:TUInt64) : (A:TValue) : _ </stack>
    requires notBool (isTValue(accountReference(A)) andBool isTValue(asaReference(ASSET)))

  rule <k> asset_holding_get _ => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:TBytes : _ : _ </stack>

  syntax KItem ::= "#asset_holding_get" TValue
  // -----------------------------------------
  rule <k> #asset_holding_get RET => .K ... </k>
       <stack> (_:Int) : _ : XS => 1 : RET : XS </stack>
    requires {RET}:>Int >=Int 0

  // Return 0 if not opted in ASSET or the account is not found
  rule <k> #asset_holding_get RET => .K ... </k>
       <stack> (_:Int) : _ : XS => 0 : 0 : XS </stack>
    requires {RET}:>Int <Int 0
```

*asset_params_get*

```k
  rule <k> asset_params_get FIELD =>
           #asset_params_get getAssetParamsField(FIELD, {asaReference(A)}:>TValue)
       ...
       </k>
       <stack> (A:TUInt64) : XS => XS </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool isTValue(asaReference(A))

  rule <k> asset_params_get _ => #panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TUInt64) : _ </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (notBool isTValue(asaReference(A)))

  rule <k> asset_params_get _ => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> asset_params_get _ => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>

  syntax KItem ::= "#asset_params_get" TValue
  // ----------------------------------------
  rule <k> #asset_params_get RET => .K ... </k>
       <stack> XS => 1 : RET : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (notBool (isInt(RET)) orElseBool {RET}:>Int >=Int 0 )

  rule <k> #asset_params_get RET => .K ... </k>
       <stack> XS => 0 : 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (isInt(RET) andThenBool {RET}:>Int <Int 0)
```

*app_params_get*

```k
  rule <k> app_params_get FIELD => . ...</k>
       <stack> APP:Int : XS => 1 : {getAppParamsField(FIELD, APP)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires isTValue(getAppParamsField(FIELD, APP))
     andBool S <Int MAX_STACK_DEPTH

  rule <k> app_params_get FIELD => . ...</k>
       <stack> APP:Int : XS => 0 : 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires notBool(isTValue(getAppParamsField(FIELD, APP)))

  rule <k> app_params_get _ => #panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> app_params_get _ => #panic(STACK_UNDERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S <Int 1

  rule <k> app_params_get _ => #panic(ILL_TYPED_STACK) ...</k>
       <stack> _:Bytes : _ </stack>

```

*acct_params_get*

```k
  rule <k> acct_params_get FIELD => . ...</k>
       <stack> ACCT : XS => 1 : {getAccountParamsField(FIELD, {accountReference(ACCT)}:>TValue)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires (isTValue(accountReference(ACCT))
 andThenBool isTValue(getAccountParamsField(FIELD, {accountReference(ACCT)}:>TValue))
 andThenBool isInt(getAccountParamsField(AcctBalance, ACCT))
 andThenBool {getAccountParamsField(AcctBalance, ACCT)}:>Int >Int 0)
     andBool S <Int MAX_STACK_DEPTH

  rule <k> acct_params_get FIELD => . ...</k>
       <stack> ACCT : XS => 0 : {getAccountParamsField(FIELD, {accountReference(ACCT)}:>TValue)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires (isTValue(accountReference(ACCT))
 andThenBool isTValue(getAccountParamsField(FIELD, {accountReference(ACCT)}:>TValue))
 andThenBool isInt(getAccountParamsField(AcctBalance, ACCT))
 andThenBool {getAccountParamsField(AcctBalance, ACCT)}:>Int <=Int 0)
     andBool S <Int MAX_STACK_DEPTH

  rule <k> acct_params_get _ => #panic(TXN_ACCESS_FAILED) ...</k>
       <stack> ACCT : _ </stack>
    requires notBool(isTValue(accountReference(ACCT)))

  rule <k> acct_params_get _ => #panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> acct_params_get _ => #panic(STACK_UNDERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S <Int 1
```

### Box storage

*box_create*

```k
  rule <k> box_create => #createBox(NAME, {boxAcct(NAME)}:>Bytes, SIZE) ... </k>
       <stack> SIZE:Int : NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires isBytes(boxAcct(NAME))

  syntax KItem ::= "#createBox" "(" Bytes "," Bytes "," Int ")"

  rule <k> #createBox(NAME, ADDR, SIZE) => . ... </k>
       <stack> XS => 1 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           (.Bag =>
           <box>
             <boxName> NAME </boxName>
             <boxData> padLeftBytes(.Bytes, SIZE, 0) </boxData>
           </box>)
           REST
         </boxes>
         <minBalance> MIN_BALANCE => MIN_BALANCE +Int (2500 +Int (400 *Int (lengthBytes(NAME) +Int SIZE))) </minBalance>
         ...
       </account>
    requires SIZE <=Int PARAM_MAX_BOX_SIZE
     andBool notBool(NAME in_boxes(<boxes> REST </boxes>))
     andBool ADDR ==K getGlobalField(CurrentApplicationAddress) // Can only create a box in your own application

  rule <k> #createBox(NAME, ADDR, SIZE) => . ... </k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           <box>
             <boxName> NAME </boxName>
             <boxData> BYTES </boxData>
           </box>
           ...
         </boxes>
         ...
       </account>
    requires SIZE <=Int PARAM_MAX_BOX_SIZE
     andBool lengthBytes(BYTES) ==Int SIZE

  rule <k> #createBox(NAME, ADDR, SIZE) => #panic(CHANGED_BOX_SIZE) ... </k>
       <account>
         <address> ADDR </address>
         <boxes>
           <box>
             <boxName> NAME </boxName>
             <boxData> BYTES </boxData>
           </box>
           ...
         </boxes>
         ...
       </account>
    requires SIZE <=Int PARAM_MAX_BOX_SIZE
     andBool lengthBytes(BYTES) =/=Int SIZE

  rule <k> #createBox(_, ADDR, _) => #panic(BOX_CREATE_EXTERNAL) ... </k>
    requires ADDR =/=K getGlobalField(CurrentApplicationAddress)

  rule <k> box_create => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> _:Int : NAME:Bytes : _</stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_create => #panic(BOX_TOO_LARGE) ... </k>
       <stack> SIZE:Int : _ : _ </stack>
    requires SIZE >Int PARAM_MAX_BOX_SIZE

  rule <k> box_create => #panic(ILL_TYPED_STACK) ... </k>
       <stack> SIZE : NAME : _ </stack>
    requires isBytes(SIZE) orBool isInt(NAME)

  rule <k> box_create => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 2
```

*box_replace*

```k
  syntax KItem ::= "#boxReplace" "(" Bytes "," Bytes "," Int "," Bytes ")"

  rule <k> box_replace => #boxReplace(NAME, {boxAcct(NAME)}:>Bytes, OFFSET, VAL) ... </k>
       <stack> VAL:Bytes : OFFSET:Int : NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxReplace(NAME, ADDR, OFFSET, VAL) => . ...</k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES => replaceAtBytes(BYTES, OFFSET, VAL) </boxData>
         </box>
         ...
       </account>
    requires (lengthBytes(VAL) +Int OFFSET) <Int lengthBytes(BYTES)

  rule <k> #boxReplace(NAME, ADDR, OFFSET, VAL) => #panic(BOX_OUT_OF_BOUNDS) ...</k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires (lengthBytes(VAL) +Int OFFSET) >=Int lengthBytes(BYTES)

  rule <k> #boxReplace(NAME, ADDR, _, _) => #panic(BOX_NOT_FOUND) ...</k>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> box_replace => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> _:Bytes : _:Int : NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_replace => #panic(ILL_TYPED_STACK) ... </k>
       <stack> VAL : OFFSET : NAME : _ </stack>
    requires isInt(VAL) orBool isBytes(OFFSET) orBool isInt(NAME)

  rule <k> box_replace => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 3
```

*box_put*

```k
  syntax KItem ::= "#boxPut" "(" Bytes "," Bytes "," Bytes ")"

  rule <k> box_put => #boxPut(NAME, {boxAcct(NAME)}:>Bytes, VAL) ... </k>
       <stack> VAL:Bytes : NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxPut(NAME, ADDR, VAL) => . ...</k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES => VAL </boxData>
         </box>
         ...
       </account>
    requires lengthBytes(VAL) ==Int lengthBytes(BYTES)

  rule <k> #boxPut(NAME, ADDR, VAL) => #panic(BOX_WRONG_LENGTH) ...</k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires lengthBytes(VAL) =/=Int lengthBytes(BYTES)

  rule <k> #boxPut(NAME, ADDR, VAL) => #createBox(NAME, ADDR, lengthBytes(VAL)) ~> #boxPut(NAME, ADDR, VAL) ...</k>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> box_put => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> _:Bytes : NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_put => #panic(ILL_TYPED_STACK) ... </k>
       <stack> VAL : NAME : _ </stack>
    requires isInt(VAL) orBool isInt(NAME)

  rule <k> box_put => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 2
```

*box_extract*

```k
  syntax KItem ::= "#boxExtract" "(" Bytes "," Bytes "," Int "," Int ")"

  rule <k> box_extract => #boxExtract(NAME, {boxAcct(NAME)}:>Bytes, OFFSET, LENGTH) ... </k>
       <stack> LENGTH:Int : OFFSET:Int : NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxExtract(NAME, ADDR, OFFSET, LENGTH) => . ... </k>
       <stack> XS => substrBytes(BYTES, OFFSET, OFFSET +Int LENGTH) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires (LENGTH +Int OFFSET) <Int lengthBytes(BYTES)

  rule <k> #boxExtract(NAME, ADDR, OFFSET, LENGTH) => #panic(BOX_OUT_OF_BOUNDS) ... </k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires (LENGTH +Int OFFSET) >=Int lengthBytes(BYTES)

  rule <k> #boxExtract(NAME, ADDR, _, _) => #panic(BOX_NOT_FOUND) ... </k>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> box_extract => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> _:Int : _:Int : NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_extract => #panic(ILL_TYPED_STACK) ... </k>
       <stack> LENGTH : OFFSET : NAME : _ </stack>
    requires isBytes(LENGTH) orBool isBytes(OFFSET) orBool isInt(NAME)

  rule <k> box_extract => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 3
```

*box_get*

```k
  syntax KItem ::= "#boxGet" "(" Bytes "," Bytes ")"

  rule <k> box_get => #boxGet(NAME, {boxAcct(NAME)}:>Bytes) ... </k>
       <stack> NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxGet(NAME, ADDR) => . ... </k>
       <stack> XS => 1 : BYTES : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires lengthBytes(BYTES) <Int MAX_BYTEARRAY_LEN

  rule <k> #boxGet(NAME, ADDR) => . ... </k>
       <stack> XS => 0 : .Bytes : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> #boxGet(NAME, ADDR) => #panic(BYTES_OVERFLOW) ... </k>
       <account>
         <address> ADDR </address>
         <box>
           <boxName> NAME </boxName>
           <boxData> BYTES </boxData>
         </box>
         ...
       </account>
    requires lengthBytes(BYTES) >=Int MAX_BYTEARRAY_LEN

  rule <k> box_get => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_get => #panic(ILL_TYPED_STACK) ... </k>
       <stack> NAME : _ </stack>
    requires isInt(NAME)

  rule <k> box_get => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 1
```

*box_len*

```k
  syntax KItem ::= "#boxLen" "(" Bytes "," Bytes ")"

  rule <k> box_len => #boxLen(NAME, {boxAcct(NAME)}:>Bytes) ... </k>
       <stack> NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxLen(NAME, ADDR) => . ... </k>
       <stack> XS => 1 : lengthBytes(BYTES) : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           <box>
             <boxName> NAME </boxName>
             <boxData> BYTES </boxData>
           </box>
           ...
         </boxes>
         ...
       </account>

  rule <k> #boxLen(NAME, ADDR) => . ... </k>
       <stack> XS => 0 : 0 : XS </stack>
       <stacksize> S => S +Int 2 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> box_len => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_len => #panic(ILL_TYPED_STACK) ... </k>
       <stack> NAME : _ </stack>
    requires isInt(NAME)

  rule <k> box_len => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 1
```

*box_del*

```k
  syntax KItem ::= "#boxDel" "(" Bytes "," Bytes ")"

  rule <k> box_del => #boxDel(NAME, {boxAcct(NAME)}:>Bytes) ... </k>
       <stack> NAME:Bytes : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires isBytes(boxAcct(NAME))

  rule <k> #boxDel(NAME, ADDR) => . ... </k>
       <stack> XS => 1 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           ((<box>
             <boxName> NAME </boxName>
             <boxData> BYTES </boxData>
           </box>) => .Bag)
           ...
         </boxes>
         <minBalance> MIN_BALANCE => MIN_BALANCE -Int (2500 +Int (400 *Int (lengthBytes(NAME) +Int
         lengthBytes(BYTES)))) </minBalance>
         ...
       </account>

  rule <k> #boxDel(NAME, ADDR) => . ... </k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <account>
         <address> ADDR </address>
         <boxes>
           BOXES
         </boxes>
         ...
       </account>
    requires notBool(NAME in_boxes(<boxes> BOXES </boxes>))

  rule <k> box_del => #panic(BOX_UNAVAILABLE) ... </k>
       <stack> NAME:Bytes : _ </stack>
    requires boxAcct(NAME) ==K NoTValue

  rule <k> box_del => #panic(ILL_TYPED_STACK) ... </k>
       <stack> NAME : _ </stack>
    requires isInt(NAME)

  rule <k> box_del => #panic(STACK_UNDERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S <Int 1
```

### Access to past transactions in the group

*gaid*

```k
  rule <k> gaid T:Int => .K ... </k>
       <stack> XS => {getGroupFieldByIdx( getTxnGroupID(getCurrentTxn()), T, ApplicationID)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool T <Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int
     andBool ({getGroupFieldByIdx(getTxnGroupID(getCurrentTxn()), T, TypeEnum)}:>Int) ==Int (@ appl)

  rule <k> gaid T => #panic(FUTURE_TXN) ... </k>
     requires T >=Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int
     orBool ({getGroupFieldByIdx(getTxnGroupID(getCurrentTxn()), T, TypeEnum)}:>Int) =/=Int (@ appl)
```

*gaids*

```k

  rule <k> gaids => .K ... </k>
       <stack> T:Int : XS => {getGroupFieldByIdx( getTxnGroupID(getCurrentTxn()), T, ApplicationID)}:>TValue : XS </stack>
    requires T <Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int
     andBool ({getGroupFieldByIdx(getTxnGroupID(getCurrentTxn()), T, TypeEnum)}:>Int) ==Int (@ appl)

  rule <k> gaids => #panic(FUTURE_TXN) ... </k>
       <stack> T:Int : _ </stack>
     requires T >=Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int
     orBool ({getGroupFieldByIdx(getTxnGroupID(getCurrentTxn()), T, TypeEnum)}:>Int) =/=Int (@ appl)
```

*gload, gloads, & gloadss*

```k
  rule <k> gload TXN_IDX I => loadGroupScratch(TXN_IDX, I) ...</k>

  rule <k> gloads I => loadGroupScratch(TXN_IDX, I) ... </k>
       <stack> (TXN_IDX:Int : XS) => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> gloadss => loadGroupScratch(TXN_IDX, I) ... </k>
       <stack> (I:Int : TXN_IDX:Int : XS) => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>

  syntax KItem ::= loadGroupScratch(Int, Int)
  //-----------------------------------------
  rule <k> loadGroupScratch(GROUP_IDX, I) => . ...</k>
       <stack> XS => ({M[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         ...
       </transaction>
       <transaction>
         <groupID> GROUP_ID </groupID>
         <groupIdx> GROUP_IDX </groupIdx>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)
     andBool S <Int MAX_STACK_DEPTH
     andBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(GROUP_IDX, I) => . ...</k>
       <stack> XS => ({M[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <groupIdx> GROUP_IDX </groupIdx>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)
     andBool S <Int MAX_STACK_DEPTH
     andBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(GROUP_IDX, I) => . ...</k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <groupID> GROUP_ID </groupID>
         ...
       </transaction>
       <transaction>
         <groupID> GROUP_ID </groupID>
         <groupIdx> GROUP_IDX </groupIdx>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool notBool (I in_keys(M))
     andBool S <Int MAX_STACK_DEPTH
     andBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(GROUP_IDX, I) => . ...</k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <groupIdx> GROUP_IDX </groupIdx>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool notBool (I in_keys(M))
     andBool S <Int MAX_STACK_DEPTH
     andBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(_, I) => #panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> loadGroupScratch(GROUP_IDX, _) => #panic(TXN_OUT_OF_BOUNDS) ... </k>
    requires GROUP_IDX <Int 0 orBool GROUP_IDX >=Int {getGlobalField(GroupSize)}:>Int

  rule <k> loadGroupScratch(GROUP_IDX, _) => #panic(FUTURE_TXN) ... </k>
    requires GROUP_IDX >=Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int
     andBool (GROUP_IDX >=Int 0 andBool GROUP_IDX <Int {getGlobalField(GroupSize)}:>Int)

  rule <k> loadGroupScratch(_, _) => #panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```

### Inner transaction opcodes

```k
  rule <k> itxn_begin => . ...</k>
       <innerTransactions>
         .List => 
         ListItem(<transaction>
           <txID> "" </txID>
           <txHeader>
             // TODO Fee is calculated dynamically
             <fee>         0                                         </fee>
             <sender>      getGlobalField(CurrentApplicationAddress) </sender>
             <firstValid>  getDefaultValue(FirstValid)  </firstValid>
             <lastValid>   getDefaultValue(LastValid)   </lastValid>
//           TODO: insert First/LastValid from parent TXN once we need them
//             <firstValid>  getTxnField(getCurrentTxn(), FirstValid)  </firstValid>
//             <lastValid>   getTxnField(getCurrentTxn(), LastValid)  </lastValid>
             <genesisHash> .Bytes                                    </genesisHash>
             <txType>       "unknown"                                </txType>
             <typeEnum>     0                                        </typeEnum>
             <groupID>      Int2String(GROUP_ID +Int 1)              </groupID>
             <groupIdx>     0                                        </groupIdx>
             <genesisID>    .Bytes                                   </genesisID>
             <lease>        .Bytes                                   </lease>
             <note>         .Bytes                                   </note>
             <rekeyTo>      PARAM_ZERO_ADDR                          </rekeyTo>
           </txHeader>
           <txnTypeSpecificFields>
             .Bag
           </txnTypeSpecificFields>
           ...
         </transaction>)
       </innerTransactions>
       <nextGroupID> GROUP_ID => GROUP_ID +Int 1 </nextGroupID>

  rule <k> (itxn_submit ~> #incrementPC() ~> #fetchOpcode()) => (#incrementPC() ~> #checkItxns(T) ~> #executeItxnGroup()) ...</k>
       <innerTransactions> T </innerTransactions>
       <lastTxnGroupID> _ => Int2String(GROUP_ID) </lastTxnGroupID>
       <nextGroupID> GROUP_ID </nextGroupID>

  rule <k> itxn_field FIELD => #setItxnField(FIELD, VAL) ...</k>
       <stack> VAL : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> itxn_next => . ...</k>
       <innerTransactions>
         REST:List
         (.List =>
         ListItem(<transaction>
           <txID> "" </txID>
           <txHeader>
             // TODO Fee is calculated dynamically
             <fee>         0                                         </fee>
             <sender>      getGlobalField(CurrentApplicationAddress) </sender>
             <firstValid>  getTxnField(getCurrentTxn(), FirstValid)  </firstValid>
             <lastValid>   getTxnField(getCurrentTxn(), LastValid)   </lastValid>
             <genesisHash> .Bytes                                    </genesisHash>
             <txType>       "unknown"                                </txType>
             <typeEnum>     0                                        </typeEnum>
             <groupID>      Int2String(GROUP_ID)                     </groupID>
             <groupIdx>     size(REST)                               </groupIdx>
             <genesisID>    .Bytes                                   </genesisID>
             <lease>        .Bytes                                   </lease>
             <note>         .Bytes                                   </note>
             <rekeyTo>      PARAM_ZERO_ADDR                          </rekeyTo>
           </txHeader>
           <txnTypeSpecificFields>
             .Bag
           </txnTypeSpecificFields>
           ...
         </transaction>))
       </innerTransactions>
       <nextGroupID> GROUP_ID </nextGroupID>
    requires size(REST) >=Int 1

  rule <k> itxn FIELD => gitxn getLastItxnGroupIdx() FIELD ...</k>

  rule <k> itxna FIELD IDX => gitxna getLastItxnGroupIdx() FIELD IDX ...</k>

  rule <k> gitxn GROUP_IDX FIELD => #loadFromGroupInner(GROUP_IDX, FIELD) ...</k>

  rule <k> gitxna GROUP_IDX FIELD IDX => #loadFromGroupInner(GROUP_IDX, FIELD, IDX) ...</k>

  rule <k> itxnas FIELD => gitxna getLastItxnGroupIdx() FIELD IDX ...</k>
       <stack> IDX : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> gitxnas GROUP_IDX FIELD => gitxna GROUP_IDX FIELD IDX ...</k>
       <stack> IDX : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
```



Panic Behaviors due to Ill-typed Stack Arguments
------------------------------------------------

### Crypto Opcodes

### Arithmetic/relational/logical/Bitwise Opcodes

```k
  rule <k> Op:OpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires (isBinaryArithOpCode(Op)         orBool
              isInequalityOpCode(Op)    orBool
              isBinaryLogicalOpCode(Op) orBool
              isBinaryBitOpCode(Op))
     andBool (isBytes(V2) orBool isBytes(V1))

  rule <k> Op:OpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>
    requires isUnaryLogicalOpCode(Op)

  rule <k> _:EqualityOpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires (isBytes(V1) andBool isInt(V2))
      orBool (isBytes(V2) andBool isInt(V1))
```

### Byte Opcodes
```k
  rule <k> OP:OpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> A : B : _ </stack>
    requires (isInt(A) orBool isInt(B))
     andBool (isArithmMathByteOpCode(OP)
     orBool   isRelationalMathByteOpCode(OP)
     orBool   isBinaryLogicalMathByteOpCode(OP))

  rule <k> OP:OpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> _:Int : _ </stack>
    requires isUnaryLogicalMathByteOpCode(OP)
  
  rule <k> len => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> itob => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>

  rule <k> btoi => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> concat => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires isInt(V2) orBool isInt(V1)

  rule <k> substring _ _ => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> substring3 => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (V:TValue) : (START:TValue) : (END:TValue) : _ </stack>
    requires isInt(V) orBool isBytes(START) orBool isBytes(END)
```

### Flow Control Opcodes
```k
  rule <k> Op:OpCode => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>
    requires isCondBranchOpCode(Op) orBool isReturnOpCode(Op)
```

### Application State Opcodes
```k
  rule <k> app_global_get => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> app_global_put => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:TValue) : (_:Int):_ </stack>

  rule <k> app_global_del => #panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>
```

### Signature Verification Opcode

Panic Behaviors due to Insufficient Stack Arguments
---------------------------------------------------

TODO: incorporate Bytes math opcodes

```k
  // Opcodes requiring at least three stack elements
  rule <k> Op:OpCode => #panic(STACK_UNDERFLOW) ... </k>
       <stack> (_:TValue) : (_:TValue) : .TStack </stack>
       <stacksize> 2 </stacksize>
    requires isTernaryStateOpCode(Op)
      orBool isTernaryByteOpCode(Op)
      orBool isSigVerOpCode(Op)
      orBool isTernaryStackOpCode(Op)

  // Opcodes requiring at least two stack elements
  rule <k> Op:OpCode => #panic(STACK_UNDERFLOW) ... </k>
       <stack> (_:TValue) : .TStack </stack>
       <stacksize> 1 </stacksize>
    requires isBinaryArithOpCode(Op)
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
  rule <k> Op:OpCode => #panic(STACK_UNDERFLOW) ... </k>
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
      orBool (isStackOpCode(Op) andBool notBool (isNullaryStackOpCode(Op)))
      orBool isStateOpCode(Op)
      orBool isSigVerOpCode(Op)

endmodule
```
