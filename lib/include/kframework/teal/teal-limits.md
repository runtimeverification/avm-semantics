The TEAL interpreter is parameterized by several constants which define total
program size and cost. We define those constants here.

```k
module TEAL-LIMITS
  imports TEAL-SYNTAX

  // Size limits
  syntax Int ::= "MAX_STACK_DEPTH"     [macro]
  syntax Int ::= "MAX_CALLSTACK_DEPTH" [macro]
  syntax Int ::= "MAX_SCRATCH_SIZE"    [macro]
  syntax Int ::= "LogicSigMaxSize"     [macro]
  syntax Int ::= "LogicSigMaxCost"     [macro]
  syntax Int ::= "MaxAppProgramLen"    [macro]
  syntax Int ::= "MaxAppProgramCost"   [macro]
  syntax Int ::= "MAX_BYTEARRAY_LEN"   [macro]
  syntax Int ::= "MAX_BYTE_MATH_SIZE"  [macro]
  syntax Int ::= "MaxTxGroupSize"      [macro]
  // -----------------------------------------
  rule MAX_STACK_DEPTH     => 1000
  // TODO: find out the real restriction. 32 is a random number.
  rule MAX_CALLSTACK_DEPTH => 32
  rule MAX_SCRATCH_SIZE    => 256
  rule LogicSigMaxSize     => 1000
  rule LogicSigMaxCost     => 20000
  rule MaxAppProgramLen    => 1024
  rule MaxAppProgramCost   => 700
  rule MAX_BYTEARRAY_LEN   => 4096
  // MAX_BYTE_MATH_SIZE is the limit of byte strings supplied as input to byte math opcodes
  rule MAX_BYTE_MATH_SIZE  => 64
  rule MaxTxGroupSize      => 16
endmodule
```

