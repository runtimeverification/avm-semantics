module OPCODES-V2-SPEC
  imports VERIFICATION

// addw 	2 	heavy_check_mark 	1
  claim <k> addw => . </k>
        <stack> 18446744073709551615 : 5 : XS => 4 : 1 : XS </stack>
        <stacksize> _ </stacksize>

// txna f i 	2 	heavy_check_mark 	1
  claim <k> txna Applications 1 => . </k>
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
          <txnIndexMapGroupValues> (0 |-> TX_ID) ... </txnIndexMapGroupValues>
        </txnIndexMapGroup>
    requires S <Int 1000

// gtxna t f i 	2 	heavy_check_mark 	1

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

// concat 	2 	heavy_check_mark 	1
  claim <k> concat => . </k>
        <stack> b"def" : b"abc" : XS => b"abcdef" : XS </stack>
        <stacksize> S => S -Int 1 </stacksize>

  claim <k> concat => panic(BYTES_OVERFLOW) </k>
        <stack> B2 : B1 : _ </stack>
    requires lengthBytes(B1) +Int lengthBytes(B2) >Int 4096

// substring s e 	2 	heavy_check_mark 	1
  claim <k> substring 3 8 => . </k>
        <stack> (b"0123456789" => b"34567") : _ </stack>
  
// substring3 	2 	heavy_check_mark 	1
  claim <k> substring3 => . </k>
        <stack> (b"0123456789" : 3 : 8 : XS) => (b"34567" : XS) </stack>
        <stacksize> S => S -Int 2 </stacksize>
  
// dup2 	2 	heavy_check_mark 	1
  claim <k> dup2 => . </k>
        <stack> (3 : 4 : XS) => (3 : 4 : 3 : 4 : XS) </stack>
        <stacksize> S => S +Int 2 </stacksize>
    requires S <Int 1000 -Int 2

// balance 	2 	heavy_check_mark 	1
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

// app_opted_in 	2 	heavy_check_mark 	1
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

// app_local_get 	2 	heavy_check_mark 	1
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

// app_local_get_ex 	2 	heavy_check_mark 	1
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

// app_global_get 	2 	heavy_check_mark 	1
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
          <address> _ </address>
          <appsCreated>
            <app>
              <appID> APP_ID </appID>
              <globalInts> A |-> 123 </globalInts>
              ...
            </app>
            ...
          </appsCreated>
          ...
        </account>

// app_global_get_ex 	2 	heavy_check_mark 	1
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
          <address> _ </address>
          <appsCreated>
            <app>
              <appID> A </appID>
              <globalInts> B |-> 123 </globalInts>
              ...
            </app>
            ...
          </appsCreated>
          ...
        </account>

// app_local_put 	2 	heavy_check_mark 	1
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

// app_global_put 	2 	heavy_check_mark 	1
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

// app_local_del 	2 	heavy_check_mark 	1
// app_global_del 	2 	heavy_check_mark 	1
// asset_holding_get i 	2 	heavy_check_mark 	1
// asset_params_get i 	2 	heavy_check_mark 	1
// return 	2 	heavy_check_mark 	1
// bnz target 	2 (4) 	heavy_check_mark 	1
// bz target 	2 (4) 	heavy_check_mark 	1
// b target 	2 (4) 	heavy_check_mark 	1

endmodule
