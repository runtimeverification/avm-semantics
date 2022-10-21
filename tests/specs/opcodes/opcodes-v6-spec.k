module OPCODES-V6-SPEC
  imports VERIFICATION

// itxnas f 	6 	not implemented 	1
  claim <k> itxnas ApplicationArgs => . </k>
        <stack> 1 : XS => 123 : XS </stack>
        <stacksize> S </stacksize>
        <lastTxnGroupID> "2" </lastTxnGroupID>
        <transactions>
          <transaction>
            <txID> "3" </txID>
            <groupID> "2" </groupID>
            <groupIdx> 0 </groupIdx>
            <applicationArgs> 1 123 4 </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000

// gitxnas t f 	6 	not implemented 	1 
  claim <k> gitxnas 1 ApplicationArgs => . </k>
        <stack> 2 : XS => 123 : XS </stack>
        <stacksize> S  </stacksize>
        <lastTxnGroupID> "2" </lastTxnGroupID>
        <transactions>
          <transaction>
            <txID> "3" </txID>
            <groupID> "2" </groupID>
            <groupIdx> 1 </groupIdx>
            <applicationArgs> 1 2 123 4 </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000
  
endmodule
