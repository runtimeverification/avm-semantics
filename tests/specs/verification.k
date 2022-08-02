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

  syntax Int ::= sum(MaybeTValue) [function]

  rule sum(N:TBytes REST:TValueList) => Bytes2Int(normalizeB(N), BE, Unsigned) +Int sum(REST)
  rule sum(N:TBytes) => Bytes2Int(normalizeB(N), BE, Unsigned)
  rule sum(_) => 0 [owise]
//  rule sum({N:TUInt64}:>Int REST:TValueList) => N +Int sum(REST)
//  rule sum({N:TUInt64}:>Int) => N
//  rule sum(NoTValue) => 0
    
  rule X:Label in_keys( M:Map [Y:Label <- _] ) => false
    requires (notBool (X in_keys ( M ))) andBool (X =/=K Y)  [simplification]

  rule X in_keys( _:Map [X <- _] ) => true  [simplification]
  rule X in_keys( M:Map [Y <- _] ) => X in_keys(M) 
    requires X =/=K Y [simplification]

  rule _:Map [X <- N] [X] => N  [simplification]
  rule M:Map [X <- _] [Y] => M [Y]  
    requires X =/=K Y [simplification]

  rule size( _:Map [_ <- _] ) >Int 0 => true  [simplification]
  rule size( _:Map [_ <- _] ) ==Int 0 => false  [simplification]
  rule { size( _:Map [_ <- _] ) #Equals 0 } => #Bottom  [simplification]

  rule N:Int +Int M:Int >Int M:Int => N:Int >Int 0
    requires M =/=Int 0 [simplification]

  rule #sizeTStack( S:TStack ) => 0
    requires S ==K .TStack  [simplification, smt-lemma]

  rule #sizeTStack( S:TStack, N:Int ) => N
    requires S ==K .TStack  [simplification, smt-lemma]

  rule #sizeTStack( S:TStack ) >Int 0 => true
    requires S =/=K .TStack  [simplification, smt-lemma]

  rule #sizeTStack( S:TStack, N:Int ) >Int 0 => N >=Int 0
    requires S =/=K .TStack  [simplification, smt-lemma]

  rule #if COND #then 1 #else 0 #fi <=Int 0 => notBool ( COND ) [simplification]
  rule #if COND #then 1 #else 0 #fi >Int 0 => COND [simplification]

  rule Bytes2Int ( Int2Bytes ( X, BYTE_ORDER, SIGNEDNESS ), BYTE_ORDER, SIGNEDNESS ) => X [simplification]

//   rule #Not ( { true #Equals X:Int <=Int Y:Int } ) => { true #Equals X >Int Y } [simplification]

//   rule {X <=Int 0} #And {X >Int 0} => #Bottom [simplification]
//   rule {X <Int 0} #And {X >=Int 0} => #Bottom [simplification]

endmodule
