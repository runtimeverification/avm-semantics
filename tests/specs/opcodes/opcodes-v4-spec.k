module OPCODES-V4-SPEC
  imports VERIFICATION
    
// divmodw 	4 	heavy_check_mark 	20
//   claim <k> divmodw => . </k>
//         <stack> 3 : 3 : 9 : 6 : XS => 3 : 2 : 0 : 0 : XS </stack>
  
// gload t i 	4 	heavy_check_mark 	1
  claim <k> gload 0 3 => . </k>
        <stack> XS => 123 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
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
  
// gloads i 	4 	heavy_check_mark 	1
  claim <k> gloads 3 => . </k>
        <stack> 0 : XS => 123 : XS </stack>
        <stacksize> S </stacksize>
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

// gaid t 	4 	heavy_check_mark 	1
  claim <k> gaid 0 => . </k>
        <stack> XS => 123 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> "2" </currentTx>
        <transactions>
          <transaction>
            <txID> "1" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            <txApplicationID> 123 </txApplicationID>
            <applicationID> 123 </applicationID>
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
        <txnIndexMap>
          <txnIndexMapGroup>
            <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
            <txnIndexMapGroupValues> (0 |-> "1") (1 |-> "2") </txnIndexMapGroupValues>
          </txnIndexMapGroup>
        </txnIndexMap>
    requires S <Int 1000

// gaids 	4 	heavy_check_mark 	1
  claim <k> gaids => . </k>
        <stack> 0 : XS => 123 : XS </stack>
        <stacksize> S </stacksize>
        <currentTx> "2" </currentTx>
        <transactions>
          <transaction>
            <txID> "1" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            <txApplicationID> 123 </txApplicationID>
            <applicationID> 123 </applicationID>
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
        <txnIndexMap>
          <txnIndexMapGroup>
            <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
            <txnIndexMapGroupValues> (0 |-> "1") (1 |-> "2") </txnIndexMapGroupValues>
          </txnIndexMapGroup>
        </txnIndexMap>
    requires S <Int 1000

// callsub target 	4 	heavy_check_mark 	1
  claim <k> callsub LABEL => . </k>
        <callStack> (.List => ListItem(CURRENT_PC +Int 1)) CS </callStack>
        <pc> CURRENT_PC:Int => JUMP_PC </pc>
        <labels> .Map[LABEL <- JUMP_PC] </labels>
        <jumped> _ => true </jumped>
    requires size(CS) <Int MAX_CALLSTACK_DEPTH

// retsub 	4 	heavy_check_mark 	1
  claim <k> retsub => . </k>
        <callStack> (ListItem(RET_PC) => .List) _ </callStack>
        <pc> _ => RET_PC </pc>
        <jumped> _ => true </jumped>

// shl 	4 	heavy_check_mark 	1
  claim <k> shl => . </k>
        <stack> 5 : 1 : XS => 32 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> shl => . </k>
        <stack> 1 : (2 ^Int 63) : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// shr 	4 	heavy_check_mark 	1
  claim <k> shr => . </k>
        <stack> 5 : 64 : XS => 2 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> shr => . </k>
        <stack> 3 : 2 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

// sqrt 	4 	heavy_check_mark 	4
// Square root algorithm is currently very slow for verification.
//   claim <k> sqrt => . </k>
//         <stack> 15 : XS => 3 : XS </stack>

// bitlen 	4 	heavy_check_mark 	1
  claim <k> bitlen => . </k>
        <stack> 8 : XS => 4 : XS </stack>

  claim <k> bitlen => . </k>
        <stack> 10 : XS => 4 : XS </stack>

  claim <k> bitlen => . </k>
        <stack> b"\x10" : XS => 5 : XS </stack>
        
// exp 	4 	heavy_check_mark 	1
  claim <k> exp => . </k>
        <stack> 5 : 3 : XS => 243 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> exp => panic(INVALID_ARGUMENT) </k>
        <stack> 0 : 0 : _ </stack>

  claim <k> exp => panic(INT_OVERFLOW) </k>
        <stack> 100 : 2 : _ </stack>

// expw 	4 	heavy_check_mark 	1
  claim <k> expw => . </k>
        <stack> 5 : 3 : XS => 243 : 0 : XS </stack>

  claim <k> expw => . </k>
        <stack> 64 : 2 : XS => 0 : 1 : XS </stack>

  claim <k> expw => panic(INVALID_ARGUMENT) </k>
        <stack> 0 : 0 : _ </stack>

  claim <k> expw => panic(INT_OVERFLOW) </k>
        <stack> 150 : 2 : _ </stack>

