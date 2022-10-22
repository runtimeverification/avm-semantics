module OPCODES-V6-SPEC
  imports VERIFICATION

// bsqrt 	6 	not implemented 	40

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

  claim <k> divw => panic(ILL_TYPED_STACK) </k>
        <stack> C : B : A : _ </stack>
    requires (isBytes(A) orBool isBytes(B) orBool isBytes(C))
     andBool C =/=K 0


// itxn_next 	6 	implemented, not tested 	1
claim <k> itxn_next => . </k>
      <currentTx> TX_ID </currentTx>
      <transactions>
        <transaction>
          <txID> TX_ID </txID>
          <firstValid> 100 </firstValid>
          <lastValid> 300 </lastValid>
          <typeEnum> @ appl </typeEnum>
          ...
        </transaction>
      </transactions>
      <currentApplicationAddress> b"application1" </currentApplicationAddress>
      <innerTransactions>
        ListItem(_)
        (.List =>
          ListItem(
            <transaction>
              <txID> "" </txID>
              <txHeader>
                 <fee> 0 </fee>
                 <sender> b"application1" </sender>
                 <firstValid> 100 </firstValid>
                 <lastValid> 300 </lastValid>
                 <genesisHash> .Bytes </genesisHash>
                 <txType> "unknown" </txType>
                 <typeEnum> 0 </typeEnum>
                 <groupID> "3" </groupID>
                 <groupIdx> 1 </groupIdx>
                 <genesisID> .Bytes </genesisID>
                 <lease> .Bytes </lease>
                 <note> .Bytes </note>
                 <rekeyTo> ?_ </rekeyTo>
              </txHeader>
              <txnTypeSpecificFields>
                .Bag
              </txnTypeSpecificFields>
              <applyData>
                <txScratch>       .Map  </txScratch>
                <txConfigAsset>   0     </txConfigAsset>
                <txApplicationID> 0     </txApplicationID>
                <log>
                  <logData> .TValueList </logData>
                  <logSize> 0:TValue    </logSize>
                </log>
              </applyData>
              <txnExecutionContext> .K </txnExecutionContext>
              <resume> false </resume>
            </transaction>))
      </innerTransactions>
      <nextGroupID> 3 </nextGroupID>

// gitxn t f 	6 	implemented, not tested 	1
  claim <k> gitxn 1 Sender => . </k>
        <stack> XS => SENDER:Bytes : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <lastTxnGroupID> "2" </lastTxnGroupID>
        <transactions>
          <transaction>
            <txID> "3" </txID>
            <groupID> "2" </groupID>
            <groupIdx> 1 </groupIdx>
            <sender> SENDER:Bytes </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000

// gitxna t f i 	6 	implemented, not tested 	1
  claim <k> gitxna 1 ApplicationArgs 2 => . </k>
        <stack> XS => 123 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
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

// gloadss 	6 	implemented, not tested 	1
  claim <k> gloadss => . </k>
        <stack> 3 : 0 : XS => 123 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> "2" </currentTx>
        <transactions>
          <transaction>
            <txID> "1" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            <txScratch> 3 |-> 123 </txScratch>
            ...
          </transaction>
          <transaction>
            <txID> "2" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 1 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <groupSize> 2 </groupSize>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (0 |-> "1") (1 |-> "2") </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000

// itxnas f 	6 	not implemented 	1
// gitxnas t f 	6 	not implemented 	1

endmodule
