requires "avm/avm-execution.md"
requires "avm/macros.md"

// Verification interface and lemmas
module VERIFICATION
  imports AVM-EXECUTION
  imports TEAL-TYPES
  imports MACROS

  syntax KItem ::= tealLogExpr(Bytes)
// ------------------------------------

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

  rule _ in_keys ( .Map ) => false [simplification]

  rule X in_keys( _:Map [X <- _] ) => true  [simplification]
  rule X in_keys( M:Map [Y <- _] ) => X in_keys(M) 
    requires X =/=K Y [simplification]

  rule _ in_keys (.Map) => false [simplification]

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

  rule Int2Bytes(Bytes2Int(B, BYTE_ORDER, SIGNEDNESS), BYTE_ORDER, SIGNEDNESS) => B [simplification]

  // Subterm equality
  rule { Int2Bytes( I1, BYTE_ORDER:Endianness, SIGNEDNESS:Signedness ) #Equals Int2Bytes( I2, BYTE_ORDER, SIGNEDNESS ) } => { I1 #Equals I2 } [simplification]

////////////////////////////////////////////////////////////////////////////////
// Int and Bool conversions
////////////////////////////////////////////////////////////////////////////////

  rule 0            >=Int bool2Int(B) => notBool B  [simplification]
  rule bool2Int(B)   >Int 0           =>         B  [simplification]

  rule 0 >Int bool2Int(_) => false [simplification]
  rule { 0 #Equals bool2Int(B:Bool) } => { true #Equals notBool(B) } [simplification]

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

//   rule N:Int +Int M:Int >Int M:Int => N:Int >Int 0
//     requires M =/=Int 0 [simplification, concrete(M)]

  rule I1:Int  >Int I2:Int +Int I3:Int => I1 -Int I3  >Int I2 [simplification, concrete(I1, I3), symbolic(I2)]
  rule I1:Int >=Int I2:Int +Int I3:Int => I1 -Int I3 >=Int I2 [simplification, concrete(I1, I3), symbolic(I2)]

  rule I1:Int +Int I2:Int >=Int I3:Int => I1 >=Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]
  rule I1:Int +Int I2:Int  >Int I3:Int => I1  >Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]

  rule I1:Int +Int I2:Int >Int I3 => I1 >Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]
  rule I1:Int >=Int I2:Int +Int I3:Int => I1 -Int I3 >=Int I2 [simplification, concrete(I1, I3), symbolic(I2)]

  rule N:Int /Int N:Int => 1 requires N =/=Int 0 [simplification]

  rule #Ceil ( log2Int ( X:Int ) ) => #Top requires X >Int 0 [simplification]

  rule log2Int(X:Int)  >Int N:Int => X  >Int (2 ^Int (N +Int 1)) -Int 1 
    [simplification, concrete(N)]

  rule N:Int >=Int log2Int(X:Int) => (2 ^Int (N +Int 1)) -Int 1 >=Int X 
    [simplification, concrete(N)]

  rule N:Int  >Int log2Int(X:Int) => 2 ^Int N  >Int X [simplification, concrete(N)]

  rule log2Int(X:Int) >=Int N:Int => X >=Int 2 ^Int N [simplification, concrete(N)]

  rule X /Int Y  >Int N:Int => X  >Int ((N +Int 1) *Int Y) -Int 1
    requires Y >Int 0 [simplification, concrete(N, Y)]

  rule N:Int >=Int X /Int Y => ((N +Int 1) *Int Y) -Int 1 >=Int X
    requires Y >Int 0 [simplification, concrete(N, Y)]

  rule N:Int  >Int X /Int Y => N *Int Y  >Int X
    requires Y >Int 0 [simplification, concrete(N, Y)]

  rule X /Int Y >=Int N:Int => X >=Int N *Int Y
    requires Y >Int 0 [simplification, concrete(N, Y)]

