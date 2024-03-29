requires "avm/avm-execution.md"
requires "cpmm-teal-source.k"
requires "macros.md"

// Verification interface and lemmas
module VERIFICATION
  imports CPMM-TEAL-SOURCE
  imports MACROS
  imports LEMMAS

endmodule

module LEMMAS
  imports AVM-EXECUTION
  imports TEAL-TYPES

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
// Recombine 128-bit Ints
////////////////////////////////////////////////////////////////////////////////

//      Upper 64 bits                    Lower 64 bits
  rule ((X:Int >>Int 64) <<Int 64) +Int (X &Int 18446744073709551615) => X [simplification]

  rule X:Int >>Int N:Int => 0
    requires X <Int 2 ^Int N
     andBool 0 <=Int X [simplification]

  rule X:Int >Int Y:Int /Int Z:Int => true
    requires X >Int Y
     andBool Z >Int 0 [simplification]

  rule X:Int /Int Y:Int >=Int 0 => true
    requires X >=Int 0
     andBool Y >=Int 0 [simplification]

  rule 0 >Int X:Int /Int Y:Int => false
    requires X >=Int 0
     andBool Y >=Int 0 [simplification]

  rule A:Int >Int (X:Int &Int B:Int) => true
    requires X >=Int 0
     andBool A >=Int 0
     andBool B >=Int 0
     andBool A >Int B [simplification]

  rule 0 >Int (X:Int &Int Y:Int) => 0 >Int X
    requires Y >=Int 0 [simplification]

  rule X:Int &Int Y:Int >=Int 0 => true
    requires X >=Int 0
     andBool Y >=Int 0  [simplification]

  syntax Bool ::= allOnes(Int) [function]
  rule allOnes(0) => true
  rule allOnes(N) => allOnes(N /Int 2) requires N modInt 2 ==Int 1 andBool N >Int 0
  rule allOnes(N) => false requires N modInt 2 ==Int 0 andBool N >Int 0

  rule X:Int &Int Y:Int => X
    requires allOnes(Y)
     andBool X <=Int Y [simplification]

  rule sqrtUInt( X:Int *Int Y:Int ) >Int N:Int => false
    requires X <=Int N
     andBool Y <=Int N [simplification]

  rule N >=Int sqrtUInt( X:Int *Int Y:Int ) => true
    requires X <=Int N
     andBool Y <=Int N [simplification]

//   rule I1 *Int I2 >Int I3 -Int (I1 *Int I4) =>
//        I1 *Int (I2 +Int I4) >Int I3 [simplification]


  rule A /Int B >Int C -Int (D /Int B) => false
    requires notBool(A +Int D >Int B *Int C) [simplification]

//   rule A /Int B >Int C -Int (D /Int B) => A +Int D >Int B *Int C [simplification]

  rule (A *Int B) +Int (A *Int C) => A *Int (B +Int C) [simplification]

  rule A *Int B >=Int C *Int D => true
    requires A >=Int C
     andBool B >=Int D [simplification]

  rule B *Int A >=Int C *Int D => true
    requires A >=Int C
     andBool B >=Int D [simplification]

  rule A *Int B >Int C *Int D => false
    requires C >=Int A
     andBool D >=Int B [simplification]

  rule B *Int A >Int C *Int D => false
    requires C >=Int A
     andBool D >=Int B [simplification]

//   rule A *Int (B -Int C) => A *Int B -Int A *Int C [simplification]

//   rule { A /Int B #Equals C /Int B } => true
//     requires A ==Int C [simplification]
//
//   rule A *Int B ==Int C *Int B => A ==Int C
//     requires B >Int 0 [simplification]

////////////////////////////////////////////////////////////////////////////////
// Map reasoning
////////////////////////////////////////////////////////////////////////////////

  rule _:Map [X <- N] [X] => N                        [simplification]
  rule M:Map [X <- _] [Y] => M [Y]  requires notBool X ==K Y [simplification]

  // Normalize Maps
  rule M:Map [ K <- _ ] [ K <- V ] => M [ K <- V ]  [simplification]
  rule M:Map [ K1 <- V1 ] [ K2 <- V2 ] => M [ K2 <- V2 ] [ K1 <- V1 ]
    requires K1 >Int K2 [simplification]

  // in_keys

//   rule X in_keys( _:Map [X <- _] ) => true  [simplification]
//   rule X in_keys( M:Map [Y <- _] ) => X in_keys(M)
//     requires notBool (X ==K Y) [simplification]
  rule X in_keys( M:Map [Y <- _] ) => (X ==K Y) orBool (X in_keys(M)) [simplification]

//   rule X in_keys( _:Map (X |-> _) ) => true  [simplification]
  rule X in_keys( M:Map (Y |-> _) ) => (X ==K Y) orBool (X in_keys(M)) [simplification]
//     requires notBool (X ==K Y) [simplification]

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

  rule X in (SetItem(Y) S:Set) => X in S requires notBool(X ==K Y) [simplification]

