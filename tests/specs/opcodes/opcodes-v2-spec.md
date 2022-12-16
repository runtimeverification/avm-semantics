```k
module OPCODES-V2-SPEC
  imports VERIFICATION
```

<table>

<thead>
<tr><th> Opcode </th><th> AVM version </th><th> Status </th><th> Cost </th><th> K Claims </th></tr>
</thead>

<tbody>

<!----------------------------------------------------------------------------->

<tr><td> addw </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> addw => . </k>
        <stack> 18446744073709551615 : 5 : XS => 4 : 1 : XS </stack>
        <stacksize> _ </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> txna f i </td><td> 2 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> txna Applications 2 => . </k>
        <stack> XS => APPL : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <groupID> "0" </groupID>
          <groupIdx> 0 </groupIdx>
          <typeEnum> @ appl </typeEnum>
          <foreignApps> 3 APPL:Int 7 </foreignApps>
          ...
        </transaction>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (0 |-> TX_ID) </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> gtxna t f i </td><td> 2 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> gtxna 0 ApplicationArgs 0 => . </k>
        <stack> XS => b"123" : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> "2a" </currentTx>
        <transactions>
          <transaction>
            <txID> "0" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 0 </groupIdx>
            <applicationArgs> b"123" </applicationArgs>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
          <transaction>
            <txID> "2a" </txID>
            <groupID> "0" </groupID>
            <groupIdx> 2 </groupIdx>
            <typeEnum> @ appl </typeEnum>
            ...
          </transaction>
        </transactions>
        <txnIndexMapGroup>
          <txnIndexMapGroupKey> "0" </txnIndexMapGroupKey>
          <txnIndexMapGroupValues> (2 |-> "2a") (0 |-> "0") </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> concat </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> concat => . </k>
        <stack> b"def" : b"abc" : XS => b"abcdef" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> concat => #panic(BYTES_OVERFLOW) </k>
        <stack> B2 : B1 : _ </stack>
    requires lengthBytes(B1) +Int lengthBytes(B2) >Int 4096
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> substring s e </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> substring 3 8 => . </k>
        <stack> (b"0123456789" => b"34567") : _ </stack>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> substring3 </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> substring3 => . </k>
        <stack> (b"0123456789" : 3 : 8 : XS) => (b"34567" : XS) </stack>
        <stacksize> S => S -Int 2 </stacksize>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> dup2 </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> dup2 => . </k>
        <stack> (3 : 4 : XS) => (3 : 4 : 3 : 4 : XS) </stack>
        <stacksize> S => S +Int 2 </stacksize>
    requires S <Int 1000 -Int 2
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> balance </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> balance => . </k>
        <stack> (normalize(ADDR) : XS) => (12345 : XS) </stack>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> ADDR </sender>
          ...
        </transaction>
        <account>
          <address> ADDR:Bytes </address>
          <balance> 12345 </balance>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_opted_in </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_opted_in => . </k>
        <stack> (B:Int : normalize(A:Bytes) : XS) => 1 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          <foreignApps> B _ </foreignApps>
          ...
        </transaction>
        <account>
          <address> A </address>
          <appsOptedIn>
            <optInApp>
              <optInAppID> B </optInAppID>
              ...
            </optInApp>
            ...
          </appsOptedIn>
          ...
        </account>

  claim <k> app_opted_in => . </k>
        <stack> (B:Int : normalize(A:Bytes) : XS) => 0 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          <foreignApps> B _ </foreignApps>
          ...
        </transaction>
        <account>
          <address> A </address>
          <appsOptedIn>
            <optInApp>
              <optInAppID> B' </optInAppID>
              ...
            </optInApp>
          </appsOptedIn>
          ...
        </account>
      requires B =/=K B'
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_local_get </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_local_get => . </k>
        <stack> (B:Bytes : normalize(A:Bytes) : XS) => 123 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          ...
        </transaction>
        <currentApplicationID> APP_ID </currentApplicationID>
        <account>
          <address> A </address>
          <appsOptedIn>
            <optInApp>
              <optInAppID> APP_ID </optInAppID>
              <localInts> B |-> 123 ...</localInts>
              ...
            </optInApp>
            ...
          </appsOptedIn>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_local_get_ex </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_local_get_ex => . </k>
        <stack> (C:Bytes : B:Int : normalize(A:Bytes) : XS) => 1 : 123 : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          <foreignApps> B _ </foreignApps>
          ...
        </transaction>
        <account>
          <address> A </address>
          <appsOptedIn>
            <optInApp>
              <optInAppID> B </optInAppID>
              <localInts> C |-> 123 ...</localInts>
              ...
            </optInApp>
            ...
          </appsOptedIn>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_global_get </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_global_get => . </k>
        <stack> (A:Bytes : XS) => (123 : XS) </stack>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          ...
        </transaction>
        <currentApplicationID> APP_ID </currentApplicationID>
        <account>
          <address> ADDR:Bytes </address>
          <appsCreated>
            <app>
              <appID> APP_ID </appID>
              <globalInts> .Map [ A <- 123 ] </globalInts>
              <globalBytes> .Map </globalBytes>
              ...
            </app>
            ...
          </appsCreated>
          ...
        </account>
        <appCreator> .Map [ APP_ID <- ADDR ] </appCreator>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_global_get_ex </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_global_get_ex => . </k>
        <stack> (B:Bytes : A:Int : XS) => (1 : 123 : XS) </stack>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <foreignApps> A _ </foreignApps>
          ...
        </transaction>
        <account>
          <address> ADDR:Bytes </address>
          <appsCreated>
            <app>
              <appID> A </appID>
              <globalInts> .Map [ B <- 123 ] </globalInts>
              <globalBytes> .Map </globalBytes>
              ...
            </app>
            ...
          </appsCreated>
          ...
        </account>
        <appCreator> .Map [ A <- ADDR ] </appCreator>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_local_put </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_local_put => . </k>
        <stack> (123 : b"key" : normalize(A:Bytes) : XS) => XS </stack>
        <stacksize> S => S -Int 3 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          ...
        </transaction>
        <currentApplicationID> APP_ID </currentApplicationID>
        <account>
          <address> A </address>
          <appsCreated>
            <app>
              <appID> APP_ID </appID>
              <localNumInts> 1 </localNumInts>
              ...
            </app>
            ...
          </appsCreated>
          <appsOptedIn>
            <optInApp>
              <optInAppID> APP_ID </optInAppID>
              <localInts> (.Map => (b"key" |-> 123)) </localInts>
              <localBytes> .Map </localBytes>
              ...
            </optInApp>
            ...
          </appsOptedIn>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_global_put </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_global_put => . </k>
        <stack> (123 : b"key" : XS) => XS </stack>
        <stacksize> S => S -Int 2 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> A </sender>
          ...
        </transaction>
        <currentApplicationID> APP_ID </currentApplicationID>
        <accountsMap>
          <account>
            <address> A </address>
            <appsCreated>
              <app>
                <appID> APP_ID </appID>
                <globalNumInts> 1 </globalNumInts>
                <globalInts> (.Map => (b"key" |-> 123)) </globalInts>
                <globalBytes> .Map </globalBytes>
                ...
              </app>
              ...
            </appsCreated>
            ...
          </account>
        </accountsMap>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_local_del </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_local_del => . </k>
        <stack> (b"key" : ADDR:Bytes : XS) => XS </stack>
        <stacksize> S => S -Int 2 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <sender> ADDR </sender>
          ...
        </transaction>
        <currentApplicationID> APP_ID </currentApplicationID>
        <accountsMap>
          <account>
            <address> ADDR </address>
            <appsOptedIn>
              <optInApp>
                <optInAppID> APP_ID </optInAppID>
                <localInts> (b"key" |-> 123) => .Map </localInts>
                <localBytes> .Map </localBytes>
                ...
              </optInApp>
              ...
            </appsOptedIn>
            ...
          </account>
        </accountsMap>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> app_global_del </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> app_global_del => . </k>
        <stack> (b"key" : XS) => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <currentApplicationID> APP_ID </currentApplicationID>
        <accountsMap>
          <account>
            <address> _ </address>
            <appsCreated>
              <app>
                <appID> APP_ID </appID>
                <globalInts> (b"key" |-> 123) => .Map </globalInts>
                <globalBytes> .Map </globalBytes>
                ...
              </app>
              ...
            </appsCreated>
            ...
          </account>
        </accountsMap>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> asset_holding_get i </td><td> 2 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> asset_holding_get AssetBalance => . </k>
        <stack> ASSET:Int : normalize(ADDR:Bytes) : XS => 1 : 12345 : XS </stack>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <foreignAssets> ASSET _ </foreignAssets>
          <sender> ADDR </sender>
          ...
        </transaction>
        <account>
          <address> ADDR </address>
          <optInAsset>
            <optInAssetID> ASSET </optInAssetID>
            <optInAssetBalance> 12345 </optInAssetBalance>
            ...
          </optInAsset>
          ...
        </account>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> asset_params_get i </td><td> 2 </td><td> tested (not every field) </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> asset_params_get AssetTotal => . </k>
        <stack> ASSET:Int : XS => 1 : 12345 : XS </stack>
        <stacksize> S => S +Int 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        <transaction>
          <txID> TX_ID </txID>
          <typeEnum> @ appl </typeEnum>
          <foreignAssets> ASSET _ </foreignAssets>
          ...
        </transaction>
        <asset>
          <assetID> ASSET </assetID>
          <assetTotal> 12345 </assetTotal>
          ...
        </asset>
    requires S <Int 1000
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> return </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> return ~> #incrementPC() ~> #fetchOpcode() => . </k>
        <stack> (1 : 2 : .TStack) => (1 : .TStack) </stack>
        <stacksize> 2 => 1 </stacksize>
        <currentTx> TX_ID </currentTx>
        (<transactions>
          <transaction>
            <txID> TX_ID </txID>
            <typeEnum> @ appl </typeEnum> 
            <txType> "appl" </txType>
            ...
          </transaction>
        </transactions> => <transactions> ?_ </transactions>)
        <currentApplicationID> APP_ID:Int </currentApplicationID>
        <activeApps> (SetItem(APP_ID) .Set) => .Set </activeApps>

```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bnz target </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bnz LABEL => . </k>
        <stack> 1 : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <jumped> _ => true </jumped>
        <pc> _ => 23 </pc>
        <labels> .Map [LABEL <- 23] </labels>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> bz target </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> bz LABEL => . </k>
        <stack> 0 : XS => XS </stack>
        <stacksize> S => S -Int 1 </stacksize>
        <jumped> _ => true </jumped>
        <pc> _ => 23 </pc>
        <labels> .Map [LABEL <- 23] </labels>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

<tr><td> b target </td><td> 2 </td><td> tested </td><td> 1 </td>
<td><details>
<summary>K claims</summary>

```k
  claim <k> b LABEL => . </k>
        <jumped> _ => true </jumped>
        <pc> _ => 23 </pc>
        <labels> .Map [LABEL <- 23] </labels>
```
</details>
</td></tr>

<!----------------------------------------------------------------------------->

</tbody>
</table>

```k
endmodule
```
