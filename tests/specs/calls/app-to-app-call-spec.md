```k
module APP-TO-APP-CALL-SPEC
  imports VERIFICATION
```

```k

claim
  <kavm>

    <k> #initGlobals() ~> #evalTxGroup() => . </k>

    <returncode>   4                        => 0                                      </returncode>
    <returnstatus> "Failure - AVM is stuck" => "Success - transaction group accepted" </returnstatus>
    <paniccode>    0                        => 0                                      </paniccode>
    <panicstatus>  ""                       => ""                                     </panicstatus>

    <transactions>
      <transaction>
        <txID> APPL_TX_ID:String </txID>
        <txHeader>
          <sender> SENDER_ADDRESS:Bytes </sender>
          <txType> "appl" </txType>
          <typeEnum> @ appl </typeEnum>
          <groupID> GROUP_ID:String </groupID>
          <groupIdx> 1 </groupIdx>
          <firstValid> _:Int </firstValid>
          <lastValid> _:Int </lastValid>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> CALCULATOR_APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <applicationArgs> METHOD_SIG:Bytes Int2Bytes(ARG1:Int, BE, Unsigned) Int2Bytes(ARG2:Int, BE, Unsigned) </applicationArgs>
            ...
          </appCallTxFields>
        </txnTypeSpecificFields>
        <applyData>
          <txScratch> _ => ?_ </txScratch>
          <logData> .TValueList => ?_ </logData>
          <logSize> 0 => ?_ </logSize>
          ...
        </applyData>
        <txnExecutionContext> _ => ?_ </txnExecutionContext>
        <resume> false => true </resume>
      </transaction>
      (.Bag => ?_)
    </transactions>

    <avmExecution>
      <currentTx> _ => ?_ </currentTx>
      <txnDeque>
        <deque> ListItem(APPL_TX_ID) => ?_ </deque>
        <dequeIndexSet> SetItem(APPL_TX_ID) => ?_ </dequeIndexSet>
      </txnDeque>
      <currentTxnExecution>
         <globals>
           <groupSize>                 _ => ?_ </groupSize>
           <globalRound>               _ => ?_ </globalRound>
           <latestTimestamp>           _ => ?_ </latestTimestamp>
           <currentApplicationID>      _ => ?_ </currentApplicationID>
           <currentApplicationAddress> _ => ?_ </currentApplicationAddress>
           <creatorAddress>            _ => ?_ </creatorAddress>
         </globals>
         <teal>    _ => ?_  </teal>
         <effects> .List => ?_ </effects>
         <lastTxnGroupID> _ => ?_ </lastTxnGroupID>
      </currentTxnExecution>
      <innerTransactions> .List => ?_ </innerTransactions>
      <activeApps> .Set </activeApps>
      <touchedAccounts> .List </touchedAccounts>
    </avmExecution>

    <blockchain>
      <accountsMap>
        <account>
          <address> SENDER_ADDRESS:Bytes => ?_ </address>
          <balance> SENDER_BALANCE:Int => ?_ </balance>
          <minBalance> SENDER_MIN_BALANCE:Int </minBalance>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
        <account>
          <address> CREATOR_ADDRESS:Bytes => ?_ </address>
          <balance> _ => ?_ </balance>
          <minBalance> _ => ?_ </minBalance>
          <appsCreated>
            <app>
              <appID> CALCULATOR_APP_ID </appID>
              <approvalPgmSrc> (
txn NumAppArgs
int 0
==
bnz MAIN_L10
txna ApplicationArgs 0
method "add(uint64,uint64)uint64"
==
bnz MAIN_L9
txna ApplicationArgs 0
method "sub(uint64,uint64)uint64"
==
bnz MAIN_L8
txna ApplicationArgs 0
method "mul(uint64,uint64)uint64"
==
bnz MAIN_L7
txna ApplicationArgs 0
method "div(uint64,uint64)uint64"
==
bnz MAIN_L6
err
MAIN_L6:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
btoi
store 9
txna ApplicationArgs 2
btoi
store 10
load 9
load 10
callsub DIV_3
store 11
byte "\x15\x1f\x7c\x75"
load 11
itob
concat
log
int 1
return
MAIN_L7:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
btoi
store 6
txna ApplicationArgs 2
btoi
store 7
load 6
load 7
callsub MUL_2
store 8
byte "\x15\x1f\x7c\x75"
load 8
itob
concat
log
int 1
return
MAIN_L8:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
btoi
store 3
txna ApplicationArgs 2
btoi
store 4
load 3
load 4
callsub SUB_1
store 5
byte "\x15\x1f\x7c\x75"
load 5
itob
concat
log
int 1
return
MAIN_L9:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
btoi
store 0
txna ApplicationArgs 2
btoi
store 1
load 0
load 1
callsub ADD_0
store 2
byte "\x15\x1f\x7c\x75"
load 2
itob
concat
log
int 1
return
MAIN_L10:
txn OnCompletion
int NoOp
==
bnz MAIN_L12
err
MAIN_L12:
txn ApplicationID
int 0
==
assert
int 1
return

// add
ADD_0:
+
retsub

// sub
SUB_1:
-
retsub

// mul
MUL_2:
*
retsub

// div
DIV_3:
/
retsub
                ):TealInputPgm => ?_
              </approvalPgmSrc>
              <globalState>
                <globalNumInts>   0             </globalNumInts>
                <globalNumBytes>  0             </globalNumBytes>
                <globalBytes>     .Map             </globalBytes>
                <globalInts>      .Map             </globalInts>
              </globalState>
              <clearStatePgmSrc> (int 1 return):TealInputPgm => ?_ </clearStatePgmSrc>
              ...
            </app>
          </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
        <account>
          <address> APP_ADDRESS:Bytes </address>
          <balance> APP_BALANCE:Int => ?_ </balance>
          <minBalance> APP_MIN_BALANCE:Int </minBalance>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
      </accountsMap>
      <appCreator> .Map [CALCULATOR_APP_ID <- CREATOR_ADDRESS] </appCreator>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
      <nextTxnID> NEXT_TXN_ID => ?_ </nextTxnID>
      <nextGroupID> NEXT_GROUP_ID => ?_ </nextGroupID>
      ...
    </blockchain>

    <tealPrograms> _ </tealPrograms>

  </kavm>

  requires CALCULATOR_APP_ID >Int 0
   andBool APP_ADDRESS ==K getAppAddressBytes(CALCULATOR_APP_ID)
   andBool APP_BALANCE >=Int APP_MIN_BALANCE
   andBool CREATOR_ADDRESS =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K APP_ADDRESS
   andBool SENDER_ADDRESS  =/=K CREATOR_ADDRESS
   andBool SENDER_BALANCE >=Int SENDER_MIN_BALANCE

   andBool SENDER_MIN_BALANCE >=Int 0
   andBool APP_MIN_BALANCE    >=Int 0

   andBool METHOD_SIG ==K substrBytes(String2Bytes(Sha512_256raw("add(uint64,uint64)uint64")), 0, 4)

   andBool Int2String(NEXT_TXN_ID) =/=String APPL_TX_ID
   andBool Int2String(NEXT_GROUP_ID +Int 1) =/=String GROUP_ID

   andBool ARG1 +Int ARG2 <=Int MAX_UINT64

   andBool 0 ==K ADD_0
   andBool 1 ==K SUB_1
   andBool 2 ==K MUL_2
   andBool 3 ==K DIV_3
   andBool 4 ==K MAIN_L6
   andBool 5 ==K MAIN_L7
   andBool 6 ==K MAIN_L8
   andBool 7 ==K MAIN_L9
   andBool 8 ==K MAIN_L10
   andBool 9 ==K MAIN_L12

```

```k
endmodule
```