////////////////////////////////////////////////////////////////////////////////
// List reasoning
////////////////////////////////////////////////////////////////////////////////

  rule _ in .List => false [simplification]

  rule X in (ListItem(Y) L:List) => X in L requires notBool(X ==K Y) [simplification]

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
    requires notBool(S ==K .TStack)  [simplification]

  rule #sizeTStack( S:TStack, N:Int ) >Int 0 => N >=Int 0
    requires notBool(S ==K .TStack)  [simplification]

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

  rule { Int2String(A) #Equals Int2String(B) } => { A #Equals B } [simplification]

  rule Int2String(A) ==K Int2String(B) => A ==Int B [simplification]

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

  rule A:Int +Int bool2Int(_) >Int B:Int => false
    requires A +Int 1 <=Int B [simplification]

  rule B :Int >=Int A:Int +Int bool2Int(_) => true
    requires A +Int 1 <=Int B [simplification]

////////////////////////////////////////////////////////////////////////////////
// De Morgan's distribution
////////////////////////////////////////////////////////////////////////////////
  rule notBool (A:Bool andBool B:Bool) => (notBool(A) orBool notBool(B)) [simplification]
  rule notBool (A:Bool orBool B:Bool) => (notBool(A) andBool notBool(B)) [simplification]

  rule true orBool _:Bool => true [simplification]
  rule _:Bool orBool true => true [simplification]

  rule { true #Equals true orBool _ } => { true #Equals true } [simplification]

////////////////////////////////////////////////////////////////////////////////
// #if #then #else #fi
////////////////////////////////////////////////////////////////////////////////

  rule 0 >=Int #if COND #then 1 #else 0 #fi => notBool (COND) [simplification]
  rule #if COND #then 1 #else 0 #fi  >Int 0 =>          COND  [simplification]

////////////////////////////////////////////////////////////////////////////////
// Arithmetic
////////////////////////////////////////////////////////////////////////////////

  rule I1:Int  >Int I2:Int +Int I3:Int => I1 -Int I3  >Int I2 [simplification, concrete(I1, I3), symbolic(I2)]
  rule I1:Int >=Int I2:Int +Int I3:Int => I1 -Int I3 >=Int I2 [simplification, concrete(I1, I3), symbolic(I2)]

  rule I1:Int +Int I2:Int >=Int I3:Int => I1 >=Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]
  rule I1:Int +Int I2:Int  >Int I3:Int => I1  >Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]

  rule I1:Int +Int I2:Int >Int I3 => I1 >Int I3 -Int I2 [simplification, concrete(I2, I3), symbolic(I1)]
  rule I1:Int >=Int I2:Int +Int I3:Int => I1 -Int I3 >=Int I2 [simplification, concrete(I1, I3), symbolic(I2)]

  rule I1:Int -Int I2:Int >=Int I3:Int => I1 -Int I3 >=Int I2 [simplification, concrete(I1, I3)]

  rule I1:Int >Int I2:Int -Int I3:Int => I3 >Int I2 -Int I1 [simplification, concrete(I1, I2)]

  rule I1:Int *Int I2:Int /Int I2:Int => I1
    requires I2 >Int 0 [simplification]

  rule I1:Int +Int (0 -Int I2:Int) => I1 -Int I2 [simplification]

//  rule I1:Int +Int I2 => I1 -Int (0 -Int I2) requires I2 <Int 0 [simplification, concrete(I2)]

  rule N:Int /Int N:Int => 1 requires notBool(N ==Int 0) [simplification]

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

  rule X >Int Y *Int Z => ((X -Int 1) /Int Z) +Int 1 >Int Y
    requires Z >Int 0
     andBool X >=Int 1 [simplification, concrete(X, Z)]

  rule 0 >Int Y *Int Z => 0 >Int Y
    requires Z >Int 0 [simplification, concrete(Z)]

  rule X *Int Y >=Int Z => X >=Int ((Z -Int 1) /Int Y) +Int 1
    requires Y >Int 0
     andBool Z >=Int 1 [simplification, concrete(Z, Y)]

  rule X *Int Y >=Int 0 => X >=Int 0
    requires Y >Int 0 [simplification, concrete(Y)]

//  rule N:Int >=Int X +Int Y => N -Int Y >=Int X [simplification, concrete(N, Y)]

////////////////////////////////////////////////////////////////////////////////
// Comparisons
////////////////////////////////////////////////////////////////////////////////

  rule N  <Int M => M  >Int N [simplification]
  rule N <=Int M => M >=Int N [simplification]

  rule notBool (N  >Int M) => M >=Int N  [simplification]
  rule notBool (N >=Int M) => M  >Int N  [simplification]

  rule N =/=K M => notBool (N ==K M) [simplification]

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
//    rule Sha512_256raw(S:String) => Sha512_256raw_symbolic(S:String) [simplification]

////////////////////////////////////////////////////////////////////////////////
// Cryptographic function hooks
////////////////////////////////////////////////////////////////////////////////

  rule #Ceil ( Sha512_256raw ( _:String ) ) => #Top [simplification]


endmodule
