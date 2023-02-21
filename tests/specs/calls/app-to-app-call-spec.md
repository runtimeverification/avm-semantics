```k
module APP-TO-APP-CALL-SPEC
  imports VERIFICATION
```

```k

claim [main]:
  <kavm>

    <k> #initGlobals() ~> #evalTxGroup() => . </k>

    <returncode>   4 => 0   </returncode>
    <returnstatus> _ => ?_ </returnstatus>

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
            <applicationID> CALL_CALCULATOR_APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <applicationArgs>
              METHOD_SIG:Bytes
              b"\x01"
              Int2Bytes(ARG1:Int, BE, Unsigned)
              Int2Bytes(ARG2:Int, BE, Unsigned) 
            </applicationArgs>
            <foreignApps> CALCULATOR_APP_ID </foreignApps>
            ...
          </appCallTxFields>
        </txnTypeSpecificFields>
        <applyData>
          <txScratch> _ => ?_ </txScratch>
          <logData> .TValueList => b"\x15\x1f\x7c\x75" +Bytes padLeftBytes(Int2Bytes(ARG1 +Int ARG2, BE, Unsigned), 8, 0) </logData>
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
         <teal>
           <pc> 0 => ?_ </pc>
           <program> .Map  => ?_ </program>
           <mode> undefined  => ?_ </mode>
           <version> 1  => ?_ </version>
           <stack> .TStack  => ?_ </stack>
           <stacksize> 0  => ?_ </stacksize>
           <jumped> false  => ?_ </jumped>
           <labels> .Map  => ?_ </labels>
           <callStack> .List  => ?_ </callStack>
           <scratch> .Map  => ?_ </scratch>
           <intcblock> .Map  => ?_ </intcblock>
           <bytecblock> .Map  => ?_ </bytecblock>
         </teal>
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
              <appID> CALL_CALCULATOR_APP_ID </appID>
              <approvalPgmSrc> (
#pragma version 6
txn NumAppArgs
int 0
==
bnz main_l10
txna ApplicationArgs 0
method "add(application,uint64,uint64)uint64"
==
bnz main_l9
txna ApplicationArgs 0
method "sub(application,uint64,uint64)uint64"
==
bnz main_l8
txna ApplicationArgs 0
method "mul(application,uint64,uint64)uint64"
==
bnz main_l7
txna ApplicationArgs 0
method "div(application,uint64,uint64)uint64"
==
bnz main_l6
err
main_l6:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
int 0
getbyte
store 21
txna ApplicationArgs 2
btoi
store 22
txna ApplicationArgs 3
btoi
store 23
load 21
load 22
load 23
callsub div_3
store 24
byte "\x15\x1f\x7c\x75"
load 24
itob
concat
log
int 1
return
main_l7:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
int 0
getbyte
store 14
txna ApplicationArgs 2
btoi
store 15
txna ApplicationArgs 3
btoi
store 16
load 14
load 15
load 16
callsub mul_2
store 17
byte "\x15\x1f\x7c\x75"
load 17
itob
concat
log
int 1
return
main_l8:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
int 0
getbyte
store 7
txna ApplicationArgs 2
btoi
store 8
txna ApplicationArgs 3
btoi
store 9
load 7
load 8
load 9
callsub sub_1
store 10
byte "\x15\x1f\x7c\x75"
load 10
itob
concat
log
int 1
return
main_l9:
txn OnCompletion
int NoOp
==
txn ApplicationID
int 0
!=
&&
assert
txna ApplicationArgs 1
int 0
getbyte
store 0
txna ApplicationArgs 2
btoi
store 1
txna ApplicationArgs 3
btoi
store 2
load 0
load 1
load 2
callsub add_0
store 3
byte "\x15\x1f\x7c\x75"
load 3
itob
concat
log
int 1
return
main_l10:
txn OnCompletion
int NoOp
==
bnz main_l12
err
main_l12:
txn ApplicationID
int 0
==
assert
int 1
return

// add
add_0:
store 6
store 5
store 4
itxn_begin
int appl
itxn_field TypeEnum
load 4
txnas Applications
itxn_field ApplicationID
method "add(uint64,uint64)uint64"
itxn_field ApplicationArgs
load 5
itob
itxn_field ApplicationArgs
load 6
itob
itxn_field ApplicationArgs
itxn_submit
itxn LastLog
extract 4 8
btoi
retsub

// sub
sub_1:
store 13
store 12
store 11
itxn_begin
int appl
itxn_field TypeEnum
load 11
txnas Applications
itxn_field ApplicationID
method "sub(uint64,uint64)uint64"
itxn_field ApplicationArgs
load 12
itob
itxn_field ApplicationArgs
load 13
itob
itxn_field ApplicationArgs
itxn_submit
itxn LastLog
extract 4 8
btoi
retsub

// mul
mul_2:
store 20
store 19
store 18
itxn_begin
int appl
itxn_field TypeEnum
load 18
txnas Applications
itxn_field ApplicationID
method "mul(uint64,uint64)uint64"
itxn_field ApplicationArgs
load 19
itob
itxn_field ApplicationArgs
load 20
itob
itxn_field ApplicationArgs
itxn_submit
itxn LastLog
extract 4 8
btoi
retsub

// div
div_3:
store 27
store 26
store 25
itxn_begin
int appl
itxn_field TypeEnum
load 25
txnas Applications
itxn_field ApplicationID
method "div(uint64,uint64)uint64"
itxn_field ApplicationArgs
load 26
itob
itxn_field ApplicationArgs
load 27
itob
itxn_field ApplicationArgs
itxn_submit
itxn LastLog
extract 4 8
btoi
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
            <app>
              <appID> CALCULATOR_APP_ID </appID>
              <approvalPgmSrc> (
txn NumAppArgs
int 0
==
bnz main_l10
txna ApplicationArgs 0
method "add(uint64,uint64)uint64"
==
bnz main_l9
txna ApplicationArgs 0
method "sub(uint64,uint64)uint64"
==
bnz main_l8
txna ApplicationArgs 0
method "mul(uint64,uint64)uint64"
==
bnz main_l7
txna ApplicationArgs 0
method "div(uint64,uint64)uint64"
==
bnz main_l6
err
main_l6:
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
callsub div_3
store 11
byte "\x15\x1f\x7c\x75"
load 11
itob
concat
log
int 1
return
main_l7:
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
callsub mul_2
store 8
byte "\x15\x1f\x7c\x75"
load 8
itob
concat
log
int 1
return
main_l8:
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
callsub sub_1
store 5
byte "\x15\x1f\x7c\x75"
load 5
itob
concat
log
int 1
return
main_l9:
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
callsub add_0
store 2
byte "\x15\x1f\x7c\x75"
load 2
itob
concat
log
int 1
return
main_l10:
txn OnCompletion
int NoOp
==
bnz main_l12
err
main_l12:
txn ApplicationID
int 0
==
assert
int 1
return

// add
add_0:
+
retsub

// sub
sub_1:
-
retsub

// mul
mul_2:
*
retsub

// div
div_3:
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
          <address> CALCULATOR_APP_ADDRESS </address>
          <balance> APP_BALANCE:Int => ?_ </balance>
          <minBalance> APP_MIN_BALANCE:Int </minBalance>
          <appsCreated> .Bag </appsCreated>
          <appsOptedIn> .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes> .Bag </boxes>
          ...
        </account>
        <account>
          <address> CALL_CALCULATOR_APP_ADDRESS </address>
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
      <appCreator> .Map [CALCULATOR_APP_ID <- CREATOR_ADDRESS] [CALL_CALCULATOR_APP_ID <- CREATOR_ADDRESS] </appCreator>
      <txnIndexMap> .Bag => ?_ </txnIndexMap>
      <nextTxnID> 1 => ?_ </nextTxnID>
      <nextGroupID> 1 => ?_ </nextGroupID>
      ...
    </blockchain>

    <tealPrograms> _ </tealPrograms>

  </kavm>

  requires CALCULATOR_APP_ID ==Int 1
   andBool CALL_CALCULATOR_APP_ID ==Int 2


   andBool CALCULATOR_APP_ADDRESS ==K getAppAddressBytes(CALCULATOR_APP_ID)
   andBool CALL_CALCULATOR_APP_ADDRESS ==K getAppAddressBytes(CALL_CALCULATOR_APP_ID)

   andBool APP_BALANCE >=Int APP_MIN_BALANCE

  // Addresses are unique
   andBool CREATOR_ADDRESS ==K padLeftBytes(b"1", 32, 0)
   andBool SENDER_ADDRESS ==K padLeftBytes(b"2", 32, 0)

   andBool SENDER_BALANCE >=Int SENDER_MIN_BALANCE

   andBool SENDER_MIN_BALANCE >=Int 0
   andBool APP_MIN_BALANCE    >=Int 0

   andBool METHOD_SIG ==K methodSelector("add(application,uint64,uint64)uint64")

   andBool APPL_TX_ID ==String "0"
   andBool GROUP_ID ==String "0"

   andBool ARG1 +Int ARG2 <=Int MAX_UINT64
   
  // Input values are in the correct range according to their size
   andBool ARG1 <=Int MAX_UINT64
   andBool ARG2 <=Int MAX_UINT64
   andBool ARG1 >Int 0
   andBool ARG2 >Int 0

```

```k
endmodule
```
