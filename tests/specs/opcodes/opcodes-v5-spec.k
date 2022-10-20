module OPCODES-V5-SPEC
  imports VERIFICATION

// ecdsa_verify 	5 	x 	1700
// ecdsa_pk_decompress 	5 	x 	650
// ecdsa_pk_recover 	5 	x 	2000

// loads 	5 	heavy_check_mark 	1
// claim <k> loads => . </k>
//       <stack> 5 : XS => 8 : XS </stack>
//       <scratch> 5 |-> 8 </scratch>
// 
// // stores 	5 	heavy_check_mark 	1
// claim <k> stores => . </k>
//       <stack> 8 : 5 : XS => XS </stack>
//       <stacksize> S => S -Int 2 </stacksize>
//       <scratch> .Map => (5 |-> 8) </scratch>
// 
// // cover 	5 	heavy_check_mark 	1
// claim <k> cover 3 => . </k>
//       <stack> 123 : 0 : 0 : 0 : XS => 0 : 0 : 0 : 123 : XS </stack>
//       <stacksize> S </stacksize>
//   requires S >=Int 4
// 
// claim <k> cover 3 => panic(STACK_UNDERFLOW) </k>
//       <stack> 123 : 0 : 0 : .TStack </stack>
//       <stacksize> 3 </stacksize>
// 
// // uncover 	5 	heavy_check_mark 	1
// claim <k> uncover 3 => . </k>
//       <stack> 0 : 0 : 0 : 123 : XS => 123 : 0 : 0 : 0 : XS </stack>
//       <stacksize> S </stacksize>
//   requires S >=Int 4
// 
// claim <k> uncover 3 => panic(STACK_UNDERFLOW) </k>
//       <stack> 123 : 0 : 0 : .TStack </stack>
//       <stacksize> 3 </stacksize>
// 
// // extract 	5 	heavy_check_mark 	1
// claim <k> extract 2 3 => . </k>
//       <stack> b"abcdefg" : XS => b"cde" : XS </stack>
// 
// // extract3 	5 	heavy_check_mark 	1
// claim <k> extract3 => . </k>
//       <stack> 3 : 2 : b"abcdefg" : XS => b"cde" : XS </stack>
//       <stacksize> S => S -Int 2 </stacksize>
// 
// // extract_uint16 	5 	heavy_check_mark 	1
// claim <k> extract_uint16 => . </k>
//       <stack> 2 : b"\xff\xff\x00\x03\xff" : XS => 3 : XS </stack>
//       <stacksize> S => S -Int 1 </stacksize>
// 
// // extract_uint32 	5 	heavy_check_mark 	1
// claim <k> extract_uint32 => . </k>
//       <stack> 2 : b"\xff\xff\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
//       <stacksize> S => S -Int 1 </stacksize>
// 
// // extract_uint64 	5 	heavy_check_mark 	1
// claim <k> extract_uint64 => . </k>
//       <stack> 2 : b"\xff\xff\x00\x00\x00\x00\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
//       <stacksize> S => S -Int 1 </stacksize>
// 
// // app_params_get 	5 	x 	1
// 
// // log 	5 	heavy_check_mark 	1
// claim <k> log => . </k>
//       <stack> b"abc" : XS => XS </stack>
//       <stacksize> S => S -Int 1 </stacksize>
//       <currentTx> TX_ID </currentTx>
//       <transaction>
//         <txID> TX_ID </txID>
//         <logData> LOG => append(b"abc", LOG) </logData>
//         <logSize> LS => LS +Int 3 </logSize>
//         ...
//       </transaction>
//   requires LS <=Int 1024 -Int 3
//    andBool size(LOG) <Int 32
// 
// // itxn_begin 	5 	heavy_check_mark 	1
//   claim <k> itxn_begin => . </k>
//         <currentTx> "1" </currentTx>
//         <transactions>
//           <transaction>
//             <txID> "1" </txID>
//             <firstValid> 0 </firstValid>
//             <lastValid> 100 </lastValid>
//             <typeEnum> @ appl </typeEnum>
//             ...
//           </transaction>
//         </transactions>
//         <currentApplicationAddress> b"application1" </currentApplicationAddress>
//         <innerTransactions>
//           .List =>
//           ListItem(
//             <transaction>
//               <txID> "" </txID>
//               <txHeader>
//                  <fee> 0 </fee>
//                  <sender> b"application1" </sender>
//                  <firstValid> 0 </firstValid>
//                  <lastValid> 100 </lastValid>
//                  <genesisHash> .Bytes </genesisHash>
//                  <txType> "unknown" </txType>
//                  <typeEnum> 0 </typeEnum>
//                  <groupID> "33" </groupID>
//                  <groupIdx> 0 </groupIdx>
//                  <genesisID> .Bytes </genesisID>
//                  <lease> .Bytes </lease>
//                  <note> .Bytes </note>
//                  <rekeyTo> ?_ </rekeyTo>
//               </txHeader>
//               <txnTypeSpecificFields>
//                 .Bag
//               </txnTypeSpecificFields>
//               <applyData>
//                 <txScratch>       .Map  </txScratch>
//                 <txConfigAsset>   0     </txConfigAsset>
//                 <txApplicationID> 0     </txApplicationID>
//                 <log>
//                   <logData> .TValueList </logData>
//                   <logSize> 0:TValue    </logSize>
//                 </log>
//               </applyData>
//               <txnExecutionContext> .K </txnExecutionContext>
//               <resume> false </resume>
//             </transaction>
//           )
//         </innerTransactions>
//         <nextGroupID> 32 => 33 </nextGroupID>
// 
// // itxn_field 	5 	heavy_check_mark 	1
//   claim <k> itxn_field TypeEnum => . </k>
//         <stack> 3 : XS => XS </stack>
//         <stacksize> S => S -Int 1 </stacksize>
//         <innerTransactions>
//           ...
//           ListItem(
//             <transaction>
//                <txType> _ => b"acfg" </txType>
//                <typeEnum> _ => 3 </typeEnum>
//                ...
//             </transaction>
//           )
//         </innerTransactions>
// 
//   claim <k> itxn_field ConfigAssetUnitName => . </k>
//         <stack> b"abcdefg" : XS => XS </stack>
//         <stacksize> S => S -Int 1 </stacksize>
//         <innerTransactions>
//           ...
//           ListItem(
//             <transaction>
//               <configUnitName> _ => b"abcdefg" </configUnitName>
//                ...
//             </transaction>
//           )
//         </innerTransactions>
// 
//   claim <k> itxn_field ConfigAssetUnitName => . </k>
//         <stack> b"abcdefg" : XS => XS </stack>
//         <stacksize> S => S -Int 1 </stacksize>
//         <innerTransactions>
//           ...
//           ListItem(
//             <transaction>
//               <txnTypeSpecificFields>
//                 .Bag => 
//                 <assetConfigTxFields>
//                   <configAsset> ?_ </configAsset>
//                   <assetParams>
//                     <configUnitName> b"abcdefg" </configUnitName>
//                     ?_
//                   </assetParams>
//                 </assetConfigTxFields>
//               </txnTypeSpecificFields>
//               ...
//             </transaction>
//           )
//         </innerTransactions>
//         
// 
// // itxn_submit 	5 	heavy_check_mark 	1
//   claim <k> itxn_submit => . </k>
//         <currentTxnExecution> 
//           <pc> 0 </pc>
//           <program> .Map </program>
//           <jumped> true => false </jumped>
//           <currentApplicationID> 1 </currentApplicationID>
//           <stack> 1 : .TStack </stack>
//           <stacksize> 1 </stacksize>
//           <lastTxnGroupID> "1" </lastTxnGroupID>
//           ...
//         </currentTxnExecution>
//         <returncode> 4 => 0 </returncode>
//         <returnstatus> _ => "Success - transaction group accepted" </returnstatus>
//         <activeApps> SetItem(1) => .Set </activeApps>
//         <touchedAccounts> .Set </touchedAccounts>
//         <currentTx> "1" </currentTx>
//         <transactions>
//           <transaction>
//             <txID> "1" </txID>
//             <groupID> "1" </groupID>
//             <sender> b"3" </sender>
//             <resume> true </resume>
//             ...
//           </transaction>
//           => ?_
//         </transactions>
//         <innerTransactions>
//           ListItem(
//             <transaction>
//               <txID> _ </txID>
//               <txHeader> 
//                 <txType> b"pay" </txType>
//                 <typeEnum> 1 </typeEnum>
//                 <groupID> "2" </groupID>
//                 <sender> b"application1" </sender>
//                 ... 
//               </txHeader>
//               <txnTypeSpecificFields>
//                 <payTxFields>
//                   <receiver> b"3" </receiver>
//                   <amount> 1000 </amount>
//                   ...
//                 </payTxFields>
//               </txnTypeSpecificFields>
//               <resume> false </resume>
//               ...
//             </transaction>)
//             => .List
//         </innerTransactions>
//         <nextTxnID> 5 => 6 </nextTxnID>
//         <nextGroupID> 1 </nextGroupID>
//         <deque> ListItem("1") => .List </deque>
//         <dequeIndexSet> SetItem("1") => (SetItem("1") SetItem("5")) </dequeIndexSet>
//         <txnIndexMap> .Bag => ?_ </txnIndexMap>
//         <accountsMap>
//           <account>
//             <address> b"application1" </address>
//             <minBalance> 10000 </minBalance>
//             <balance> 100000000 => 100000000 -Int 1000 </balance>
//             ...
//           </account>
//           <account>
//             <address> b"3" </address>
//             <minBalance> 10000 </minBalance>
//             <balance> 100000000 => 100000000 +Int 1000 </balance>
//             ...
//           </account>
//         </accountsMap>

