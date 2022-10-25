module TXN-ACCESS-SPEC
    imports VERIFICATION

  // Both these claims do not pass
  claim <k> runLemma(getCurrentTxn()) => doneLemma(?X) </k>
        <currentTx> "0":String </currentTx>
    ensures ?X ==K "0"

  claim <k> runLemma(getCurrentTxn()) => doneLemma("0") </k>
        <currentTx> "0":String </currentTx>

endmodule
