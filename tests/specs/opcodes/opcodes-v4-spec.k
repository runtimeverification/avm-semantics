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
// retsub 	4 	heavy_check_mark 	1
// shl 	4 	heavy_check_mark 	1
// shr 	4 	heavy_check_mark 	1
// sqrt 	4 	heavy_check_mark 	4
// bitlen 	4 	heavy_check_mark 	1
// exp 	4 	heavy_check_mark 	1
// expw 	4 	heavy_check_mark 	1
// b+ 	4 	heavy_check_mark 	10
// b- 	4 	heavy_check_mark 	10
// b/ 	4 	heavy_check_mark 	20
// b* 	4 	heavy_check_mark 	20
// b< 	4 	heavy_check_mark 	1
// b> 	4 	heavy_check_mark 	1
// b<= 	4 	heavy_check_mark 	1
// b>= 	4 	heavy_check_mark 	1
// b== 	4 	heavy_check_mark 	1
// b!= 	4 	heavy_check_mark 	1
// b% 	4 	heavy_check_mark 	20
// b| 	4 	heavy_check_mark 	6
// b& 	4 	heavy_check_mark 	6
// b^ 	4 	heavy_check_mark 	6
// b~ 	4 	heavy_check_mark 	4
// bzero 	4 	heavy_check_mark 	1 

endmodule
