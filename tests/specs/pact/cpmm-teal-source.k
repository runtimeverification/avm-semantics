requires "avm/teal/teal-syntax.md"

module CPMM-TEAL-SOURCE
  imports TEAL-SYNTAX

// Source: https://github.com/pactfi/algorand-testbed/blob/96bca251238f8a1b3f220bfbda9bcffaf935aa5f/constant_product.teal
// Syntactic changes applied:
//   SendToAddress_1 -> sub_1
//   SendToCaller_0 -> sub_2

  syntax TealInputPgm ::= cpmmApprovalMacro(Int, Int, TAddressLiteral, Int, Int) [alias]
  // -----------------------------------------------------------------------------------
  rule cpmmApprovalMacro(MACRO_PARAM_PRIMARY_ASSET_ID,
                         MACRO_PARAM_SECONDARY_ASSET_ID,
                         MACRO_PARAM_ADMIN_AND_TREASURY_ADDRESS,
                         MACRO_PARAM_FEE_BPS,
                         MACRO_PARAM_PACT_FEE_BPS) =>
#pragma version 6
txn RekeyTo
global ZeroAddress
==
txna Assets 0
int MACRO_PARAM_PRIMARY_ASSET_ID
==
&&
txna Assets 1
int MACRO_PARAM_SECONDARY_ASSET_ID
==
&&
txn NumAssets
int 3
<=
&&
txn NumAssets
int 3
==
bnz main_l83
int 1
main_l2:
&&
txn OnCompletion
int NoOp
==
&&
!
bnz main_l82
txn ApplicationID
int 0
==
bnz main_l81
txna ApplicationArgs 0
byte "OPTIN"
==
bnz main_l78
txna ApplicationArgs 0
byte "CLT"
==
bnz main_l69
txna ApplicationArgs 0
byte "SWAP"
==
bnz main_l51
txna ApplicationArgs 0
byte "ADDLIQ"
==
bnz main_l19
txna ApplicationArgs 0
byte "REMLIQ"
==
bnz main_l18
txna ApplicationArgs 0
byte "WITHDRAWFEES"
==
bnz main_l17
txna ApplicationArgs 0
byte "CHANGE_ADMIN"
==
bnz main_l16
txna ApplicationArgs 0
byte "CHANGE_TREASURY"
==
bnz main_l15
txna ApplicationArgs 0
byte "CHANGE_PACT_FEE"
==
bnz main_l14
err
main_l14:
txn Sender
byte "ADMIN"
app_global_get
==
assert
txna ApplicationArgs 1
btoi
byte "FEE_BPS"
app_global_get
int 2
/
<=
assert
byte "PACT_FEE_BPS"
txna ApplicationArgs 1
btoi
app_global_put
int 1
return
main_l15:
txn Sender
byte "ADMIN"
app_global_get
==
assert
txna Accounts 1
len
int 32
==
assert
byte "TREASURY"
txna Accounts 1
app_global_put
int 1
return
main_l16:
txn Sender
byte "ADMIN"
app_global_get
==
assert
txna Accounts 1
len
int 32
==
assert
byte "ADMIN"
txna Accounts 1
app_global_put
int 1
return
main_l17:
byte "TREASURY"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
byte "PRIMARY_FEES"
app_global_get
callsub sub_1
byte "TREASURY"
app_global_get
int MACRO_PARAM_SECONDARY_ASSET_ID
byte "SECONDARY_FEES"
app_global_get
callsub sub_1
byte "PRIMARY_FEES"
int 0
app_global_put
byte "SECONDARY_FEES"
int 0
app_global_put
int 1
return
main_l18:
txn GroupIndex
int 1
-
gtxns TypeEnum
int axfer
==
txn GroupIndex
int 1
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns AssetCloseTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns XferAsset
byte "LTID"
app_global_get
==
&&
txn GroupIndex
int 1
-
gtxns AssetReceiver
global CurrentApplicationAddress
==
&&
assert
byte "L"
app_global_get
int 0
!=
assert
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "A"
app_global_get
mulw
int 0
byte "L"
app_global_get
divmodw
pop
pop
swap
!
assert
store 19
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "B"
app_global_get
mulw
int 0
byte "L"
app_global_get
divmodw
pop
pop
swap
!
assert
store 20
byte "A"
byte "A"
app_global_get
load 19
-
app_global_put
byte "B"
byte "B"
app_global_get
load 20
-
app_global_put
byte "L"
byte "L"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
-
app_global_put
load 20
txna ApplicationArgs 2
btoi
-
pop
load 19
txna ApplicationArgs 1
btoi
-
pop
int MACRO_PARAM_PRIMARY_ASSET_ID
load 19
callsub sub_2
int MACRO_PARAM_SECONDARY_ASSET_ID
load 20
callsub sub_2
int 1
return
main_l19:
byte "LTID"
app_global_get
assert
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l50
txn GroupIndex
int 2
-
gtxns TypeEnum
int axfer
==
txn GroupIndex
int 2
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 2
-
gtxns AssetCloseTo
global ZeroAddress
==
&&
txn GroupIndex
int 2
-
gtxns XferAsset
int MACRO_PARAM_PRIMARY_ASSET_ID
==
&&
txn GroupIndex
int 2
-
gtxns AssetReceiver
global CurrentApplicationAddress
==
&&
main_l21:
assert
txn GroupIndex
int 1
-
gtxns TypeEnum
int axfer
==
txn GroupIndex
int 1
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns AssetCloseTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns XferAsset
int MACRO_PARAM_SECONDARY_ASSET_ID
==
&&
txn GroupIndex
int 1
-
gtxns AssetReceiver
global CurrentApplicationAddress
==
&&
assert
byte "L"
app_global_get
int 0
==
bnz main_l43
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l42
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l24:
byte "L"
app_global_get
mulw
int 0
byte "A"
app_global_get
divmodw
pop
pop
swap
!
assert
store 12
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "L"
app_global_get
mulw
int 0
byte "B"
app_global_get
divmodw
pop
pop
swap
!
assert
store 13
load 12
load 13
dup2
>
select
txna ApplicationArgs 1
btoi
-
pop
load 12
load 13
dup2
>
select
int 0
>
assert
byte "LTID"
app_global_get
load 12
load 13
dup2
>
select
callsub sub_2
byte "L"
byte "L"
app_global_get
load 12
load 13
dup2
>
select
+
app_global_put
load 12
load 13
>
bnz main_l38
load 12
load 13
<
bnz main_l31
byte "A"
byte "A"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l30
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l28:
+
app_global_put
byte "B"
byte "B"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
+
app_global_put
main_l29:
int 1
return
main_l30:
txn GroupIndex
int 2
-
gtxns Amount
b main_l28
main_l31:
byte "B"
app_global_get
store 16
byte "B"
byte "B"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l37
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l33:
byte "B"
app_global_get
mulw
int 0
byte "A"
app_global_get
divmodw
||
+
swap
!
assert
+
app_global_put
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "B"
app_global_get
load 16
-
-
store 18
int MACRO_PARAM_SECONDARY_ASSET_ID
load 18
callsub sub_2
byte "A"
byte "A"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l36
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l35:
+
app_global_put
b main_l29
main_l36:
txn GroupIndex
int 2
-
gtxns Amount
b main_l35
main_l37:
txn GroupIndex
int 2
-
gtxns Amount
b main_l33
main_l38:
byte "A"
app_global_get
store 15
byte "A"
byte "A"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "A"
app_global_get
mulw
int 0
byte "B"
app_global_get
divmodw
||
+
swap
!
assert
+
app_global_put
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l41
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l40:
byte "A"
app_global_get
load 15
-
-
store 17
int MACRO_PARAM_PRIMARY_ASSET_ID
load 17
callsub sub_2
byte "B"
byte "B"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
+
app_global_put
b main_l29
main_l41:
txn GroupIndex
int 2
-
gtxns Amount
b main_l40
main_l42:
txn GroupIndex
int 2
-
gtxns Amount
b main_l24
main_l43:
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l49
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l45:
itob
txn GroupIndex
int 1
-
gtxns AssetAmount
itob
b*
bsqrt
btoi
store 14
byte "L"
load 14
app_global_put
byte "A"
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l48
txn GroupIndex
int 2
-
gtxns AssetAmount
main_l47:
app_global_put
byte "B"
txn GroupIndex
int 1
-
gtxns AssetAmount
app_global_put
load 14
int 1000
-
store 14
load 14
txna ApplicationArgs 1
btoi
>=
assert
byte "LTID"
app_global_get
load 14
callsub sub_2
b main_l29
main_l48:
txn GroupIndex
int 2
-
gtxns Amount
b main_l47
main_l49:
txn GroupIndex
int 2
-
gtxns Amount
b main_l45
main_l50:
txn GroupIndex
int 2
-
gtxns TypeEnum
int pay
==
txn GroupIndex
int 2
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 2
-
gtxns CloseRemainderTo
global ZeroAddress
==
&&
txn GroupIndex
int 2
-
gtxns Receiver
global CurrentApplicationAddress
==
&&
b main_l21
main_l51:
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l68
txn GroupIndex
int 1
-
gtxns TypeEnum
int axfer
==
txn GroupIndex
int 1
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns AssetCloseTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns XferAsset
int MACRO_PARAM_PRIMARY_ASSET_ID
==
&&
txn GroupIndex
int 1
-
gtxns AssetReceiver
global CurrentApplicationAddress
==
&&
main_l53:
bnz main_l58
txn GroupIndex
int 1
-
gtxns TypeEnum
int axfer
==
txn GroupIndex
int 1
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns AssetCloseTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns XferAsset
int MACRO_PARAM_SECONDARY_ASSET_ID
==
&&
txn GroupIndex
int 1
-
gtxns AssetReceiver
global CurrentApplicationAddress
==
&&
bnz main_l57
int 0
return
int 1
return
main_l57:
txn GroupIndex
int 1
-
gtxns AssetAmount
byte "A"
app_global_get
mulw
int 0
byte "B"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
+
divmodw
pop
pop
swap
!
assert
store 9
load 9
byte "PACT_FEE_BPS"
app_global_get
mulw
int 0
int 10000
divmodw
pop
pop
swap
!
assert
store 11
load 9
int 10000
byte "FEE_BPS"
app_global_get
-
mulw
int 0
int 10000
divmodw
pop
pop
swap
!
assert
store 10
load 10
txna ApplicationArgs 1
btoi
-
pop
byte "A"
byte "A"
app_global_get
load 10
-
app_global_put
byte "A"
byte "A"
app_global_get
load 11
-
app_global_put
byte "PRIMARY_FEES"
byte "PRIMARY_FEES"
app_global_get
load 11
+
app_global_put
byte "B"
byte "B"
app_global_get
txn GroupIndex
int 1
-
gtxns AssetAmount
+
app_global_put
int MACRO_PARAM_PRIMARY_ASSET_ID
load 10
callsub sub_2
int 1
return
main_l58:
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l67
txn GroupIndex
int 1
-
gtxns AssetAmount
main_l60:
byte "B"
app_global_get
mulw
int 0
byte "A"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l66
txn GroupIndex
int 1
-
gtxns AssetAmount
main_l62:
+
divmodw
pop
pop
swap
!
assert
store 7
load 7
byte "PACT_FEE_BPS"
app_global_get
mulw
int 0
int 10000
divmodw
pop
pop
swap
!
assert
store 8
load 7
int 10000
byte "FEE_BPS"
app_global_get
-
mulw
int 0
int 10000
divmodw
pop
pop
swap
!
assert
store 6
load 6
txna ApplicationArgs 1
btoi
-
pop
byte "B"
byte "B"
app_global_get
load 6
-
app_global_put
byte "B"
byte "B"
app_global_get
load 8
-
app_global_put
byte "SECONDARY_FEES"
byte "SECONDARY_FEES"
app_global_get
load 8
+
app_global_put
byte "A"
byte "A"
app_global_get
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l65
txn GroupIndex
int 1
-
gtxns AssetAmount
main_l64:
+
app_global_put
int MACRO_PARAM_SECONDARY_ASSET_ID
load 6
callsub sub_2
int 1
return
main_l65:
txn GroupIndex
int 1
-
gtxns Amount
b main_l64
main_l66:
txn GroupIndex
int 1
-
gtxns Amount
b main_l62
main_l67:
txn GroupIndex
int 1
-
gtxns Amount
b main_l60
main_l68:
txn GroupIndex
int 1
-
gtxns TypeEnum
int pay
==
txn GroupIndex
int 1
-
gtxns RekeyTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns CloseRemainderTo
global ZeroAddress
==
&&
txn GroupIndex
int 1
-
gtxns Receiver
global CurrentApplicationAddress
==
&&
b main_l53
main_l69:
txn Sender
global CreatorAddress
==
assert
byte "LTID"
app_global_get
int 0
==
assert
int MACRO_PARAM_PRIMARY_ASSET_ID
!
bnz main_l77
int MACRO_PARAM_PRIMARY_ASSET_ID
asset_params_get AssetUnitName
store 3
store 2
load 2
byte ""
==
bnz main_l76
load 2
store 0
main_l72:
int MACRO_PARAM_SECONDARY_ASSET_ID
asset_params_get AssetUnitName
store 5
store 4
load 4
byte ""
==
bnz main_l75
load 4
store 1
main_l74:
itxn_begin
int 0
itxn_field Fee
int acfg
itxn_field TypeEnum
int 18446744073709551615
itxn_field ConfigAssetTotal
int 6
itxn_field ConfigAssetDecimals
load 0
byte "/"
concat
load 1
concat
byte " PACT LP Token"
concat
itxn_field ConfigAssetName
byte "PLP"
itxn_field ConfigAssetUnitName
byte "https://pact.fi/"
itxn_field ConfigAssetURL
global CurrentApplicationAddress
itxn_field ConfigAssetReserve
itxn_submit
byte "LTID"
itxn CreatedAssetID
app_global_put
int 1
return
main_l75:
byte "?"
store 1
b main_l74
main_l76:
byte "?"
store 0
b main_l72
main_l77:
byte "ALGO"
store 0
b main_l72
main_l78:
txn Sender
global CreatorAddress
==
assert
int MACRO_PARAM_PRIMARY_ASSET_ID
!
!
bnz main_l80
main_l79:
itxn_begin
int axfer
itxn_field TypeEnum
global CurrentApplicationAddress
itxn_field AssetReceiver
int 0
itxn_field AssetAmount
int MACRO_PARAM_SECONDARY_ASSET_ID
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
int 1
return
main_l80:
itxn_begin
int axfer
itxn_field TypeEnum
global CurrentApplicationAddress
itxn_field AssetReceiver
int 0
itxn_field AssetAmount
int MACRO_PARAM_PRIMARY_ASSET_ID
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
b main_l79
main_l81:
int MACRO_PARAM_PRIMARY_ASSET_ID
int MACRO_PARAM_SECONDARY_ASSET_ID
<
assert
int MACRO_PARAM_FEE_BPS
int 10000
<
assert
byte "CONFIG"
int MACRO_PARAM_PRIMARY_ASSET_ID
itob
int MACRO_PARAM_SECONDARY_ASSET_ID
itob
concat
int MACRO_PARAM_FEE_BPS
itob
concat
app_global_put
byte "CONTRACT_NAME"
byte "PACT AMM"
app_global_put
byte "VERSION"
int 2
app_global_put
byte "A"
int 0
app_global_put
byte "B"
int 0
app_global_put
byte "L"
int 0
app_global_put
byte "LTID"
int 0
app_global_put
byte "ADMIN"
addr MACRO_PARAM_ADMIN_AND_TREASURY_ADDRESS
app_global_put
byte "TREASURY"
addr MACRO_PARAM_ADMIN_AND_TREASURY_ADDRESS
app_global_put
byte "FEE_BPS"
int MACRO_PARAM_FEE_BPS
app_global_put
byte "PACT_FEE_BPS"
int MACRO_PARAM_PACT_FEE_BPS
app_global_put
byte "PRIMARY_FEES"
int 0
app_global_put
byte "SECONDARY_FEES"
int 0
app_global_put
int 1
return
main_l82:
int 0
return
main_l83:
txna Assets 2
byte "LTID"
app_global_get
==
b main_l2

// SendToCaller
sub_2:
store 22
store 21
load 21
bnz sub_2_l2
itxn_begin
int pay
itxn_field TypeEnum
txn Sender
itxn_field Receiver
load 22
itxn_field Amount
int 0
itxn_field Fee
itxn_submit
b sub_2_l3
sub_2_l2:
itxn_begin
int axfer
itxn_field TypeEnum
txn Sender
itxn_field AssetReceiver
load 22
itxn_field AssetAmount
load 21
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
sub_2_l3:
retsub

// SendToAddress
sub_1:
store 25
store 24
store 23
load 24
bnz sub_1_l2
itxn_begin
int pay
itxn_field TypeEnum
load 23
itxn_field Receiver
load 25
itxn_field Amount
int 0
itxn_field Fee
itxn_submit
b sub_1_l3
sub_1_l2:
itxn_begin
int axfer
itxn_field TypeEnum
load 23
itxn_field AssetReceiver
load 25
itxn_field AssetAmount
load 24
itxn_field XferAsset
int 0
itxn_field Fee
itxn_submit
sub_1_l3:
retsub


endmodule
