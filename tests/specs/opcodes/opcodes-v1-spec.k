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
// intc i 	1 	heavy_check_mark 	1
// intc_0 i 	1 	heavy_check_mark 	1
// intc_1 	1 	heavy_check_mark 	1
// intc_2 	1 	heavy_check_mark 	1
// intc_3 	1 	heavy_check_mark 	1
// bytecblock 	1 	heavy_check_mark 	1
// bytec i 	1 	heavy_check_mark 	1
// bytec_0 	1 	heavy_check_mark 	1
// bytec_1 	1 	heavy_check_mark 	1
// bytec_2 	1 	heavy_check_mark 	1
// bytec_3 	1 	heavy_check_mark 	1
// arg n 	1 	heavy_check_mark 	1
// arg_0 	1 	heavy_check_mark 	1
// arg_1 	1 	heavy_check_mark 	1
// arg_2 	1 	heavy_check_mark 	1
// arg_3 	1 	heavy_check_mark 	1

// txn f 	1 	heavy_check_mark 	1
// global f 	1 	heavy_check_mark 	1
// gtxn t f 	1 	heavy_check_mark 	1
// load i 	1 	heavy_check_mark 	1
// store i 	1 	heavy_check_mark 	1
// pop 	1 	heavy_check_mark 	1
// dup 	1 	heavy_check_mark 	1 

endmodule
