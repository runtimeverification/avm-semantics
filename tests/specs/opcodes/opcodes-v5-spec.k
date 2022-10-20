module OPCODES-V5-SPEC
  imports VERIFICATION

// ecdsa_verify 	5 	x 	1700
// ecdsa_pk_decompress 	5 	x 	650
// ecdsa_pk_recover 	5 	x 	2000

// loads 	5 	heavy_check_mark 	1
claim <k> loads => . </k>
      <stack> 5 : XS => 8 : XS </stack>
      <scratch> 5 |-> 8 </scratch>

// stores 	5 	heavy_check_mark 	1
claim <k> stores => . </k>
      <stack> 8 : 5 : XS => XS </stack>
      <stacksize> S => S -Int 2 </stacksize>
      <scratch> .Map => (5 |-> 8) </scratch>

// cover 	5 	heavy_check_mark 	1
claim <k> cover 3 => . </k>
      <stack> 123 : 0 : 0 : 0 : XS => 0 : 0 : 0 : 123 : XS </stack>
      <stacksize> S </stacksize>
  requires S >=Int 4

claim <k> cover 3 => panic(STACK_UNDERFLOW) </k>
      <stack> 123 : 0 : 0 : .TStack </stack>
      <stacksize> 3 </stacksize>

// uncover 	5 	heavy_check_mark 	1
claim <k> uncover 3 => . </k>
      <stack> 0 : 0 : 0 : 123 : XS => 123 : 0 : 0 : 0 : XS </stack>
      <stacksize> S </stacksize>
  requires S >=Int 4

claim <k> uncover 3 => panic(STACK_UNDERFLOW) </k>
      <stack> 123 : 0 : 0 : .TStack </stack>
      <stacksize> 3 </stacksize>

// extract 	5 	heavy_check_mark 	1
claim <k> extract 2 3 => . </k>
      <stack> b"abcdefg" : XS => b"cde" : XS </stack>

// extract3 	5 	heavy_check_mark 	1
claim <k> extract3 => . </k>
      <stack> 3 : 2 : b"abcdefg" : XS => b"cde" : XS </stack>
      <stacksize> S => S -Int 2 </stacksize>

// extract_uint16 	5 	heavy_check_mark 	1
claim <k> extract_uint16 => . </k>
      <stack> 2 : b"\xff\xff\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// extract_uint32 	5 	heavy_check_mark 	1
claim <k> extract_uint32 => . </k>
      <stack> 2 : b"\xff\xff\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// extract_uint64 	5 	heavy_check_mark 	1
claim <k> extract_uint64 => . </k>
      <stack> 2 : b"\xff\xff\x00\x00\x00\x00\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// app_params_get 	5 	x 	1

// log 	5 	heavy_check_mark 	1
claim <k> log => . </k>
      <stack> b"abc" : XS => XS </stack>
      <stacksize> S => S -Int 1 </stacksize>
      <currentTx> TX_ID </currentTx>
      <transaction>
        <txID> TX_ID </txID>
        <logData> LOG => append(b"abc", LOG) </logData>
        <logSize> LS => LS +Int 3 </logSize>
        ...
      </transaction>
  requires LS <=Int 1024 -Int 3
   andBool size(LOG) <Int 32

// itxn_begin 	5 	heavy_check_mark 	1
claim <k> itxn_begin => . </k>
      <currentTx> "1" </currentTx>
      <transactions>
        <transaction>
          <txID> "1" </txID>
          <firstValid> 0 </firstValid>
          <lastValid> 100 </lastValid>
          <typeEnum> @ appl </typeEnum>
          ...
        </transaction>
      </transactions>
      <currentApplicationAddress> b"application1" </currentApplicationAddress>
      <innerTransactions>
        .List =>
        ListItem(
          <transaction>
            <txID> "" </txID>
            <txHeader>
               <fee> 0 </fee>
               <sender> b"application1" </sender>
               <firstValid> 0 </firstValid>
               <lastValid> 100 </lastValid>
               <genesisHash> .Bytes </genesisHash>
               <txType> "unknown" </txType>
               <typeEnum> 0 </typeEnum>
               <groupID> "33" </groupID>
               <groupIdx> 0 </groupIdx>
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
          </transaction>
        )
      </innerTransactions>
      <nextGroupID> 32 => 33 </nextGroupID>

// itxn_field 	5 	heavy_check_mark 	1
// itxn_submit 	5 	heavy_check_mark 	1
// itxn 	5 	heavy_check_mark 	1
// itxna 	5 	heavy_check_mark 	1
// txnas 	5 	heavy_check_mark 	1
// gtxnas 	5 	heavy_check_mark 	1
// gtxnsas 	5 	heavy_check_mark 	1
// args 	5 	heavy_check_mark 	1    

endmodule
