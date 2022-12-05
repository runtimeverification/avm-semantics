```k
module KAVM-MINI-SPEC
  imports VERIFICATION

  claim
    <k> #executeTxn(TX_ID) => . </k>
    <program> _ => ?_ </program>
    <stack> _ => ?_ </stack>
    <pc> _ => ?_ </pc>
    <currentTx> _ => ?_ </currentTx>
    <transactions>
      <transaction>
        <txID> TX_ID </txID>
        <pgm>
          account 0
          account 1
          arg 0
          btoi
          arg 1
          btoi
          +
          pay
          .TealProgram
        </pgm>
        <args> Int2Bytes(ARG1, BE, Unsigned) Int2Bytes(ARG2, BE, Unsigned) .BytesList </args>
        <foreignAccounts> ADDR1:Bytes ADDR2:Bytes .BytesList </foreignAccounts>
      </transaction>
    </transactions>
    <account>
      <address> ADDR1 </address>
      <balance> BAL1 => ?BAL1POST </balance>
    </account>
    <account>
      <address> ADDR2 </address>
      <balance> BAL2 => ?BAL2POST </balance>
    </account>
    requires ADDR1 =/=K ADDR2
     andBool BAL1 >=Int (ARG1 +Int ARG2)
    ensures ?BAL1POST ==Int BAL1 -Int (ARG1 +Int ARG2)
    andBool ?BAL2POST ==Int BAL2 +Int (ARG1 +Int ARG2)

endmodule
```