// b+ 	4 	heavy_check_mark 	10
  claim <k> b+ => . </k>
        <stack> b"\x03" : b"\x04" : XS => b"\x07" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  // Are byte operations supposed to be able to overflow?
  claim <k> b+ => . </k>
        <stack> b"\x01\x00\x00\x00\x00\x00\x00\x00\x00" : b"\x04" : XS 
            =>  b"\x01\x00\x00\x00\x00\x00\x00\x00\x04": XS
        </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b+ => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
  
// b- 	4 	heavy_check_mark 	10
  claim <k> b- => . </k>
        <stack> b"\x03" : b"\x04" : XS => b"\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b- => panic(INT_UNDERFLOW) </k>
        <stack> b"\x07" : b"\x04" : _ </stack>

  claim <k> b- => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b/ 	4 	heavy_check_mark 	20
  claim <k> b/ => . </k>
        <stack> b"\x02" : b"\x08" : XS => b"\x04" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b/ => panic(DIV_BY_ZERO) </k>
        <stack> b"\x00" : b"\x04" : _ </stack>

  claim <k> b/ => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b* 	4 	heavy_check_mark 	20
  claim <k> b* => . </k>
        <stack> b"\x03" : b"\x04" : XS => b"\x0c" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  // Are byte operations supposed to be able to overflow?
  claim <k> b* => . </k>
        <stack> b"\x02\x00\x00\x00\x00\x00" : b"\x02\x00\x00\x00" : XS 
            =>  b"\x04\x00\x00\x00\x00\x00\x00\x00\x00": XS
        </stack>
        <stacksize> S => S -Int 1 </stacksize>
        
  claim <k> b* => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b< 	4 	heavy_check_mark 	1
  claim <k> b< => . </k>
        <stack> b"\x10\x00" : b"\x01\x00" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b< => . </k>
        <stack> b"\x10\x00" : b"\x10\x01" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b< => . </k>
        <stack> b"\x10\x01" : b"\x10\x01" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b< => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b> 	4 	heavy_check_mark 	1
  claim <k> b> => . </k>
        <stack> b"\x10\x00" : b"\x01\x00" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b> => . </k>
        <stack> b"\x10\x00" : b"\x10\x01" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b> => . </k>
        <stack> b"\x10\x01" : b"\x10\x01" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b> => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b<= 	4 	heavy_check_mark 	1
  claim <k> b<= => . </k>
        <stack> b"\x10\x00" : b"\x01\x00" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b<= => . </k>
        <stack> b"\x10\x00" : b"\x10\x01" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b<= => . </k>
        <stack> b"\x10\x01" : b"\x10\x01" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b<= => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b>= 	4 	heavy_check_mark 	1
  claim <k> b>= => . </k>
        <stack> b"\x10\x00" : b"\x01\x00" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b>= => . </k>
        <stack> b"\x10\x00" : b"\x10\x01" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b>= => . </k>
        <stack> b"\x10\x01" : b"\x10\x01" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b>= => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b== 	4 	heavy_check_mark 	1
  claim <k> b== => . </k>
        <stack> b"abcd" : b"abcd" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b== => . </k>
        <stack> b"abcd" : b"abcde" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b== => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b!= 	4 	heavy_check_mark 	1
  claim <k> b!= => . </k>
        <stack> b"abcd" : b"abcd" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b!= => . </k>
        <stack> b"abcd" : b"abcde" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b!= => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b% 	4 	heavy_check_mark 	20
  claim <k> b% => . </k>
        <stack> b"\x02" : b"\x09" : XS => b"\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b% => panic(DIV_BY_ZERO) </k>
        <stack> b"\x00" : b"\x09" : _ </stack>

  claim <k> b% => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b| 	4 	heavy_check_mark 	6
  claim <k> b| => . </k>
        <stack> b"\x01\x01" : b"\x12" : XS => b"\x01\x13" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b| => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b& 	4 	heavy_check_mark 	6
  claim <k> b& => . </k>
        <stack> b"\x01\x01" : b"\x13" : XS => b"\x00\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b& => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b^ 	4 	heavy_check_mark 	6
  claim <k> b^ => . </k>
        <stack> b"\x01\x01" : b"\x10\x01" : XS => b"\x11\x00" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b^ => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>

// b~ 	4 	heavy_check_mark 	4
  claim <k> b~ => . </k>
        <stack> b"\x01\x01" : XS => b"\xfe\xfe" : XS </stack>

  claim <k> b~ => panic(ILL_TYPED_STACK) </k>
        <stack> 123 : _ </stack>

// bzero 	4 	heavy_check_mark 	1 
  claim <k> bzero => . </k>
        <stack> 7 : XS => b"\x00\x00\x00\x00\x00\x00\x00" : XS </stack>

endmodule
