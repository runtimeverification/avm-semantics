module OPCODES-V2-SPEC
  imports VERIFICATION

// // addw 	2 	heavy_check_mark 	1
//   claim <k> addw => . </k>
//         <stack> 18446744073709551615 : 5 : XS => 4 : 1 : XS </stack>
//         <stacksize> _ </stacksize>
// 
// // txna f i 	2 	heavy_check_mark 	1
//   claim <k> txna Applications 1 => . </k>
//         <stack> XS => APPL : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <currentTx> TX_ID </currentTx>
//         <transaction>
//           <txID> TX_ID </txID>
//           <groupID> "0" </groupID>
//           <groupIdx> 0 </groupIdx>
//           <typeEnum> @ appl </typeEnum>
//           <foreignApps> 3 APPL:Int 7 </foreignApps>
//           ...
//         </transaction>
//     requires S <Int 1000
        
// gtxna t f i 	2 	heavy_check_mark 	1
//   claim <k> gtxna 0 Applications 1 => . </k>
// //        <stack> XS => APPL : XS </stack>
//         <stack> XS => SENDER : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <currentTx> "2" </currentTx>
//         <transactions>
//           <transaction>
//             <txID> "2" </txID>
//             <groupID> "0" </groupID>
//             <groupIdx> 2 </groupIdx>
//             <sender> SENDER:Bytes </sender>
//             <typeEnum> @ appl </typeEnum>
//             ...
//           </transaction>
//           <transaction>
//             <txID> "0" </txID>
//             <groupID> "0" </groupID>
//             <groupIdx> 0 </groupIdx>
//             <typeEnum> @ appl </typeEnum>
//             <sender> SENDER:Bytes </sender>
// //            <foreignApps> 3 APPL:Int 7 </foreignApps>
//             ...
//           </transaction>
//         </transactions>
//     requires S <Int 1000

//   claim <k> gtxna 0 ApplicationArgs 1 => . </k>
//         <stack> XS => SENDER : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <currentTx> "2a" </currentTx>
//         <transactions>
//           <transaction>
//             <txID> "0" </txID>
//             <groupID> "0" </groupID>
//             <groupIdx> 0 </groupIdx>
//             <sender> SENDER:Bytes </sender>
//             <typeEnum> @ appl </typeEnum>
//             ...
//           </transaction>
//           <transaction>
//             <txID> "2a" </txID>
//             <groupID> "0" </groupID>
//             <groupIdx> 2 </groupIdx>
//             <typeEnum> @ appl </typeEnum>
//             ...
//           </transaction>
//         </transactions>
//     requires S <Int 1000

// // concat 	2 	heavy_check_mark 	1
//   claim <k> concat => . </k>
//         <stack> b"def" : b"abc" : XS => b"abcdef" : XS </stack>
//         <stacksize> S => S -Int 1 </stacksize>
// 
//   claim <k> concat => panic(BYTES_OVERFLOW) </k>
//         <stack> B2 : B1 : _ </stack>
//     requires lengthBytes(B1) +Int lengthBytes(B2) >Int 4096

// substring s e 	2 	heavy_check_mark 	1
// substring3 	2 	heavy_check_mark 	1
// dup2 	2 	heavy_check_mark 	1
// balance 	2 	heavy_check_mark 	1
// app_opted_in 	2 	heavy_check_mark 	1
// app_local_get 	2 	heavy_check_mark 	1
// app_local_get_ex 	2 	heavy_check_mark 	1
// app_global_get 	2 	heavy_check_mark 	1
// app_global_get_ex 	2 	heavy_check_mark 	1
// app_local_put 	2 	heavy_check_mark 	1
// app_global_put 	2 	heavy_check_mark 	1
// app_local_del 	2 	heavy_check_mark 	1
// app_global_del 	2 	heavy_check_mark 	1
// asset_holding_get i 	2 	heavy_check_mark 	1
// asset_params_get i 	2 	heavy_check_mark 	1
// return 	2 	heavy_check_mark 	1
// bnz target 	2 (4) 	heavy_check_mark 	1
// bz target 	2 (4) 	heavy_check_mark 	1
// b target 	2 (4) 	heavy_check_mark 	1

endmodule
