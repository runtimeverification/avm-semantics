```k
requires "json.md"

module AVM-INITIALIZATION-JSON-SYNTAX
    imports STRING
    imports INT
    imports JSON

    syntax NetworkState ::= JSON
    syntax KItem ::= setup(NetworkState)

    configuration
      <k> setup($PGM:NetworkState) </k>
      <returncode exit=""> 0 </returncode>
      <blockchain>
        <accountsMap>
          <account multiplicity="*" type="Map">
            <address>    "":String </address>
            <balance>    0         </balance>
          </account>
        </accountsMap>
      </blockchain>
endmodule

module AVM-INITIALIZATION-JSON
    imports AVM-INITIALIZATION-JSON-SYNTAX

    syntax KItem ::= #panic(String)

    rule <k> setup({"accounts": ACCTS:JSON, "transactions": _TXNS:JSON}) => setupAccounts(ACCTS) ... </k>
    rule <k> setup(INPUT:JSON) => #panic("Invalid input:" +String JSON2String(INPUT)) ... </k> [owise]

    syntax KItem ::= setupAccounts(JSON)
    rule <k> setupAccounts([ACCT_JSON, REST]) => addAccountJSON(ACCT_JSON) ~> setupAccounts([REST]) ... </k>
    rule <k> setupAccounts([.JSONs]) => .K ... </k>

    syntax KItem ::= setupTransactions(JSON)

    syntax KItem ::= addAccountJSON(JSON)
    rule <k> addAccountJSON({"address": ADDR:String, "balance": BALANCE:Int}) => .K ... </k>
         <accountsMap>
           (.Bag =>
           <account>
             <address> ADDR    </address>
             <balance> BALANCE </balance>
           </account>)
           ...
         </accountsMap>
    rule <k> addAccountJSON(INPUT:JSON) => #panic("Invalid account JSON:" +String JSON2String(INPUT)) ... </k> [owise]
  ```

Compile with:
```
kompile lib/include/kframework/avm/avm-initialization-json.md
```

Test with:
```
krun -cPGM='{"accounts": [], "transactions":[]}'
krun -cPGM='{"accounts": [{"address": "1", "balance": 1}], "transactions":[]}'
krun -cPGM='{"accounts": [ {"address": "1", "balance": 1}, {"address": "2", "balance": 2} ], "transactions":[]}'
```


```k
endmodule
```
