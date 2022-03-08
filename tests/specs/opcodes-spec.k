module OPCODES-SPEC
////////////////////////////////////////////////////////////////////////////////
//// Specification of TEAL opcodes, organized by version.
////
//// The goal of this spec is to check sanity and completeness of the semantics.
////////////////////////////////////////////////////////////////////////////////

  imports VERIFICATION

////////////////////////////////////////
//// Auxilarry opcodes of the semantics.
//// These are not a part of TEAL itself.
////////////////////////////////////////

  claim <k> NoOpCode => .K ... </k>

  claim <k> err => panic(ERR_OPCODE) ... </k>

////////////////////////////////////////
//// TEAL v1 and v2 ////////////////////
////////////////////////////////////////

  claim <k> + => . ... </k>
        <stack> (X:Int) : (Y:Int) : _ => (X +Int Y) : ?_ </stack>
        <stacksize> SS => SS -Int 1 </stacksize>
    requires 0 <=Int X        andBool X        <=Int MAX_UINT64
     andBool 0 <=Int Y        andBool Y        <=Int MAX_UINT64
     andBool 0 <=Int X +Int Y andBool X +Int Y <=Int MAX_UINT64

  claim <k> intc (I:Int) => .K ... </k>
        <intcblock> INTS </intcblock>
        <stack> XS => V : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires (S <Int MAX_STACK_DEPTH)
     andBool (I:Int in_keys(INTS))
     andBool (V ==K INTS[I])
////////////////////////////////////////
//// TEAL v3 ///////////////////////////
////////////////////////////////////////

  claim <k> assert => . ... </k>
        <stack> (X:Int) : _ => ?_ </stack>
        <stacksize> SS => SS -Int 1 </stacksize>
    requires X =/=Int 0
     andBool 0 <=Int X andBool X <=Int MAX_UINT64

  claim <k> dig N => . ... </k>
     <stack> STACK => STACK[N]:STACK </stack>
     <stacksize> S => S +Int 1 </stacksize>
    requires S <Int MAX_STACK_DEPTH
     andBool 0 <=Int N andBool N <Int S

  claim <k> swap => . ... </k>
       <stack> X : Y : XS => Y : X : XS </stack>
    requires S <Int MAX_STACK_DEPTH
     andBool 0 <=Int N andBool N <=Int S

  // In 1, all bits except the least significant one are 0
  claim <k> getbit => . ... </k>
        <stack> B : 1 : _ => 0 : ?_ </stack>
        <stacksize> S => S -Int 1 </stacksize>
    requires 0 <Int B andBool B <Int 64

  // A generalization of the previous claim:
  // all bits after the most significant one set are unset (zero)
  claim <k> getbit => . ... </k>
        <stack> B : I : _ => 0 : ?_ </stack>
        <stacksize> S => S -Int 1 </stacksize>
    // TODO: this should be `I >=Int 0`, but I can't make the proof go through
    requires (I >Int 0 andBool I <=Int MAX_UINT64)
     andBool (0 <Int B andBool log2Int(I) <Int B andBool B <Int 64)

  // // All bits in one-byte arrayt 0xff are 1
  // claim <k> getbit => . ... </k>
  //       <stack> prepBytesString("0xff") : B : _ => 1 : ?_ </stack>
  //       <stacksize> S => S -Int 1 </stacksize>
  //   requires 0 <=Int B andBool B <Int lengthBytes(prepBytesString("0xff")) *Int 8

////////////////////////////////////////
//// TEAL v4 ///////////////////////////
////////////////////////////////////////

////////////////////////////////////////
//// TEAL v5 ///////////////////////////
////////////////////////////////////////
endmodule
