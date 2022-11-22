Transaction Execution Deque
===========================

```k
module AVM-TXN-DEQUE
  imports LIST
  imports SET
  imports AVM-CONFIGURATION
```

The semantics maintains a deque that tracks the order in which the transactions will be executed.
The deque will contain integer identifiers of transactions as tracked by the `<txID>` cell
of a `<transaction>` cell.

Note that the deque operations only *read* the `<transactions>` cell, and will panic of a transaction
is not present there.

**Operations**:

* push a transaction to the back of the deque;
* push a transaction to the front of the deque;
* pop a transaction from the front of the deque.

```k
  syntax TxnDeque ::= List
  //----------------------
```

### Push to the back

This operation adds a transaction id to the *back* of the deque, scheduling it for evaluation
after all preceding transactions. Panic if the transaction is missing or is already
scheduled for evaluation.

```k
  syntax TxnDequeCommand ::= #pushTxnBack(TxIDCell)
  //-----------------------------------------------
  rule <k> #pushTxnBack(<txID> TXN_ID </txID>) => .K ... </k>
       <txnDeque>
         <deque> TXNS => TXNS ListItem(TXN_ID) </deque>
         <dequeIndexSet> INDICES => SetItem(TXN_ID) INDICES  </dequeIndexSet>
       </txnDeque>
       <transactions> TS </transactions>
       requires notBool (TXN_ID in INDICES)
        andBool TXN_ID in_txns(<transactions> TS </transactions>)

  rule <k> #pushTxnBack(<txID> TXN_ID </txID>) => #internalPanic(TXN_DEQUE_ERROR) ... </k>
       <dequeIndexSet> INDICES </dequeIndexSet>
       requires TXN_ID in INDICES

  rule <k> #pushTxnBack(<txID> TXN_ID </txID>) => #internalPanic(TXN_DEQUE_ERROR) ... </k>
       <transactions> TS </transactions>
    requires notBool (TXN_ID in_txns(<transactions> TS </transactions>))
```

### Push to the front

This operation adds a transaction id to the *front* of the deque, scheduling it
to be evaluated as next transaction. Panic if the transaction is missing or is already
scheduled for evaluation.

```k
  syntax TxnDequeCommand ::= #pushTxnFront(TxIDCell)
  //-----------------------------------------------
  rule <k> #pushTxnFront(<txID> TXN_ID </txID>) => .K ... </k>
       <txnDeque>
         <deque> TXNS => ListItem(TXN_ID) TXNS </deque>
         <dequeIndexSet> INDICES => SetItem(TXN_ID) INDICES  </dequeIndexSet>
       </txnDeque>
       <transactions> TS </transactions>
       requires notBool (TXN_ID in INDICES)
        andBool TXN_ID in_txns(<transactions> TS </transactions>)

  rule <k> #pushTxnFront(<txID> TXN_ID </txID>) => #internalPanic(TXN_DEQUE_ERROR) ... </k>
       <dequeIndexSet> INDICES </dequeIndexSet>
       requires TXN_ID in INDICES

  rule <k> #pushTxnFront(<txID> TXN_ID </txID>) => #internalPanic(TXN_DEQUE_ERROR) ... </k>
       <transactions> TS </transactions>
    requires notBool (TXN_ID in_txns(<transactions> TS </transactions>))
```

### Pop from the front

This operation pops a transaction id from the front of the queue and sets it as the
`<currentTx>`, triggering its evaluation by the AVM.
Panics if the deque is empty.

**NOTE**: we intentionally do not remove the id from the `<dequeIndexSet>`, so if the group,
for some reason, contains duplicate ids, the semantics will panic.
In Algorand, transaction ids are supposed to be unique, so this should never happen. But if it does,
we will know immediately, since `#pushTxnFront()`/`#pushTxnBack()` would panic.

**NOTE**: the check that the id is present in `<transactions>` will have already been performed by
`#pushTxnFront()`/`#pushTxnBack()`.

```k
  syntax TxnDequeCommand ::= #getNextTxn()
  rule <k> #getNextTxn() => .K ... </k>
       <deque> ListItem(TXN_ID) _TXNS </deque>
       <currentTx> _ => TXN_ID </currentTx>


  rule <k> #getNextTxn() => #internalPanic(TXN_DEQUE_ERROR) ... </k>
       <deque> .List </deque>

  syntax TxnDequeCommand ::= #popTxnFront()
  //-----------------------------------------------
  rule <k> #popTxnFront() => .K ... </k>
       <deque> ListItem(_TXN_ID) TXNS => TXNS </deque>

  rule <k> #popTxnFront() => .K ... </k>
       <deque> .List </deque>

endmodule
```
