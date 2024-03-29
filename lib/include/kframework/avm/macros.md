Algorand State Macros
=====================

```k
require "avm/txn.md"
require "avm/blockchain.md"
```

```k
module MACROS
  imports ALGO-BLOCKCHAIN
  imports ALGO-TXN
```

Accounts
--------

```k

  syntax AccountCell ::= account(Bytes, Int, Int) [macro]
  // ----------------------------------------------------
  rule account(ADDRESS, BALANCE, MIN_BALANCE) =>
        <account>
          <address>    ADDRESS     </address>
          <balance>    BALANCE     </balance>
          <minBalance> MIN_BALANCE </minBalance>
          <round>      0           </round>
          <preRewards> 0           </preRewards>
          <rewards>    0           </rewards>
          <status>     0           </status>
          <key>        "":TBytes    </key>
          <appsCreated>   .Bag </appsCreated>
          <appsOptedIn>   .Bag </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn> .Bag </assetsOptedIn>
          <boxes>         .Bag </boxes>
        </account>
```

Transactions
------------

```k
  syntax TransactionCell ::= paymentTxn(String, String, Int, Bytes, Bytes, Int) [macro]
  // ---------------------------------------------------------------------

  rule paymentTxn(TXN_ID, GROUP_ID, GROUP_INDEX, SENDER, RECEIVER, AMOUNT) =>
       <transaction>
          <txID> TXN_ID </txID>
          <txHeader>
              <groupID>  GROUP_ID        </groupID>
              <groupIdx> GROUP_INDEX     </groupIdx>
              <sender>   SENDER          </sender>
              <txType>   "pay"           </txType>
              <typeEnum> @ pay           </typeEnum>
              <rekeyTo>  PARAM_ZERO_ADDR </rekeyTo>
              <fee>         0            </fee>
              <firstValid>  0            </firstValid>
              <lastValid>   0            </lastValid>
              <genesisHash> ""           </genesisHash>
              <genesisID>   ""           </genesisID>
              <lease>       ""           </lease>
              <note>        ""           </note>
          </txHeader>
          <txnTypeSpecificFields>
            <payTxFields>
                <receiver> RECEIVER                </receiver>
                <amount> AMOUNT                    </amount>
                <closeRemainderTo> PARAM_ZERO_ADDR </closeRemainderTo>
            </payTxFields>
            ...
          </txnTypeSpecificFields>
          <resume> false </resume>
          ...
        </transaction>
```

Predicates
----------

### Range of types

```k

  syntax Int ::= "pow64"  [alias] /* 2 ^Int 64"  */
  // ----------------------------------------------
  rule pow64  => 18446744073709551616

  syntax Bool ::= #rangeBool    ( Int )             [alias]
                | #rangeUInt    ( Int , Int )       [alias]
  // ------------------------------------------------------
  rule #rangeBool    (            X ) => X ==Int 0 orBool X ==Int 1
  rule #rangeUInt    (  64 ,      X ) => #range ( 0       <= X <  pow64           )

  syntax Bool ::= "#range" "(" Int "<"  Int "<"  Int ")" [macro]
                | "#range" "(" Int "<"  Int "<=" Int ")" [macro]
                | "#range" "(" Int "<=" Int "<"  Int ")" [macro]
                | "#range" "(" Int "<=" Int "<=" Int ")" [macro]
  // -----------------------------------------------------------
  rule #range ( LB <  X <  UB ) => LB  <Int X andBool X  <Int UB
  rule #range ( LB <  X <= UB ) => LB  <Int X andBool X <=Int UB
  rule #range ( LB <= X <  UB ) => LB <=Int X andBool X  <Int UB
  rule #range ( LB <= X <= UB ) => LB <=Int X andBool X <=Int UB
```

```k
endmodule
```
