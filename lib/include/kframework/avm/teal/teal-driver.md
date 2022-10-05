```k
requires "krypto.md"

requires "avm/blockchain.md"
requires "avm/args.md"
requires "avm/avm-configuration.md"
requires "avm/avm-limits.md"
requires "avm/teal/teal-syntax.md"
requires "avm/teal/teal-stack.md"
requires "avm/teal/teal-execution.md"
```

TEAL Interpreter
================

```k
module TEAL-DRIVER
  imports AVM-CONFIGURATION
  imports AVM-LIMITS
  imports GLOBALS
  imports TEAL-INTERPRETER-STATE
  imports TEAL-EXECUTION
  imports TEAL-STACK
  imports KRYPTO
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

*Exponentiation*
```k
  rule <k> exp => .K ... </k>
       <stack> I2 : I1 : XS => (I1 ^Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I1 ^Int I2 <=Int MAX_UINT64
     andBool notBool (I1 ==Int 0 andBool I2 ==Int 0)

  rule <k> exp => panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ==Int 0 andBool I2 ==Int 0

  rule <k> exp => panic(INT_OVERFLOW) ... </k>
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

  rule <k> divmodw => panic(DIV_BY_ZERO) ... </k>
       <stack> I4 : I3 : _ : _ : _ </stack>
    requires I4 ==Int 0 andBool I3 ==Int 0

  // Auxilary funtion that interprets two `UInt64` as one Int, big-endian
  syntax Int ::= asUInt128(TUInt64, TUInt64) [function, functional]
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

  rule <k> expw => panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ==Int 0 andBool I2 ==Int 0

  rule <k> expw => panic(INT_OVERFLOW) ... </k>
       <stack> I2 : I1 : _ </stack>
    requires I1 ^Int I2 >Int MAX_UINT128
```

*Square root*

The largest integer B such that B^2 <= X

```k
  rule <k> sqrt => .K ... </k>
       <stack> X : XS => sqrtTUInt64(X) : XS </stack>
    requires X >=Int 0 andBool X <=Int MAX_UINT64

  rule <k> sqrt => panic(INVALID_ARGUMENT) ... </k>
       <stack> X : _ </stack>
    requires notBool( X >=Int 0 andBool X <=Int MAX_UINT64)
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

  rule <k> shl => panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : _ : _ </stack>
    requires notBool (I2 >=Int 0 andBool I2 <Int 64)

  rule <k> shr => .K ... </k>
       <stack> I2 : I1 : XS => (I1 >>Int I2) : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires I2 >=Int 0 andBool I2 <Int 64

  rule <k> shr => panic(INVALID_ARGUMENT) ... </k>
       <stack> I2 : _ : _ </stack>
    requires notBool (I2 >=Int 0 andBool I2 <Int 64)

  rule <k> ~ => .K ... </k>
       <stack> I : XS => (~Int I) : XS </stack>
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

  rule <k> bitlen => panic(INVALID_ARGUMENT) ... </k>
       <stack> (I:Int) : _ </stack>
    requires notBool (0 <=Int I andBool I <=Int MAX_UINT64)

  rule <k> bitlen => .K ... </k>
       <stack> (B:Bytes) : XS => 0 : XS </stack>
    requires lengthBytes(B) <=Int MAX_BYTEARRAY_LEN
     andBool Bytes2Int(B, BE, Unsigned) ==Int 0

  rule <k> bitlen => .K ... </k>
       <stack> (B:Bytes) : XS => log2Int(Bytes2Int(B, BE, Unsigned)) +Int 1 : XS </stack>
    requires lengthBytes(B) <=Int MAX_BYTEARRAY_LEN
     andBool Bytes2Int(B, BE, Unsigned) >Int 0

  rule <k> bitlen => panic(INVALID_ARGUMENT) ... </k>
       <stack> (B:Bytes) : _ </stack>
    requires lengthBytes(B) >Int MAX_BYTEARRAY_LEN
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
    requires lengthBytes(B1 +Bytes B2) <=Int MAX_BYTEARRAY_LEN

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

*Zero bytes*
```k
  rule <k> bzero => .K ... </k>
       <stack> X : XS => padLeftBytes(.Bytes, X, 0) : XS </stack>
    requires X <=Int MAX_BYTEARRAY_LEN

  rule <k> bzero => panic(INVALID_ARGUMENT) ... </k>
       <stack> X : _ </stack>
    requires X >Int MAX_BYTEARRAY_LEN
```

*Byte-array access and modification*

```k
  rule <k> getbyte => .K ... </k>
       <stack> ARRAY : B : XS => ARRAY[B] : XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)

  rule <k> getbyte => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> ARRAY : B : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => .K ... </k>
       <stack> ARRAY : B : C : XS => ARRAY[B <- C] : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires 0 <=Int B andBool B <Int lengthBytes(ARRAY)
             andBool 0 <=Int C andBool C <=Int MAX_UINT8

  rule <k> setbyte => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> ARRAY : B : _ </stack>
    requires 0 >Int B orBool B >=Int lengthBytes(ARRAY)

  rule <k> setbyte => panic(ILL_TYPED_STACK) ... </k>
       <stack> _ : _ : C : _ </stack>
    requires 0 >Int C orBool C >Int MAX_UINT8
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

  rule <k> extract S L => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> ARRAY : _ </stack>
      requires S >Int lengthBytes(ARRAY)
        orBool S +Int L >Int lengthBytes(ARRAY)

  rule <k> extract S L => panic(INVALID_ARGUMENT) ... </k>
      requires 0 >Int S orBool S >Int MAX_UINT8
       orBool  0 >Int L orBool L >Int MAX_UINT8
```

```k
  rule <k> extract3 => .K ... </k>
       <stack> C : B : ARRAY : XS => substrBytes(ARRAY, B, B +Int C) : XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
    requires B <=Int lengthBytes(ARRAY)
     andBool B +Int C <=Int lengthBytes(ARRAY)

  rule <k> extract3 => panic(INDEX_OUT_OF_BOUNDS) ... </k>
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

  rule <k> extract_uint16 => panic(INDEX_OUT_OF_BOUNDS) ... </k>
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

  rule <k> extract_uint32 => panic(INDEX_OUT_OF_BOUNDS) ... </k>
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

  rule <k> extract_uint64 => panic(INDEX_OUT_OF_BOUNDS) ... </k>
       <stack> B : ARRAY : _ </stack>
      requires B >Int lengthBytes(ARRAY)
        orBool B +Int 8 >Int lengthBytes(ARRAY)
```

#### Byte-arrays as big-endian unsigned integers


The length of the arguments is limited to `MAX_BYTE_MATH_SIZE`, but there is no restriction on the length of the result.

```k
  rule <k> _OP:MathByteOpCode => panic(MATH_BYTES_ARG_TOO_LONG) ... </k>
       <stack> B:Bytes : A:Bytes : _ </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires lengthBytes(A) >Int MAX_BYTE_MATH_SIZE
      orBool lengthBytes(B) >Int MAX_BYTE_MATH_SIZE

  rule <k> _OP:UnaryLogicalMathByteOpCode => panic(MATH_BYTES_ARG_TOO_LONG) ... </k>
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

  rule <k> b- => panic(INT_UNDERFLOW) ... </k>
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
     andBool lengthBytes(B) >Int 0

  rule <k> b/ => panic(DIV_BY_ZERO) ... </k>
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
     andBool lengthBytes(B) >Int 0

  rule <k> b% => panic(DIV_BY_ZERO) ... </k>
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
   rule <k> return ~> X::TealExecutionOp => #finalizeExecution() ... </k>
        <stack> (I:Int) : _XS => I : .TStack </stack>
        <stacksize> _ => 1 </stacksize>
    requires notBool isTxnCommand(X)

  rule <k> _: => .K ... </k>

  rule <k> assert => .K ... </k>
       <stack> (X:Int) : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>
    requires X >=Int 0

  rule <k> assert => panic(ASSERTION_VIOLATION) ... </k>
       <stack> (X:Int) : _ </stack>
    requires X ==Int 0

  rule <k> assert => panic(IMPOSSIBLE_NEGATIVE_NUMBER) ... </k>
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

  rule <k> jump(L) => panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires notBool (L in_labels LL)
```

### Subroutine call internal rules

A subroutine call in TEAL performs an unconditional jump to a target label and
records the next program counter value on the call stack.

Subroutines share the regular `<stack>` and `<scratch>` with the main TEAL program. Either could be used to pass arguments or return results.

```k
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
       <callStack> XS => ListItem(PC +Int 1) XS </callStack>
    requires  (TARGET in_labels LL)
      andBool (size(XS) <Int MAX_CALLSTACK_DEPTH)

  rule <k> callSubroutine(_TARGET) => panic(CALLSTACK_OVERFLOW) ... </k>
       <callStack> XS </callStack>
    requires size(XS) >=Int MAX_CALLSTACK_DEPTH

  rule <k> callSubroutine(TARGET) => panic(ILLEGAL_JUMP) ... </k>
       <labels> LL </labels>
    requires notBool(TARGET in_labels LL)

  syntax KItem ::= returnSubroutine()
  //---------------------------------
  rule <k> returnSubroutine() => .K ... </k>
       <pc> _ => RETURN_PC </pc>
       <jumped> _ => true </jumped>
       <callStack> ListItem(RETURN_PC) XS => XS </callStack>

  rule <k> returnSubroutine() => panic(CALLSTACK_UNDERFLOW) ... </k>
       <pc> _ </pc>
       <callStack> .List </callStack>
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

  rule <k> dig N => panic(STACK_UNDERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> cover N => .K ... </k>
       <stack> X : STACK => #take(N, STACK) (X : #drop(N, STACK)) </stack>
       <stacksize> S </stacksize>
    requires 0 <=Int N andBool N <Int S

  rule <k> cover N => panic(STACK_UNDERFLOW) ... </k>
       <stack> _ </stack>
       <stacksize> S </stacksize>
    requires notBool (0 <=Int N andBool N <Int S)

  rule <k> swap => .K ... </k>
       <stack> X : Y : XS => Y : X : XS </stack>

  rule <k> swap => panic(STACK_UNDERFLOW) ... </k>
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
```

### Blockchain State Accessors

```k
  rule <k> txn I => gtxn getCurrentTxn() I ... </k>

  rule <k> txn I J => txna I J ... </k>

  rule <k> gtxn G I => loadFromGroup(G, I) ... </k>

  rule <k> gtxns I => loadFromGroup(G, I) ... </k>
       <stack> G : XS => XS </stack>
       <stacksize> S => S -Int 1 </stacksize>

  rule <k> txna I J => gtxna getCurrentTxn() I J ... </k>

  rule <k> txnas I => gtxnas getCurrentTxn() I ... </k>

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

  rule <k> _:BlockchainOpCode => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  syntax KItem ::= loadFromGroup(Int, TxnField)
  //-------------------------------------------
  rule <k> loadFromGroup(GROUP_IDX, FIELD) => . ...</k>
       <stack> XS => {getTxnField(GROUP_IDX, FIELD)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires   isTValue(getTxnField(GROUP_IDX, FIELD))
    andBool    S <Int MAX_STACK_DEPTH
    andBool    (notBool(isTxnDynamicField(FIELD))
    orElseBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int))

  rule <k> loadFromGroup(GROUP_IDX, _:TxnDynamicField) => panic(FUTURE_TXN) ...</k>
    requires GROUP_IDX >=Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadFromGroup(_, _) => panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> loadFromGroup(GROUP_IDX, FIELD) => panic(TXN_ACCESS_FAILED) ...</k>
    requires   notBool(isTValue(getTxnField(GROUP_IDX, FIELD)))

  syntax KItem ::= loadFromGroup(Int, TxnaField, Int)
  //-------------------------------------------------
  rule <k> loadFromGroup(GROUP_IDX, FIELD, IDX) => . ...</k>
       <stack> XS => {getTxnField(GROUP_IDX, FIELD, IDX)}:>TValue : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires   isTValue(getTxnField(GROUP_IDX, FIELD, IDX))
    andBool    S <Int MAX_STACK_DEPTH
    andBool    (notBool(isTxnaDynamicField(FIELD))
    orElseBool GROUP_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int))

  rule <k> loadFromGroup(GROUP_IDX, _:TxnaDynamicField, _) => panic(FUTURE_TXN) ...</k>
    requires GROUP_IDX >=Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadFromGroup(_, _, _) => panic(STACK_OVERFLOW) ...</k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> loadFromGroup(GROUP_IDX, FIELD, IDX) => panic(TXN_ACCESS_FAILED) ...</k>
    requires   notBool(isTValue(getTxnField(GROUP_IDX, FIELD, IDX)))
       
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

  rule <k> load I => panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> store I => panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> loads => .K ... </k>
       <stack> I : XS => ({M[I]}:>TValue) : XS </stack>
       <scratch> M </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)

  rule <k> loads => panic(INVALID_SCRATCH_LOC) ... </k>
       <stack> I : _ </stack>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> stores => .K ... </k>
       <stack> V : I : XS => XS </stack>
       <stacksize> S => S -Int 2 </stacksize>
       <scratch> M => M[I <- V] </scratch>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE

  rule <k> stores => panic(INVALID_SCRATCH_LOC) ... </k>
       <stack> _ : I : _ </stack>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> _:LoadOpCode => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
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
//  rule <k> arg I => panic(INDEX_OUT_OF_BOUNDS) ... </k>
//       <stacksize> S </stacksize>
//    requires S <Int MAX_STACK_DEPTH
//     andBool notBool (isTValue(getArgument(I)))
//
//  rule <k> arg _ => panic(STACK_OVERFLOW) ... </k>
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

  rule <k> balance => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  syntax KItem ::= "#balance" MaybeTValue
  
  rule <k> #balance BAL:TUInt64 => . ...</k>
       <stack> _ : XS => BAL : XS </stack>
      
  rule <k> #balance _ => panic(TXN_ACCESS_FAILED) </k>  [owise]
```

*min_balance*

```k
  rule <k> min_balance => #min_balance getAccountParamsField(AcctMinBalance, {accountReference(A)}:>TValue) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> min_balance => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  syntax KItem ::= "#min_balance" MaybeTValue
  
  rule <k> #min_balance MIN_BAL:TUInt64 => . ...</k>
       <stack> _ : XS => MIN_BAL : XS </stack>
      
  rule <k> #min_balance _ => panic(TXN_ACCESS_FAILED) </k>  [owise]
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

   rule <k> log => panic(ILL_TYPED_STACK) ...</k>
        <stack> _:TUInt64 : _ </stack>

   rule <k> log => panic(LOG_CALLS_EXCEEDED) ...</k>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <logData> LOG </logData>
         ...
       </transaction>
    requires size(LOG) >=Int PARAM_MAX_LOG_CALLS

   rule <k> log => panic(LOG_SIZE_EXCEEDED) ...</k>
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

  rule <k> app_opted_in  => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> APP:Int : A:TValue : _:TStack </stack>
    requires notBool (isTValue(appReference(APP)) andBool isTValue(accountReference(A)))

  rule <k> app_opted_in => panic(ILL_TYPED_STACK) ... </k>
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

  rule <k> app_local_get => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_get => panic(ILL_TYPED_STACK) ... </k>
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

  rule <k> #app_local_get NoTValue => panic(TXN_ACCESS_FAILED) ... </k>
```

*app_local_get_ex*

```k
  rule <k> app_local_get_ex =>
           #app_local_get_ex getAppLocal({accountReference(A)}:>TValue, {appReference(APP)}:>TValue, KEY) ... </k>
       <stack> (KEY:Bytes) : (APP:TUInt64) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A)) andBool isTValue(appReference(APP))

  rule <k> app_local_get_ex => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (APP:TUInt64) : (A:TValue) : _ </stack>
    requires notBool (isTValue(accountReference(A)) andBool isTValue(appReference(APP)))

  rule <k> app_local_get_ex => panic(ILL_TYPED_STACK) ... </k>
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

  rule <k> #app_local_get_ex NoTValue => panic(TXN_ACCESS_FAILED) ... </k>
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

  rule <k> app_local_put => #app_local_put {accountReference(A)}:>TAddressLiteral
                                           getGlobalField(CurrentApplicationID) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (A:TValue) : _ </stack>
    requires isTValue(accountReference(A))

  rule <k> app_local_put => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:TValue) : (_:Bytes) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_put => panic(ILL_TYPED_STACK) ...  </k>
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

  rule <k> #app_local_put _ _ => panic(KEY_TOO_LARGE) ... </k>
       <stack> _ : (KEY:Bytes) : _ : _ </stack>
    requires lengthBytes(KEY) >Int PARAM_MAX_KEY_SIZE

  rule <k> #app_local_put _ _ => panic(KEY_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : _ : _ </stack>
    requires lengthBytes(KEY) +Int sizeInBytes(NEWVAL) >Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_local_put _ _ => panic(BYTE_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:Bytes) : _ : _ : _ </stack>
    requires lengthBytes(NEWVAL) >Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_local_put ADDR APP => panic(LOCAL_INTS_EXCEEDED) ... </k>
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

  rule <k> #app_local_put ADDR APP => panic(LOCAL_BYTES_EXCEEDED) ... </k>
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
  rule <k> #app_local_put ADDR APP => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> _ : _ : _ : XS => XS </stack>
       <stacksize> S => S -Int 3 </stacksize>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, panic
    rule <k> #app_local_put ADDR _ => panic(TXN_ACCESS_FAILED) ... </k>
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

  rule <k> app_local_del => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes ) : (A:TValue) : _ </stack>
    requires notBool isTValue(accountReference(A))

  rule <k> app_local_del => panic(ILL_TYPED_STACK) ... </k>
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
  rule <k> #app_local_del ADDR APP => panic(TXN_ACCESS_FAILED) ... </k>
       <account>
         <address> ADDR </address>
         <appsOptedIn> OA </appsOptedIn> ...
       </account>
    requires notBool (APP in_optedInApps(<appsOptedIn> OA </appsOptedIn>))

  // if the account doesn't exist, panic.
  rule <k> #app_local_del ADDR _ => panic(TXN_ACCESS_FAILED) ... </k>
       <accountsMap> AMAP  </accountsMap>
    requires notBool (ADDR in_accounts(<accountsMap> AMAP </accountsMap>))
```

*app_global_get*

```k
  rule <k> app_global_get =>
           #app_global_get getAppGlobal(getGlobalField(CurrentApplicationID), KEY) ... </k>
       <stack> (KEY:Bytes) : _ </stack>

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
  rule <k> app_global_get_ex =>
           #app_global_get_ex getAppGlobal({appReference(APP)}:>TValue, KEY) ... </k>
       <stack> (KEY:Bytes) : (APP:TUInt64) : _ </stack>
    requires isTValue(appReference(APP))

  rule <k> app_global_get_ex => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (_:Bytes) : (APP:TUInt64) : _ </stack>
    requires notBool isTValue(appReference(APP))

  rule <k> app_global_get_ex => panic(ILL_TYPED_STACK) ... </k>
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

  rule <k> #app_global_put _ => panic(KEY_TOO_LARGE) ... </k>
       <stack> _ : (KEY:Bytes) : _ </stack>
    requires lengthBytes(KEY) >Int PARAM_MAX_KEY_SIZE

  rule <k> #app_global_put _ => panic(KEY_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:TValue) : (KEY:Bytes) : _ </stack>
    requires lengthBytes(KEY) +Int sizeInBytes(NEWVAL) >Int PARAM_MAX_SUM_KEY_VALUE_SIZE

  rule <k> #app_global_put _ => panic(BYTE_VALUE_TOO_LARGE) ... </k>
       <stack> (NEWVAL:Bytes) : _ : _ </stack>
    requires lengthBytes(NEWVAL) >Int PARAM_MAX_BYTE_VALUE_SIZE

  rule <k> #app_global_put APP => panic(GLOBAL_INTS_EXCEEDED) ... </k>
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

  rule <k> #app_global_put APP => panic(GLOBAL_BYTES_EXCEEDED) ... </k>
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

  rule <k> asset_holding_get _ => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (ASSET:TUInt64) : (A:TValue) : _ </stack>
    requires notBool (isTValue(accountReference(A)) andBool isTValue(asaReference(ASSET)))

  rule <k> asset_holding_get _ => panic(ILL_TYPED_STACK) ... </k>
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
       <stack> (A:TUInt64) : _ </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool isTValue(asaReference(A))

  rule <k> asset_params_get _ => panic(TXN_ACCESS_FAILED) ... </k>
       <stack> (A:TUInt64) : _ </stack>
       <stacksize> S </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (notBool isTValue(asaReference(A)))

  rule <k> asset_params_get _ => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH

  rule <k> asset_params_get _ => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Bytes) : _ </stack>

  syntax KItem ::= "#asset_params_get" TValue
  // ----------------------------------------
  rule <k> #asset_params_get RET => .K ... </k>
       <stack> (_:Int) : XS => 1 : RET : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (notBool (isInt(RET)) orElseBool {RET}:>Int >=Int 0 )

  rule <k> #asset_params_get RET => .K ... </k>
       <stack> (_:Int) : XS => 0 : 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool (isInt(RET) andThenBool {RET}:>Int <Int 0)
```

### Access to past transactions in the group

*gaid*

```k
  rule <k> gaid T => .K ... </k>
       <stack> XS => ({getTxnField(T, ApplicationID)}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool T <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)
     andBool ({getTxnField(T, TypeEnum)}:>Int) ==Int (@ appl)

  rule <k> gaid T => panic(FUTURE_TXN) ... </k>
    requires T >=Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)
     orBool ({getTxnField(T, TypeEnum)}:>Int) =/=Int (@ appl)
```

*gaids*

```k
  rule <k> gaids => .K ... </k>
       <stack> T : XS => ({getTxnField(T, ApplicationID)}:>TValue) : XS </stack>
    requires T <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)
     andBool ({getTxnField(T, TypeEnum)}:>Int) ==Int (@ appl)

  rule <k> gaids => panic(FUTURE_TXN) ... </k>
       <stack> T : _ </stack>
    requires T >=Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)
     orBool ({getTxnField(T, TypeEnum)}:>Int) =/=Int (@ appl)
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
  rule <k> loadGroupScratch(TXN_IDX, I) => . ...</k>
       <stack> XS => ({M[I]}:>TValue) : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <transaction>
         <txID> TXN_IDX </txID>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool I in_keys(M)
     andBool S <Int MAX_STACK_DEPTH
     andBool TXN_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(TXN_IDX, I) => . ...</k>
       <stack> XS => 0 : XS </stack>
       <stacksize> S => S +Int 1 </stacksize>
       <transaction>
         <txID> TXN_IDX </txID>
         <txScratch> M </txScratch>
         ...
       </transaction>
    requires 0 <=Int I andBool I <Int MAX_SCRATCH_SIZE
     andBool notBool (I in_keys(M))
     andBool S <Int MAX_STACK_DEPTH
     andBool TXN_IDX <Int ({getTxnField(getCurrentTxn(), GroupIndex)}:>Int)

  rule <k> loadGroupScratch(_, I) => panic(INVALID_SCRATCH_LOC) ... </k>
    requires I <Int 0 orBool I >=Int MAX_SCRATCH_SIZE

  rule <k> loadGroupScratch(TXN_IDX, _) => panic(FUTURE_TXN) ... </k>
    requires TXN_IDX >=Int {getTxnField(getCurrentTxn(), GroupIndex)}:>Int

  rule <k> loadGroupScratch(TXN_IDX, _) => panic(TXN_OUT_OF_BOUNDS) ... </k>
    requires TXN_IDX <Int 0 orBool TXN_IDX >=Int {getGlobalField(GroupSize)}:>Int
  
  rule <k> loadGroupScratch(_, _) => panic(STACK_OVERFLOW) ... </k>
       <stacksize> S </stacksize>
    requires S >=Int MAX_STACK_DEPTH
```


Panic Behaviors due to Ill-typed Stack Arguments
------------------------------------------------

### Crypto Opcodes

### Arithmetic/relational/logical/Bitwise Opcodes

```k
  rule <k> Op:OpCode => panic(ILL_TYPED_STACK) ... </k>
       <stack> (V2:TValue) : (V1:TValue) : _ </stack>
    requires (isBinaryArithOpCode(Op)         orBool
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
  rule <k> app_global_get => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>

  rule <k> app_global_put => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:TValue) : (_:Int):_ </stack>

  rule <k> app_global_del => panic(ILL_TYPED_STACK) ... </k>
       <stack> (_:Int) : _ </stack>
```

### Signature Verification Opcode

Panic Behaviors due to Insufficient Stack Arguments
---------------------------------------------------

TODO: incorporate Bytes math opcodes

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
