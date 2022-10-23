```k
module OPCODES-V4-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> divmodw </td><td> 4 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
//   claim <k> divmodw => . </k>
//         <stack> 3 : 3 : 9 : 6 : XS => 3 : 2 : 0 : 0 : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gload t i </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gloads i </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gaid i </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gaids </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> callsub target </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> callsub LABEL => . </k>
        <callStack> (.List => ListItem(CURRENT_PC +Int 1)) CS </callStack>
        <pc> CURRENT_PC:Int => JUMP_PC </pc>
        <labels> .Map[LABEL <- JUMP_PC] </labels>
        <jumped> _ => true </jumped>
    requires size(CS) <Int MAX_CALLSTACK_DEPTH
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> retsub </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> retsub => . </k>
        <callStack> (ListItem(RET_PC) => .List) _ </callStack>
        <pc> _ => RET_PC </pc>
        <jumped> _ => true </jumped>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> shl </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> shl => . </k>
        <stack> 5 : 1 : XS => 32 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> shl => . </k>
        <stack> 1 : (2 ^Int 63) : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> shr </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> shr => . </k>
        <stack> 5 : 64 : XS => 2 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> shr => . </k>
        <stack> 3 : 2 : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> sqrt </td><td> 4 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
//   claim <k> sqrt => . </k>
//         <stack> 15 : XS => 3 : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bitlen </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bitlen => . </k>
        <stack> 8 : XS => 4 : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bitlen </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bitlen => . </k>
        <stack> 8 : XS => 4 : XS </stack>

  claim <k> bitlen => . </k>
        <stack> 10 : XS => 4 : XS </stack>

  claim <k> bitlen => . </k>
        <stack> b"\x10" : XS => 5 : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> exp </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> exp => . </k>
        <stack> 5 : 3 : XS => 243 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> exp => panic(INVALID_ARGUMENT) </k>
        <stack> 0 : 0 : _ </stack>

  claim <k> exp => panic(INT_OVERFLOW) </k>
        <stack> 100 : 2 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> expw </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> expw => . </k>
        <stack> 5 : 3 : XS => 243 : 0 : XS </stack>

  claim <k> expw => . </k>
        <stack> 64 : 2 : XS => 0 : 1 : XS </stack>

  claim <k> expw => panic(INVALID_ARGUMENT) </k>
        <stack> 0 : 0 : _ </stack>

  claim <k> expw => panic(INT_OVERFLOW) </k>
        <stack> 150 : 2 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b+ </td><td> 4 </td><td> tested </td><td> 10 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b- </td><td> 4 </td><td> tested </td><td> 10 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b- => . </k>
        <stack> b"\x03" : b"\x04" : XS => b"\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b- => panic(INT_UNDERFLOW) </k>
        <stack> b"\x07" : b"\x04" : _ </stack>

  claim <k> b- => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b/ </td><td> 4 </td><td> tested </td><td> 20 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b/ => . </k>
        <stack> b"\x02" : b"\x08" : XS => b"\x04" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b/ => panic(DIV_BY_ZERO) </k>
        <stack> b"\x00" : b"\x04" : _ </stack>

  claim <k> b/ => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b* </td><td> 4 </td><td> tested </td><td> 20 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b< </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b> </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b<= </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b>= </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
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
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b== </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b== => . </k>
        <stack> b"abcd" : b"abcd" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b== => . </k>
        <stack> b"abcd" : b"abcde" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b== => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b!= </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b!= => . </k>
        <stack> b"abcd" : b"abcd" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b!= => . </k>
        <stack> b"abcd" : b"abcde" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b!= => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b% </td><td> 4 </td><td> tested </td><td> 20 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b% => . </k>
        <stack> b"\x02" : b"\x09" : XS => b"\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b% => panic(DIV_BY_ZERO) </k>
        <stack> b"\x00" : b"\x09" : _ </stack>

  claim <k> b% => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b| </td><td> 4 </td><td> tested </td><td> 6 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b| => . </k>
        <stack> b"\x01\x01" : b"\x12" : XS => b"\x01\x13" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b| => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b& </td><td> 4 </td><td> tested </td><td> 6 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b& => . </k>
        <stack> b"\x01\x01" : b"\x13" : XS => b"\x00\x01" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b& => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b^ </td><td> 4 </td><td> tested </td><td> 6 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b^ => . </k>
        <stack> b"\x01\x01" : b"\x10\x01" : XS => b"\x11\x00" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> b^ => panic(ILL_TYPED_STACK) </k>
        <stack> b"1" : 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b~ </td><td> 4 </td><td> tested </td><td> 4 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b~ => . </k>
        <stack> b"\x01\x01" : XS => b"\xfe\xfe" : XS </stack>

  claim <k> b~ => panic(ILL_TYPED_STACK) </k>
        <stack> 123 : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bzero </td><td> 4 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bzero => . </k>
        <stack> 7 : XS => b"\x00\x00\x00\x00\x00\x00\x00" : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

</tbody>
</table>

```k
endmodule
```
