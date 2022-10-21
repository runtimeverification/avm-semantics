module OPCODES-V6-SPEC
  imports VERIFICATION

// acct_params_get f 	6 	not implemented 	1 
  claim <k> acct_params_get AcctBalance => . </k>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <sender> b"1" </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <stack> b"1" : XS => 1 : BAL : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <accountsMap>
          <account>
            <address> b"1" </address>
            <balance> BAL </balance>
            ...
          </account>
        </accountsMap>
    requires S >=Int 1 andBool S <Int 1000 andBool BAL >Int 0

  claim <k> acct_params_get AcctMinBalance => . </k>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <sender> b"1" </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <stack> b"1" : XS => 0 : MIN_BAL : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <accountsMap>
          <account>
            <address> b"1" </address>
            <balance> 0 </balance>
            <minBalance> MIN_BAL </minBalance>
            ...
          </account>
        </accountsMap>
    requires S >=Int 1 andBool S <Int 1000

  claim <k> acct_params_get AcctAuthAddr => . </k>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <sender> b"1" </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <stack> b"1" : XS => 1 : AUTH_ADDR : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <accountsMap>
          <account>
            <address> b"1" </address>
            <balance> BAL </balance>
            <key> AUTH_ADDR </key>
            ...
          </account>
        </accountsMap>
    requires S >=Int 1 andBool S <Int 1000 andBool BAL >Int 0

// divw 	6 	not implemented 	1 
  // ((12345 + (3 << 64)) / 54321) = 1018763134351883
  claim <k> divw => . </k>
        <stack> 54321 : 12345 : 3 : XS => 1018763134351883 : XS </stack>
        <stacksize> S => S -Int 2 </stacksize>

  claim <k> divw => panic(DIV_BY_ZERO) </k>
        <stack> 0 : _:Int : _:Int : _ </stack>

  // (5 << 64) / 2 > MAX_UINT
  claim <k> divw => panic(INT_OVERFLOW) </k>
        <stack> 2 : 0 : 5 : _ </stack>

  // (5 << 64) / 2 > MAX_UINT
  claim <k> divw => panic(ILL_TYPED_STACK) </k>
        <stack> C : B : A : _ </stack>
    requires (isBytes(A) orBool isBytes(B) orBool isBytes(C))
     andBool C =/=K 0

endmodule
