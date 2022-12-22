```k
module OPCODES-V8-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> bury n </td><td> 8 </td><td> tested </td><td> 1  </td>
<td><details>
<summary>K claims</summary>

```k
claim <k> bury 3 => . </k>
      <stack> 1 : 2 : 3 : 4 : 5 : 6 : .TStack => 2 : 3 : 1 : 5 : 6 : .TStack </stack>
      <stacksize> 6 => 5 </stacksize>

claim <k> bury 6 => #panic(STACK_UNDERFLOW) </k>
      <stack> 1 : 2 : 3 : 4 : 5 : 6 : .TStack </stack>
      <stacksize> 6 </stacksize>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> popn n </td><td> 8 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
claim <k> popn 3 => . </k>
      <stack> 1 : 2 : 3 : 4 : 5 : 6 : .TStack => 4 : 5 : 6 : .TStack </stack>
      <stacksize> 6 => 3 </stacksize>

claim <k> popn 7 => #panic(STACK_UNDERFLOW) </k>
      <stack> 1 : 2 : 3 : 4 : 5 : 6 : .TStack </stack>
      <stacksize> 6 </stacksize>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> dupn n </td><td> 8 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
claim <k> dupn 3 => . </k>
      <stack> 1 : 2 : .TStack => 1 : 1 : 1 : 1 : 2 : .TStack </stack>
      <stacksize> 2 => 5 </stacksize>

claim <k> dupn 7 => #panic(STACK_OVERFLOW) </k>
      <stack> 1 : _ => ?_ </stack>
      <stacksize> MAX_STACK_DEPTH -Int 6 => ?_ </stacksize>
```

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> proto a r </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> frame_dig i </td><td> 8 </td><td> implemented, not tested  </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> frame_bury i </td><td> 8 </td><td> implemented, not tested  </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> switch target </td><td> 8 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> match target </td><td> 8 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> pushbytess b </td><td> 8 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> pushints i </td><td> 8 </td><td> not implemented </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_create </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_extract </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_replace </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_del </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_len </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_get </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> box_put </td><td> 8 </td><td> implemented, not tested </td><td> 1 </td>
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
