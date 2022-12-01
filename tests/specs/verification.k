requires "avm/avm-execution.md"

// Verification interface and lemmas
module VERIFICATION
  imports AVM-EXECUTION
  imports TEAL-TYPES
//  imports SET-SYMBOLIC


  syntax StepSort ::= MaybeTValue
// ------------------------------------------------

  syntax KItem ::= runLemma ( KItem )
                 | doneLemma( KItem )
// --------------------------------------
  rule runLemma( T ) => doneLemma( T )

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
    requires (I >Int 0 andBool MAX_UINT64 >=Int I)
     andBool (B >Int log2Int(I) andBool 64 >Int B)
    [simplification]

////////////////////////////////////////////////////////////////////////////////
// Map reasoning
////////////////////////////////////////////////////////////////////////////////

  rule _:Map [X <- N] [X] => N                        [simplification]
  rule M:Map [X <- _] [Y] => M [Y]  requires X =/=K Y [simplification]
    
  // Normalize Maps
  rule M:Map [ K <- _ ] [ K <- V ] => M [ K <- V ]  [simplification]
  rule M:Map [ K1 <- V1 ] [ K2 <- V2 ] => M [ K2 <- V2 ] [ K1 <- V1 ]
    requires K1 >Int K2 [simplification]

  // in_keys
  rule X:Label in_keys( M:Map [Y:Label <- _] ) => false
    requires (notBool (X in_keys ( M ))) andBool (X =/=K Y)  [simplification]

  rule X in_keys( _:Map [X <- _] ) => true  [simplification]
  rule X in_keys( M:Map [Y <- _] ) => X in_keys(M) 
    requires X =/=K Y [simplification]

  // size
  rule size( _:Map [_ <- _] )  >Int 0 => true   [simplification]
  rule size( _:Map [_ <- _] ) ==Int 0 => false  [simplification]
  rule { size( _:Map [_ <- _] ) #Equals 0 } => #Bottom  [simplification]

  // Subterm equality
  rule { M1:Map [ K <- V1 ] #Equals M2:Map [ K <- V2 ] } => { M1 #Equals M2 } #And { V1 #Equals V2 } [simplification]
  rule { M1:Map [ K <- V  ] #Equals M2:Map [ K <- V  ] } => { M1 #Equals M2 }
    requires notBool (K in_keys(M1) orBool K in_keys (M1)) [simplification]

////////////////////////////////////////////////////////////////////////////////
// Set reasoning
////////////////////////////////////////////////////////////////////////////////
  
  rule _ in .Set => false [simplification]

  rule X in (SetItem(Y) S:Set) => X in S requires X =/=K Y [simplification]

////////////////////////////////////////////////////////////////////////////////
// List reasoning
////////////////////////////////////////////////////////////////////////////////
  
  rule _ in .List => false [simplification]

  rule X in (ListItem(Y) L:List) => X in L requires X =/=K Y [simplification]

  rule X in (ListItem(X) _:List) => true [simplification]

////////////////////////////////////////////////////////////////////////////////
// TStack
////////////////////////////////////////////////////////////////////////////////

  // #sizeTStack
  rule #sizeTStack( S:TStack ) => 0
    requires S ==K .TStack  [simplification]

  rule #sizeTStack( S:TStack, N:Int ) => N
    requires S ==K .TStack  [simplification]

  rule #sizeTStack( S:TStack ) >Int 0 => true
    requires S =/=K .TStack  [simplification]

  rule #sizeTStack( S:TStack, N:Int ) >Int 0 => N >=Int 0
    requires S =/=K .TStack  [simplification]

  rule #sizeTStack(_) >=Int 0 => true  [simplification]
  rule #sizeTStack(_, 0) >=Int 0 => true  [simplification]
  
  rule #sizeTStack(_, N) +Int M >Int L => true
    requires (N +Int M) >Int L [simplification]

  rule #sizeTStack(_, M) >Int L => true
    requires M >Int L  [simplification]

  rule #sizeTStack(_) +Int M >Int L => true
    requires M >Int L  [simplification]

////////////////////////////////////////////////////////////////////////////////
// Int and Byte conversions
////////////////////////////////////////////////////////////////////////////////

  rule Bytes2Int ( Int2Bytes ( X, BYTE_ORDER, SIGNEDNESS ), BYTE_ORDER, SIGNEDNESS ) => X [simplification]
  rule Bytes2Int ( Int2Bytes ( (log2Int(X) +Int 8) /Int 8, X, BYTE_ORDER ), BYTE_ORDER, Unsigned ) => X [simplification]

  // Subterm equality
  rule { Int2Bytes( I1, BYTE_ORDER:Endianness, SIGNEDNESS:Signedness ) #Equals Int2Bytes( I2, BYTE_ORDER, SIGNEDNESS ) } => { I1 #Equals I2 } [simplification]

////////////////////////////////////////////////////////////////////////////////
// Int and Bool conversions
////////////////////////////////////////////////////////////////////////////////

  rule 0            >=Int bool2Int(B) => notBool B  [simplification]
  rule bool2Int(B)   >Int 0           =>         B  [simplification]

  rule A           >=Int bool2Int(_) => true requires A >=Int 1 [simplification]
  rule bool2Int(_) >=Int A           => true requires 0 >=Int A [simplification]

  rule int2Bool(bool2Int(I)) => I [simplification]
  rule bool2Int(int2Bool(B)) => B [simplification]

  rule A           >=Int bool2Int(_) => true requires A >=Int 1 [simplification]
  rule bool2Int(_) >=Int A           => true requires 0 >=Int A [simplification]

////////////////////////////////////////////////////////////////////////////////
// #if #then #else #fi
////////////////////////////////////////////////////////////////////////////////

  rule 0 >=Int #if COND #then 1 #else 0 #fi => notBool (COND) [simplification]
  rule #if COND #then 1 #else 0 #fi  >Int 0 =>          COND  [simplification]

////////////////////////////////////////////////////////////////////////////////
// Arithmetic
////////////////////////////////////////////////////////////////////////////////

  rule N:Int +Int M:Int >Int M:Int => N:Int >Int 0
    requires M =/=Int 0 [simplification, concrete(M)]

  rule N:Int /Int N:Int => 1 requires N =/=Int 0 [simplification]

////////////////////////////////////////////////////////////////////////////////
// Comparisons
////////////////////////////////////////////////////////////////////////////////

  rule N  <Int M => M  >Int N [simplification]
  rule N <=Int M => M >=Int N [simplification]

  rule notBool (N  >Int M) => M >=Int N  [simplification]
  rule notBool (N >=Int M) => M  >Int N  [simplification]

////////////////////////////////////////////////////////////////////////////////
// Bytes and String reasoning
////////////////////////////////////////////////////////////////////////////////

  rule lengthBytes(B1) +Int lengthBytes(B2) => lengthBytes(B1 +Bytes B2)  [simplification]
  rule String2Bytes(Bytes2String(B)) => B  [simplification]

////////////////////////////////////////////////////////////////////////////////
// Address hooks
////////////////////////////////////////////////////////////////////////////////

  // for symbolic reasoning, we relax address validity to just the checking the length
  rule IsAddressValid(A) => lengthString(A) ==Int 58 [simplification]

  // for symbolic reasoning, we eliminate the hashing from app address calculation
  // rule getAppAddressBytes(APP_ID:Int) => padLeftBytes(b"appID" +Bytes Int2Bytes(8, APP_ID, BE), 58, 0) [simplification]
  // The following lemma does the jon of the commented-out lemma for getAppAddressBytes, which
  // does not apply because the rule for getAppAddressBytes applies first

  rule Sha512_256raw(S:String) => Bytes2String(padLeftBytes(String2Bytes(S), 58, 0)) [simplification]

////////////////////////////////////////////////////////////////////////////////
// Cryptographic function hooks 
////////////////////////////////////////////////////////////////////////////////

  rule #Ceil ( Sha512_256raw ( _:String ) ) => #Top [simplification]

endmodule
