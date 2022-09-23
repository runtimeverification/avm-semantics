module OPCODES-V1-SPEC
  imports VERIFICATION

// err 	1 	heavy_check_mark 	1
  claim <k> err => panic(ERR_OPCODE) ...</k>

// sha256 	1 	heavy_check_mark 	35
//  claim <k> sha256 </k>
//        <stack> A:Bytes : XS => String2Bytes(Sha256raw(Bytes2String(A:Bytes))) : XS </stack>

// keccak256 	1 	heavy_check_mark 	130
// sha512_256 	1 	heavy_check_mark 	45
// ed25519verify 	1 	heavy_check_mark 	1900

// + 	1 	heavy_check_mark 	1
  claim <k> + => . ...</k>
        <stack> 5 : 3 : XS => 8 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> + => panic(INT_OVERFLOW) ...</k>
        <stack> MAX_UINT64 : 3 : _ </stack>

// - 	1 	heavy_check_mark 	1
  claim <k> - => . ...</k>
        <stack> 6 : 10 : XS => 4 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> - => panic(INT_UNDERFLOW) ...</k>
        <stack> 10 : 6 : _ </stack>

// / 	1 	heavy_check_mark 	1
  claim <k> / => . ...</k>
        <stack> 5 : 30 : XS => 6 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> / => panic(DIV_BY_ZERO) ...</k>
        <stack> 0 : 30 : _</stack>

// * 	1 	heavy_check_mark 	1
  claim <k> * => . ...</k>
        <stack> 6 : 7 : XS => 42 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> * => panic(INT_OVERFLOW) ...</k>
        <stack> MAX_UINT64 : 2 : _ </stack>

// < 	1 	heavy_check_mark 	1
  claim <k> < => . ...</k>
        <stack> 5 : 3 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> < => . ...</k>
        <stack> 3 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> < => . ...</k>
        <stack> 5 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// > 	1 	heavy_check_mark 	1
  claim <k> > => . ...</k>
        <stack> 5 : 3 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> > => . ...</k>
        <stack> 3 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> > => . ...</k>
        <stack> 5 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// <= 	1 	heavy_check_mark 	1
  claim <k> <= => . ...</k>
        <stack> 5 : 3 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> <= => . ...</k>
        <stack> 3 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> <= => . ...</k>
        <stack> 5 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// >= 	1 	heavy_check_mark 	1
  claim <k> >= => . ...</k>
        <stack> 5 : 3 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> >= => . ...</k>
        <stack> 3 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> >= => . ...</k>
        <stack> 5 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// && 	1 	heavy_check_mark 	1
  claim <k> && => . ...</k>
        <stack> 3 : 1 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> && => . ...</k>
        <stack> 0 : 1 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> && => . ...</k>
        <stack> 5 : 0 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> && => . ...</k>
        <stack> 0 : 0 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// || 	1 	heavy_check_mark 	1
  claim <k> || => . ...</k>
        <stack> 3 : 1 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> || => . ...</k>
        <stack> 0 : 1 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> || => . ...</k>
        <stack> 5 : 0 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> || => . ...</k>
        <stack> 0 : 0 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// == 	1 	heavy_check_mark 	1
  claim <k> == => . ...</k>
        <stack> 2 : 2 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> == => . ...</k>
        <stack> 4 : 2 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> == => . ...</k>
        <stack> b"123" : b"123" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> == => . ...</k>
        <stack> b"123" : b"321" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// != 	1 	heavy_check_mark 	1
  claim <k> != => . ...</k>
        <stack> 2 : 2 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> != => . ...</k>
        <stack> 4 : 2 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> != => . ...</k>
        <stack> b"123" : b"123" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> != => . ...</k>
        <stack> b"123" : b"321" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// ! 	1 	heavy_check_mark 	1
  claim <k> ! => . ...</k>
        <stack> 1 : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> ! => . ...</k>
        <stack> 5 : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> ! => . ...</k>
        <stack> 0 : XS => 1 : XS </stack>
        <stacksize> _ </stacksize>

// len 	1 	heavy_check_mark 	1
  claim <k> len => . ...</k>
        <stack> b"123456" : XS => 6 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> len => . ...</k>
        <stack> b"" : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>

// itob 	1 	heavy_check_mark 	1
  claim <k> itob => . ...</k>
        <stack> 6382179 : XS => b"abc" : XS </stack>
        <stacksize> _ </stacksize>

// btoi 	1 	heavy_check_mark 	1
  claim <k> btoi => . ...</k>
        <stack> b"abc" : XS => 6382179 : XS </stack>
        <stacksize> _ </stacksize>

//  claim <k> btoi => panic(?_) </k>
//        <stack> b"123456789" : _</stack>
//        <stacksize> _ </stacksize>

// % 	1 	heavy_check_mark 	1
  claim <k> % => . ...</k>
        <stack> 3 : 5 : XS => 2 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> % => panic(DIV_BY_ZERO) ...</k>
        <stack> 0 : 5 : _ </stack>

// | 	1 	heavy_check_mark 	1
  claim <k> | => . ...</k>
        <stack> 123 : 321 : XS => 379 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// & 	1 	heavy_check_mark 	1
  claim <k> & => . ...</k>
        <stack> 123 : 321 : XS => 65 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// ^ 	1 	heavy_check_mark 	1
  claim <k> ^ => . ...</k>
        <stack> 123 : 321 : XS => 314 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// ~ 	1 	heavy_check_mark 	1
//  claim <k> ~ => . </k>
//        <stack> 123 : XS => 18446744073709551492 : XS </stack>
//        <stacksize> _ </stacksize>

