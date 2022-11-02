```k
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"

```

```k
module AVM-INITIALIZATION
  imports INT
  imports LIST
  imports STRING
  imports BYTES
  imports ALGO-BLOCKCHAIN
  imports AVM-CONFIGURATION
  imports AVM-TXN-DEQUE
  imports TEAL-CONSTANTS
  imports ALGO-TXN
```

### Globals Initialization

To know the group size, we need to count the transactions in the group:

```k
  syntax Int ::= countTxns(TransactionsCell) [function, functional]
  // --------------------------------------------------------------

  rule countTxns(<transactions> <transaction> _ </transaction> REST </transactions>)
       => 1 +Int countTxns(<transactions> REST </transactions>)
  rule countTxns(<transactions> .Bag </transactions>)
       => 0

  syntax Int ::= countTxnsInGroup(TransactionsCell, String) [function, functional]
  // -----------------------------------------------------------------------------

  rule countTxnsInGroup(<transactions> <transaction> <groupID> GROUP </groupID> ... </transaction> REST </transactions>, GROUP)
       => 1 +Int countTxnsInGroup(<transactions> REST </transactions>, GROUP)
  rule countTxnsInGroup(<transactions> <transaction> <groupID> GROUP' </groupID> ... </transaction> REST </transactions>, GROUP)
       => countTxnsInGroup(<transactions> REST </transactions>, GROUP)
    requires GROUP' =/=K GROUP
  rule countTxnsInGroup(<transactions> .Bag </transactions>, _)
       => 0
```

The semantics does not currently care about block production, therefore the `<globalRound> `
and ` <latestTimestamp>` are initialized with somewhat arbitrary values.

```k
  syntax AlgorandCommand ::= #initGlobals()
  //---------------------------------------
  rule <k> #initGlobals() => .K ... </k>
       <globals>
         <groupSize>            _ => countTxns(<transactions> TXNS </transactions>) </groupSize>
         <globalRound>          _ => 6 </globalRound>
         <latestTimestamp>      _ => 50  </latestTimestamp>
         <currentApplicationID> _ => 0 </currentApplicationID>
         <currentApplicationAddress> _ => .Bytes </currentApplicationAddress>
       </globals>
       <transactions> TXNS </transactions>
```

### Transaction Index Initialization

Traverse the `<transactions>` cell and index the relation of group ids with transaction ids

```k
  syntax AlgorandCommand ::= #initTxnIndexMap()
  //-------------------------------------------
  rule <k> #initTxnIndexMap() => #initTxnIndexMap(collectTxnIds(<transactions> TXNS </transactions>)) ... </k>
       <transactions> TXNS </transactions>

  syntax AlgorandCommand ::= #initTxnIndexMap(List)
  //-----------------------------------------------
  rule <k> #initTxnIndexMap(ListItem(TXN_ID) REST) => #initTxnIndexMap(ListItem(TXN_ID) REST) ... </k>
       <transaction>
         <txID> TXN_ID </txID>
         <groupID> GROUP_ID </groupID>
         ...
       </transaction>
       <txnIndexMap>
          ITEMS =>
          <txnIndexMapGroup>
            <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
            <txnIndexMapGroupValues> .Map </txnIndexMapGroupValues>
          </txnIndexMapGroup>
          ITEMS
       </txnIndexMap>
    requires notBool (group_id_in_index_map(GROUP_ID))

  rule <k> #initTxnIndexMap(ListItem(TXN_ID) REST) => #initTxnIndexMap(REST) ... </k>
       <transaction>
         <txID> TXN_ID </txID>
         <groupID> GROUP_ID </groupID>
         <groupIdx> GROUP_IDX </groupIdx>
         ...
       </transaction>
       <txnIndexMap>
          <txnIndexMapGroup>
            <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
            <txnIndexMapGroupValues> VALUES => VALUES[GROUP_IDX <- TXN_ID] </txnIndexMapGroupValues>
          </txnIndexMapGroup>
          ...
       </txnIndexMap>

  rule <k> #initTxnIndexMap(.List) => .K ... </k>

  syntax List ::= collectTxnIds(TransactionsCell) [function, functional]
  //--------------------------------------------------------------------
  rule collectTxnIds(<transactions> .Bag </transactions>) => .List
  rule collectTxnIds(<transactions> <transaction> <txID> TXN_ID </txID> ... </transaction> TXNS </transactions>)
    => ListItem(TXN_ID) collectTxnIds(<transactions> TXNS </transactions>)

  syntax Bool ::= "group_id_in_index_map" "(" String ")" [function, functional]
  //---------------------------------------------------------------------------
  rule [[ group_id_in_index_map(GROUP_ID) => true ]]
       <txnIndexMapGroupKey> GROUP_ID </txnIndexMapGroupKey>
  rule group_id_in_index_map(_GROUP_ID) => false [owise]

```

```k
endmodule
```
