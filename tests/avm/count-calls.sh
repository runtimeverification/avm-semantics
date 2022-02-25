#!/bin/bash

# This is an example testing scenario for the new AVM/TEAL semantics that supports transaction groups.
#
# Initial network state
#   Apps: a stateful app that counts how many times it has been called
#         State: (one global Int, one local Int)
#   Accounts: one account that is the app's creator and had opted into the app
#   Assets: none
#
# Transaction group: tree app calls from the account to the app
#
# Expected effect on the apps state:
#   (Global 0, Local [(account 1, 0), (account 2, 0)]) =>
#   (Global 3, Local [(account 1, 2), (account 2, 1)])

# Account Initialization Commands

account[1]="addAccount <address> b\"1\" </address> <balance> 10000 </balance>"
account[2]="addAccount <address> b\"2\" </address> <balance> 10000 </balance>"

# App Initialization Commands
# approval programs should be retrieved from TEAL source files by the trailing integer id
app[1]="addApp <appID> 1 </appID> <address> b\"1\" </address> 0"

# App Optin Commands
optin[1]="optinApp <appID> 1 </appID> <address> b\"1\" </address>"
optin[2]="optinApp <appID> 1 </appID> <address> b\"2\" </address>"

# Transaction Group Initialisation Commands
txn[0]="addAppCallTx <txID>            0        </txID>"
txn[0]+="            <sender>          b\"1\"   </sender>"
txn[0]+="            <applicationID>   1        </applicationID>"
txn[0]+="            <onCompletion>    0        </onCompletion>"
txn[0]+="            <accounts>        b\"1\"   </accounts>"
txn[0]+="            <applicationArgs> NoTValue </applicationArgs>"

txn[1]="addAppCallTx <txID>            1        </txID>"
txn[1]+="            <sender>          b\"2\"   </sender>"
txn[1]+="            <applicationID>   1        </applicationID>"
txn[1]+="            <onCompletion>    0        </onCompletion>"
txn[1]+="            <accounts>        b\"2\"   </accounts>"
txn[1]+="            <applicationArgs> NoTValue </applicationArgs>"

txn[2]="addAppCallTx <txID>            2        </txID>"
txn[2]+="            <sender>          b\"1\"   </sender>"
txn[2]+="            <applicationID>   1        </applicationID>"
txn[2]+="            <onCompletion>    0        </onCompletion>"
txn[2]+="            <accounts>        b\"1\"   </accounts>"
txn[2]+="            <applicationArgs> NoTValue </applicationArgs>"

# Concatenate the sequence of initialization commands into a variable.
TEST_SCENARIO+="${account[1]}; ${account[2]};"
TEST_SCENARIO+="${app[1]};"
TEST_SCENARIO+="${optin[1]}; ${optin[2]};"
TEST_SCENARIO+="initTxGroup;"
TEST_SCENARIO+="${txn[0]};"
TEST_SCENARIO+="${txn[1]};"
TEST_SCENARIO+="${txn[2]};"
TEST_SCENARIO+="initGlobals;"
TEST_SCENARIO+="#evalTxGroup();"
TEST_SCENARIO+=".AS"

# execute the tests scenario with krun
krun -cPGM="${TEST_SCENARIO}"\
     -cTEAL_PROGRAMS="$(cat ./tests/teal/stateful/count_calls.teal); .TealPrograms"\
     -pTEAL_PROGRAMS=./parse-teal-programs.sh\
     --directory .build/usr/lib/kavm/avm-llvm\
     --verbose