// mulw 	1 	heavy_check_mark 	1
  claim <k> mulw => . </k>
        <stack> 123456789012345 : 123456789012345 : XS => 15098910126093764401 : 826247639 : XS </stack>
        <stacksize> _ </stacksize>

// intcblock 	1 	heavy_check_mark 	1
  claim <k> intcblock 3 4 5 6 => . </k>
        <intcblock> _ => 
                   (0 |-> 4
                    1 |-> 5
                    2 |-> 6)
        </intcblock>
// intc i 	1 	heavy_check_mark 	1
  claim <k> intc 1 => . </k>
        <stack> XS => 5 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
        </intcblock>
    requires S <Int 1000

// intc_0 	1 	heavy_check_mark 	1
  claim <k> intc_0 => . </k>
        <stack> XS => 4 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000

// intc_1 	1 	heavy_check_mark 	1
  claim <k> intc_1 => . </k>
        <stack> XS => 5 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000

// intc_2 	1 	heavy_check_mark 	1
  claim <k> intc_2 => . </k>
        <stack> XS => 6 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000

// intc_3 	1 	heavy_check_mark 	1
  claim <k> intc_3 => . </k>
        <stack> XS => 7 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000

// bytecblock 	1 	heavy_check_mark 	1
  claim <k> bytecblock 3 (1, "1") (1, "2") (1,"3") => . </k>
        <bytecblock> _ => 
                   (0 |-> "1"
                    1 |-> "2"
                    2 |-> "3")
        </bytecblock>

// bytec i 	1 	heavy_check_mark 	1
  claim <k> bytec 1 => . </k>
        <stack> XS => "2" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
        </bytecblock>
    requires S <Int 1000

// bytec_0 	1 	heavy_check_mark 	1
  claim <k> bytec_0 => . </k>
        <stack> XS => "1" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000

// bytec_1 	1 	heavy_check_mark 	1
  claim <k> bytec_1 => . </k>
        <stack> XS => "2" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000

// bytec_2 	1 	heavy_check_mark 	1
  claim <k> bytec_2 => . </k>
        <stack> XS => "3" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000

// bytec_3 	1 	heavy_check_mark 	1
  claim <k> bytec_3 => . </k>
        <stack> XS => "4" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000

// // arg n 	1 	heavy_check_mark 	1
//   claim <k> arg 2 => . </k>
//         <stack> XS => 6 : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <args> 0 |-> 4
//                1 |-> 5
//                2 |-> 6
//                3 |-> 7
//         </args>
//     requires S <Int 1000
// 
// // arg_0 	1 	heavy_check_mark 	1
//   claim <k> arg_0 => . </k>
//         <stack> XS => 4 : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <args> 0 |-> 4
//                1 |-> 5
//                2 |-> 6
//                3 |-> 7
//         </args>
//     requires S <Int 1000
// 
// // arg_1 	1 	heavy_check_mark 	1
//   claim <k> arg_1 => . </k>
//         <stack> XS => 5 : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <args> 0 |-> 4
//                1 |-> 5
//                2 |-> 6
//                3 |-> 7
//         </args>
//     requires S <Int 1000
// 
// // arg_2 	1 	heavy_check_mark 	1
//   claim <k> arg_2 => . </k>
//         <stack> XS => 6 : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <args> 0 |-> 4
//                1 |-> 5
//                2 |-> 6
//                3 |-> 7
//         </args>
//     requires S <Int 1000
// 
// // arg_3 	1 	heavy_check_mark 	1
//   claim <k> arg_3 => . </k>
//         <stack> XS => 7 : XS </stack>
//         <stacksize> S => S +Int 1 </stacksize>
//         <args> 0 |-> 4
//                1 |-> 5
//                2 |-> 6
//                3 |-> 7
//         </args>
//     requires S <Int 1000

// txn f 	1 	heavy_check_mark 	1
  claim <k> txn Sender => . </k>
        <stack> XS => SENDER : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <group> TX_ID </group>
            <sender> SENDER:Bytes </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000

// global f 	1 	heavy_check_mark 	1
  claim <k> global MinBalance => . </k>
        <stack> XS => 100000 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000

// gtxn t f 	1 	heavy_check_mark 	1
  claim <k> gtxn 0 Sender => . </k>
        <stack> XS => SENDER : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> 1 </currentTx>
        <transactions>
          <transaction>
            <txID> 0 </txID>
            <group> 0 </group>
            <sender> SENDER:Bytes </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
          <transaction>
            <txID> 1 </txID>
            <group> 1 </group>
            <sender> SENDER:Bytes </sender>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
    requires S <Int 1000

// load i 	1 	heavy_check_mark 	1
  claim <k> load 1 => . </k>
        <stack> XS => VALUE : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <scratch> (2 |-> _) (1 |-> VALUE) (4 |-> _) </scratch>
    requires S <Int 1000

  claim <k> load 3 => . </k>
        <stack> XS => 0 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <scratch> (2 |-> _) (1 |-> _) (4 |-> _) (.Map => (3 |-> 0)) </scratch>
    requires S <Int 1000

// store i 	1 	heavy_check_mark 	1
  claim <k> store 1 => . </k>
        <stack> VALUE : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <scratch> (2 |-> _) (1 |-> (_ => VALUE)) (4 |-> _) </scratch>

// pop 	1 	heavy_check_mark 	1
  claim <k> pop => . </k>
        <stack> _ : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// dup 	1 	heavy_check_mark 	1 
  claim <k> dup => . </k>
        <stack> VAL : XS => VAL : VAL : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000

endmodule
