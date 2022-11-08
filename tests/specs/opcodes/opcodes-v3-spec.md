```k
module OPCODES-V3-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> gtxns f </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> gtxns Sender => . </k>
        <stack> 1 : XS => normalize(ADDR) : XS </stack>
        <stacksize> S </stacksize>
        <currentTx> "1" </currentTx>
        <transaction>
          <txID> "1" </txID>
          <groupID> "0" </groupID>
          <groupIdx> 0 </groupIdx>
          ...
        </transaction>
        <transaction>
          <txID> "2" </txID>
          <typeEnum> @ appl </typeEnum>
          <groupID> "0" </groupID>
          <groupIdx> 1 </groupIdx>
          <sender> ADDR:Bytes </sender>
          ...
        </transaction>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (0 |-> "1") (1 |-> "2") ... </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gtxnsa f i </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> gtxnsa ApplicationArgs 1 => . </k>
        <stack> 1 : XS => 2 : XS </stack>
        <stacksize> S </stacksize>
        <currentTx> "1" </currentTx>
        <transaction>
          <txID> "1" </txID>
          <groupID> "0" </groupID>
          <groupIdx> 0 </groupIdx>
          ...
        </transaction>
        <transaction>
          <txID> "2" </txID>
          <typeEnum> @ appl </typeEnum>
          <groupID> "0" </groupID>
          <groupIdx> 1 </groupIdx>
          <applicationArgs> 1 2 3 </applicationArgs>
          ...
        </transaction>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (0 |-> "1") (1 |-> "2") ... </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> assert </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> assert => . </k>
        <stack> 0 : _ </stack>
        <returncode> 4 => 3 </returncode>
        <currentApplicationID> APP_ID </currentApplicationID>
        <activeApps> SetItem(APP_ID) => .Set </activeApps>
        <returnstatus> _ => "Failure - panic: assertion violation" </returnstatus>
        <paniccode> _ => 24 </paniccode>
        <panicstatus> _ => "assertion violation" </panicstatus>

  claim <k> assert => . </k>
        <stack> N : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <returncode> _ </returncode>
        <returnstatus> _ </returnstatus>
    requires N >=Int 1
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> dig n </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> dig 3 => . </k>
        <stack> 4 : 5 : 6 : 7 : 8 : XS => 7 : 4 : 5 : 6 : 7: 8 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000 andBool S >=Int 6
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> swap </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> swap => . </k>
        <stack> 3 : 5 : XS => 5 : 3 : XS </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> select </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> select => . </k>
        <stack> 1 : A : _ : XS => A : XS </stack>
        <stacksize> S => S -Int 2 </stacksize>

  claim <k> select => . </k>
        <stack> 0 : _ : B : XS => B : XS </stack>
        <stacksize> S => S -Int 2 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> getbit </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> getbit => . </k>
        <stack> 0 : b"\x0f" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> getbit => . </k>
        <stack> 3 : b"\x0f" : XS => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> getbit => . </k>
        <stack> 5 : b"\x0f" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> getbit => . </k>
        <stack> 7 : b"\x0f" : XS => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> setbit </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> setbit => . </k>
        <stack> 1 : 0 : b"\x0f" : XS => b"\x8f" : XS </stack>
        <stacksize> S => S -Int 2 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> getbyte </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> getbyte => . </k>
        <stack> 3 : b"abc\x0fd" : XS => 15 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> setbyte </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> setbyte => . </k>
        <stack> 4 : 3 : b"abc\x0fd" : XS => b"abc\x04d" : XS </stack>
        <stacksize> S => S -Int 2 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> min_balance </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> min_balance => . </k>
        <stack> normalize(ADDR:Bytes) : XS => MIN_BAL : XS </stack>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <sender> ADDR </sender>
          <typeEnum> @ appl </typeEnum>
          ...
        </transaction>
        <account>
          <address> ADDR </address>
          <minBalance> MIN_BAL </minBalance>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> pushbytes bytes </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> pushbytes "123" => . </k>
        <stack> XS => b"123" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> pushint uint </td><td> 3 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> pushint 321 => . </k>
        <stack> XS => 321 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

</tbody>
</table>

```k
endmodule
```
