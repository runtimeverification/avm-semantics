module TXN-ACCESS-SPEC
    imports VERIFICATION

  claim <k> runLemma(getCurrentTxn()) => doneLemma("0") </k>
        <currentTx> "0":String </currentTx>

endmodule
