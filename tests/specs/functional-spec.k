module FUNCTIONAL-SPEC
  imports VERIFICATION
  
  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes))) => doneLemma(ListItem(A) ListItem(B)) </k>
    requires A =/=K B

  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes) ListItem(C:Bytes))) => doneLemma(ListItem(A) ListItem(B) ListItem(C)) </k>
    requires A =/=K B andBool B =/=K C andBool A =/=K C

  claim <k> runLemma(addToListNoDup(A:Bytes, ListItem(B:Bytes) ListItem(A:Bytes))) => doneLemma(ListItem(B) ListItem(A)) </k>
    requires A =/=K B

endmodule
