```k
module OPCODES-V7-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> replace2 s </td><td> 7 </td><td> tested </td><td> 1  </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> replace2 2 => . </k>
        <stack> b"123" : b"abcdefgh" : XS => b"ab123fgh" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> replace2 3 => #panic(BYTES_OVERFLOW) </k>
        <stack> b"123" : b"12345" : _ </stack>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> replace3 </td><td> 7 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> replace3 => . </k>
        <stack> b"123" : 3 : b"abcdefgh" : XS => b"abc123gh" : XS </stack>
        <stacksize> 3 => 1 </stacksize>

  claim <k> replace3 => #panic(BYTES_OVERFLOW) </k>
        <stack> b"123" : 3 :  b"12345" : _ </stack>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> base64_decode e </td><td> 7 </td><td> not implemented </td><td> 1 + 1 per 16 bytes of A </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> json_ref r </td><td> 7 </td><td> not implemented </td><td> 25 + 2 per 7 bytes of A </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> ed25519verify_bare </td><td> 7 </td><td> not implemented </td><td> 1900 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> sha3_256 </td><td> 7 </td><td> not implemented </td><td> 130 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> vrf_verify s </td><td> 7 </td><td> not implemented </td><td> 5700 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> block f </td><td> 7 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

</tbody>
</table>

```k
endmodule
```
