module OPCODES-V6-SPEC
  imports VERIFICATION

// acct_params_get f 	6 	not implemented 	1
// bsqrt 	6 	not implemented 	40
// divw 	6 	not implemented 	1
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
