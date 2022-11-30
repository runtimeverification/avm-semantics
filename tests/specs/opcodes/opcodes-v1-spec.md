```k
module OPCODES-V1-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> err </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> err => panic(ERR_OPCODE) ...</k>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> sha256        </td><td> 1 </td><td> not implemented </td><td> 1   </td>
<td></td>

<!----------------------------------------------------------------------------->

<tr><td> keccak256     </td><td> 1 </td><td> not implemented </td><td> 130  </td>
<td></td>

<!----------------------------------------------------------------------------->

<tr><td> sha512_256    </td><td> 1 </td><td> not implemented </td><td> 45   </td>
<td></td>

<!----------------------------------------------------------------------------->

<tr><td> ed25519verify </td><td> 1 </td><td> not implemented </td><td> 1900 </td>
<td></td>

<!----------------------------------------------------------------------------->

<tr><td> + </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> + => . ...</k>
        <stack> 5 : 3 : XS => 8 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> + => panic(INT_OVERFLOW) ...</k>
        <stack> MAX_UINT64 : 3 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> - </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> - => . ...</k>
        <stack> 6 : 10 : XS => 4 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> - => panic(INT_UNDERFLOW) ...</k>
        <stack> 10 : 6 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> / </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> / => . ...</k>
        <stack> 5 : 30 : XS => 6 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> / => panic(DIV_BY_ZERO) ...</k>
        <stack> 0 : 30 : _</stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> * </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> * => . ...</k>
        <stack> 6 : 7 : XS => 42 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> * => panic(INT_OVERFLOW) ...</k>
        <stack> MAX_UINT64 : 2 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> < </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> < => . ...</k>
        <stack> 5 : 3 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> < => . ...</k>
        <stack> 3 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> < => . ...</k>
        <stack> 5 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> > </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> > => . ...</k>
        <stack> 5 : 3 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> > => . ...</k>
        <stack> 3 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> > => . ...</k>
        <stack> 5 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> <= </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> <= => . ...</k>
        <stack> 5 : 3 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> <= => . ...</k>
        <stack> 3 : 5 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> <= => . ...</k>
        <stack> 5 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> >= </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> >= => . ...</k>
        <stack> 5 : 3 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> >= => . ...</k>
        <stack> 3 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> >= => . ...</k>
        <stack> 5 : 5 : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> && </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>


<!----------------------------------------------------------------------------->

<tr><td> || </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> == </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> != </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> ! </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> ! => . ...</k>
        <stack> 1 : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> ! => . ...</k>
        <stack> 5 : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> ! => . ...</k>
        <stack> 0 : XS => 1 : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> len </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> len => . ...</k>
        <stack> b"123456" : XS => 6 : XS </stack>
        <stacksize> _ </stacksize>

  claim <k> len => . ...</k>
        <stack> b"" : XS => 0 : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> itob </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> itob => . ...</k>
        <stack> 6382179 : XS => b"\x00\x00\x00\x00\x00abc" : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> btoi </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> btoi => . ...</k>
        <stack> b"\x00\x00\x00\x00\x00abc" : XS => 6382179 : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> % </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> % => . ...</k>
        <stack> 3 : 5 : XS => 2 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> % => panic(DIV_BY_ZERO) ...</k>
        <stack> 0 : 5 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> | </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> | => . ...</k>
        <stack> 123 : 321 : XS => 379 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> & </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> & => . ...</k>
        <stack> 123 : 321 : XS => 65 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> ^ </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> ^ => . ...</k>
        <stack> 123 : 321 : XS => 314 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> ~ </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
// ~ 	1 	heavy_check_mark 	1
//  claim <k> ~ => . </k>
//        <stack> 123 : XS => 18446744073709551492 : XS </stack>
//        <stacksize> _ </stacksize>
  claim <k> ~ => panic(ILL_TYPED_STACK) </k>
        <stack> b"123" : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> mulw </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> mulw => . </k>
        <stack> 123456789012345 : 123456789012345 : XS => 15098910126093764401 : 826247639 : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intcblock </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intcblock 3 4 5 6 => . </k>
        <intcblock> _ =>
                   (0 |-> 4
                    1 |-> 5
                    2 |-> 6)
        </intcblock>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intc </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intc 1 => . </k>
        <stack> XS => 5 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
        </intcblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intc_0 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intc_0 => . </k>
        <stack> XS => 4 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intc_1 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intc_1 => . </k>
        <stack> XS => 5 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intc_2 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intc_2 => . </k>
        <stack> XS => 6 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> intc_3 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> intc_3 => . </k>
        <stack> XS => 7 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <intcblock> 0 |-> 4
                    1 |-> 5
                    2 |-> 6
                    3 |-> 7
        </intcblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytecblock </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytecblock 3 (1, "1") (1, "2") (1,"3") => . </k>
        <bytecblock> _ =>
                   (0 |-> "1"
                    1 |-> "2"
                    2 |-> "3")
        </bytecblock>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytec </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytec 1 => . </k>
        <stack> XS => "2" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
        </bytecblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytec_0 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytec_0 => . </k>
        <stack> XS => "1" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytec_1 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytec_1 => . </k>
        <stack> XS => "2" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytec_2 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytec_2 => . </k>
        <stack> XS => "3" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bytec_3 </td><td> 1 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bytec_3 => . </k>
        <stack> XS => "4" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <bytecblock> 0 |-> "1"
                    1 |-> "2"
                    2 |-> "3"
                    3 |-> "4"
        </bytecblock>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> arg n </td><td> 1 </td><td> not implemented </td><td> 1 </td>
<td></td></tr>

<!----------------------------------------------------------------------------->

<tr><td> arg_0 </td><td> 1 </td><td> not implemented </td><td> 1 </td>
<td></td></tr>

<!----------------------------------------------------------------------------->

<tr><td> arg_1 </td><td> 1 </td><td> not implemented </td><td> 1 </td>
<td></td></tr>

<!----------------------------------------------------------------------------->

<tr><td> arg_2 </td><td> 1 </td><td> not implemented </td><td> 1 </td>
<td></td></tr>

<!----------------------------------------------------------------------------->

<tr><td> arg_3 </td><td> 1 </td><td> not implemented </td><td> 1 </td>
<td></td></tr>

<!----------------------------------------------------------------------------->

<tr><td> txn f </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> txn Sender => . </k>
        <stack> XS => normalize(SENDER) : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transactions>
          <transaction>
            <txID> TX_ID </txID>
            <groupID> GROUP_ID:String </groupID>
            <groupIdx> GROUP_INDEX:Int </groupIdx>
            <sender> SENDER:Bytes </sender>
            <typeEnum> TYPE </typeEnum>
            ...
          </transaction>
          ...
        </transactions>
        <txnIndexMap>
          <txnIndexMapGroup>
            <txnIndexMapGroupKey> GROUP_ID:String </txnIndexMapGroupKey>
            <txnIndexMapGroupValues> .Map [GROUP_INDEX:Int <- TX_ID:String] </txnIndexMapGroupValues>
          </txnIndexMapGroup>
          ...
        </txnIndexMap>
    requires S <Int MAX_STACK_DEPTH
      andBool #isValidForTxnType(Sender, TYPE)
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> global f </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> global MinBalance => . </k>
        <stack> XS => 100000 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gtxn t f </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
   claim <k> gtxn GROUP_INDEX Sender => . </k>
         <stack> XS => normalize(SENDER) : XS </stack>
         <stacksize> S => S +Int 1 </stacksize>
         <currentTx> CURRENT_TX_ID </currentTx>
         <transactions>
           <transaction>
             <txID> CURRENT_TX_ID </txID>
             <groupID> GROUP_ID:String </groupID>
             <groupIdx> CURRENT_GROUP_INDEX:Int </groupIdx>
             ...
           </transaction>
           <transaction>
             <txID> TARGET_TX_ID </txID>
             <groupID> GROUP_ID:String </groupID>
             <groupIdx> GROUP_INDEX:Int </groupIdx>
             <sender> SENDER:Bytes </sender>
             <typeEnum> TYPE </typeEnum>
             ...
           </transaction>
           ...
         </transactions>
         <txnIndexMap>
           <txnIndexMapGroup>
             <txnIndexMapGroupKey> GROUP_ID:String </txnIndexMapGroupKey>
             <txnIndexMapGroupValues> .Map 
                                      [GROUP_INDEX:Int <- TARGET_TX_ID:String]
                                      [CURRENT_GROUP_INDEX <- CURRENT_TX_ID:String]
             </txnIndexMapGroupValues>
           </txnIndexMapGroup>
           ...
         </txnIndexMap>
     requires S <Int MAX_STACK_DEPTH
      andBool #isValidForTxnType(Sender, TYPE)
      andBool GROUP_INDEX =/=K CURRENT_GROUP_INDEX
      andBool CURRENT_TX_ID =/=K TARGET_TX_ID
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> load i </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> store i </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> store 1 => . </k>
        <stack> VALUE : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <scratch> (2 |-> _) (1 |-> (_ => VALUE)) (4 |-> _) </scratch>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> pop </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> pop => . </k>
        <stack> _ : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> dup </td><td> 1 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> dup => . </k>
        <stack> VAL : XS => VAL : VAL : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000
```
</details>
</td></tr>

</tbody>
</table>


```k
endmodule
```
