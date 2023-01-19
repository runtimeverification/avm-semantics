module FUNCTIONAL-SPEC
  imports VERIFICATION
  
  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes))) => doneLemma(ListItem(A) ListItem(B)) </k>
    requires A =/=K B

  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes) ListItem(C:Bytes))) => doneLemma(ListItem(A) ListItem(B) ListItem(C)) </k>
    requires A =/=K B andBool B =/=K C andBool A =/=K C

  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes) ListItem(A:Bytes))) => doneLemma(ListItem(B) ListItem(A)) </k>
    requires A =/=K B

  claim <k> extract 4 8 => . </k>
        <stack> 
          b"\x15\x1f|u" +Bytes padLeftBytes ( Int2Bytes ( I1 , BE , Unsigned ) , 8 , 0 ) : .TStack
          => padLeftBytes(Int2Bytes(I1, BE, Unsigned), 8, 0) : .TStack
        </stack>
    requires 0 <=Int I1 andBool I1 <=Int MAX_UINT64

  claim <k> concat => . </k>
        <stack> 
          padLeftBytes ( Int2Bytes ( ( log2Int ( ARG1:Int +Int ARG2:Int ) +Int 8 ) /Int 8 , ARG1:Int +Int ARG2:Int , BE ) , 8 , 0 ) : b"\x15\x1f|u" : .TStack
          => b"\x15\x1f|u" +Bytes padLeftBytes ( Int2Bytes ( ( log2Int ( ARG1:Int +Int ARG2:Int ) +Int 8 ) /Int 8 , ARG1:Int +Int ARG2:Int , BE ) , 8 , 0 ) : .TStack
        </stack>
        <stacksize> 2 => 1 </stacksize>
    requires ARG1 +Int ARG2 <=Int MAX_UINT64
     andBool ARG1 >=Int 0
     andBool ARG2 >=Int 0

  claim <k> 
          runLemma(bool2Int ( ( ( AMOUNT:Int *Int 3000000 >>Int 64 <<Int 64 ) +Int ( AMOUNT:Int *Int 3000000 &Int 18446744073709551615 ) ) /Int ( AMOUNT:Int +Int 1000000 ) >>Int 64 ==Int 0 ))
          => 
          doneLemma(bool2Int ( ( AMOUNT:Int *Int 3000000 ) /Int ( AMOUNT:Int +Int 1000000 ) >>Int 64 ==Int 0 ))
        </k>

  claim <k>
          runLemma(AMOUNT:Int *Int 3000000 /Int ( AMOUNT:Int +Int 1000000 ) >>Int 64)
          =>
          doneLemma(0)
        </k>
      requires AMOUNT <Int 18446744073709551615
       andBool AMOUNT >=Int 0

  claim <k>
          runLemma(( AMOUNT:Int *Int 3000000 &Int 18446744073709551615 ) /Int ( AMOUNT:Int +Int 1000000 ) >>Int 64)
          =>
          doneLemma(0)
        </k>
    requires AMOUNT <Int 18446744073709551615
     andBool AMOUNT >=Int 0

  claim <k>
          runLemma(( ( AMOUNT:Int *Int 3000000 &Int 18446744073709551615 ) /Int ( AMOUNT:Int +Int 1000000 ) &Int 18446744073709551615 ) *Int 10 /Int 10000 >>Int 64)
          =>
          doneLemma(0)
        </k>
    requires AMOUNT <Int 18446744073709551615
     andBool AMOUNT >=Int 0

  claim <k>
          runLemma( 0 >Int ( ( AMOUNT:Int *Int 3000000 &Int 18446744073709551615 ) /Int ( AMOUNT:Int +Int 1000000 ) &Int 18446744073709551615 ) *Int 9700 /Int 10000 &Int 18446744073709551615 )
          =>
          doneLemma(false)
        </k>
    requires AMOUNT <Int 18446744073709551615
     andBool AMOUNT >=Int 0

endmodule
