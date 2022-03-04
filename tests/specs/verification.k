requires "avm/avm-execution.md"

// Verification interface and lemmas
module VERIFICATION
  imports AVM-EXECUTION

////////////////////////////////////////////////////////////////////////////////
// Lemmas to support `getbit` opcode specification
////////////////////////////////////////////////////////////////////////////////
  rule (I >>Int _) => 0
    requires I ==Int 0 [simplification]
  rule (1 >>Int 0) => 1 [simplification]
  rule (1 >>Int B) => 0
    requires B >Int 0 [simplification]

  // every bit after the most significant one set is zero,
  // therefore the shifted number is zero if we shift beyound
  // the most significant bit.
  // For example: 1 >>Int 1 ==Int 0;
  //              (3 >>Int 2 ==Int 1) andBool (3 >>Int 3 ==Int 0), etc.
  rule (I >>Int B) => 0
    requires (0 <Int I andBool I <=Int MAX_UINT64)
     andBool (log2Int(I) <Int B andBool B <Int 64)
    [simplification]

endmodule
