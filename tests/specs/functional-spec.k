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

endmodule