//  rule N:Int >=Int X +Int Y => N -Int Y >=Int X [simplification, concrete(N, Y)]

  rule X +Int (0 -Int Y) => X -Int Y [simplification]

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

  // Simplify concrete portion of lengthBytes
  rule lengthBytes(B1) +Int lengthBytes(B2) => lengthBytes(B1 +Bytes B2)  [simplification, concrete(B1, B2)]
  rule lengthBytes(B1 +Bytes B2) => lengthBytes(B1) +Int lengthBytes(B2) [simplification, symbolic(B1)]
  rule lengthBytes(B1 +Bytes B2) => lengthBytes(B1) +Int lengthBytes(B2) [simplification, symbolic(B2)]
 
   // Simplify lengthBytes comparison by magnitude bound on length
   rule lengthBytes(Int2Bytes(I:Int, BE, Unsigned)) >Int N => false
     requires 0 <=Int I andBool I <Int (2 ^Int (N *Int 8)) [simplification]
   rule N >=Int lengthBytes(Int2Bytes(I:Int, BE, Unsigned)) => true
     requires 0 <=Int I andBool I <Int (2 ^Int (N *Int 8)) [simplification]
   
   // Simplify lengthBytes comparison for padLeftBytes terms
   rule N >=Int lengthBytes(padLeftBytes(B:Bytes, PAD_LEN:Int, _:Int)) => N >=Int lengthBytes(B)
     requires N >=Int PAD_LEN [simplification]
   rule lengthBytes(padLeftBytes(B:Bytes, PAD_LEN:Int, _:Int)) >Int N:Int =>  lengthBytes(B) >Int N
     requires PAD_LEN <=Int N [simplification]
   rule lengthBytes(padLeftBytes(_:Bytes, PAD_LEN:Int, _:Int)) >=Int N => true
     requires PAD_LEN >=Int N [simplification]
   rule N:Int >Int lengthBytes(padLeftBytes(_:Bytes, PAD_LEN:Int, _:Int)) => false
     requires PAD_LEN >=Int N [simplification]

   rule lengthBytes (substrBytes(_:Bytes, _:Int, LEN:Int)) >Int N => false
    requires LEN <=Int N [simplification]

   rule N >=Int lengthBytes (substrBytes(_:Bytes, _:Int, LEN:Int)) => true
    requires LEN <=Int N [simplification]
 
   // Left padding an Int with 0 bytes can't affect the value
   rule Bytes2Int(padLeftBytes(Int2Bytes(I:Int, BE, Unsigned), _:Int, 0), BE, Unsigned) => I
     requires I >=Int 0 [simplification]
 
   rule Bytes2Int(padLeftBytes(Int2Bytes(_:Int, I:Int, BE), _:Int, 0), BE, Unsigned) => I
     requires I >=Int 0 [simplification]
 
   // Simplify concrete portions of substrBytes
   rule substrBytes(B1:Bytes +Bytes B2:Bytes, START:Int, END:Int) => 
        substrBytes(B1, START, lengthBytes(B1)) +Bytes substrBytes(B2, 0, END -Int lengthBytes(B1))
        [concrete(B1), symbolic(B2), simplification]
 
   rule substrBytes(padLeftBytes(B, LEN:Int, PADDING:Int), 0, LEN) => padLeftBytes(B, LEN, PADDING)
     requires lengthBytes(B) <=Int LEN [simplification]
 
   rule String2Bytes(Bytes2String(B)) => B  [simplification]
 
   rule .Bytes +Bytes B:Bytes => B [simplification]
   rule B:Bytes +Bytes .Bytes => B [simplification]
 
   // For Int2Bytes, if length is given explicitely, use that
  rule lengthBytes(Int2Bytes(LENGTH:Int, I:Int, _BYTE_ORDER)) => LENGTH -Int 1
    requires I >=Int 0 [simplification]

////////////////////////////////////////////////////////////////////////////////
// Address hooks
////////////////////////////////////////////////////////////////////////////////

  // for symbolic reasoning, we relax address validity to just the checking the length
  rule IsAddressValid(A) => lengthString(A) ==Int 58 [simplification]

  // for symbolic reasoning, we eliminate the hashing from app address calculation
  // rule getAppAddressBytes(APP_ID:Int) => padLeftBytes(b"appID" +Bytes Int2Bytes(8, APP_ID, BE), 58, 0) [simplification]
  // The following lemma does the jon of the commented-out lemma for getAppAddressBytes, which
  // does not apply because the rule for getAppAddressBytes applies first

//  rule Sha512_256raw(S:String) => Bytes2String(padLeftBytes(String2Bytes(S), 58, 0)) [simplification]

////////////////////////////////////////////////////////////////////////////////
// Cryptographic function hooks 
////////////////////////////////////////////////////////////////////////////////

  rule #Ceil ( Sha512_256raw ( _:String ) ) => #Top [simplification]

endmodule