// itxn 	5 	heavy_check_mark 	1
  claim <k> itxn Sender => . </k>
        <stack> XS => SENDER:Bytes : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <lastTxnGroupID> "2" </lastTxnGroupID>
        <transactions>
          <transaction>
            <txID> "3" </txID>
            <groupID> "2" </groupID>
            <groupIdx> 0 </groupIdx>
            <sender> SENDER:Bytes </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000

// itxna 	5 	heavy_check_mark 	1
  claim <k> itxna ApplicationArgs 1 => . </k>
        <stack> XS => 123 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
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

// txnas 	5 	heavy_check_mark 	1
  claim <k> txnas Applications => . </k>
        <stack> 1 : XS => APPL : XS </stack>
        <stacksize> S </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <groupID> "0" </groupID>
          <groupIdx> 0 </groupIdx>
          <typeEnum> @ appl </typeEnum>
          <foreignApps> 3 APPL:Int 7 </foreignApps>
          ...
        </transaction>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (0 |-> TX_ID) ... </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000

// gtxnas 	5 	heavy_check_mark 	1
  claim <k> gtxnas 0 ApplicationArgs => . </k>
        <stack> 1 : XS => b"123" : XS </stack>
        <stacksize> S </stacksize>
        <currentTx> "2a" </currentTx>
        <transactions>
          <transaction>
            <txID> "0" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <applicationArgs> b"456" b"123" </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
          <transaction>
            <txID> "2a" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 2 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (2 |-> "2a") (0 |-> "0") </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000

// gtxnsas 	5 	heavy_check_mark 	1
  claim <k> gtxnsas ApplicationArgs => . </k>
        <stack> 1 : 0 : XS => b"123" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> "2a" </currentTx>
        <transactions>
          <transaction>
            <txID> "0" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <applicationArgs> b"456" b"123" </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
          <transaction>
            <txID> "2a" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 2 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (2 |-> "2a") (0 |-> "0") </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000

// args 	5 	heavy_check_mark 	1    

endmodule
