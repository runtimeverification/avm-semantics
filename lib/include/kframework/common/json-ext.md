JSON Utility Functions
======================

```k
requires "json.md"
```

JSON Extensions
---------------

Some common functions of JSON are provided here.

```k
module JSON-EXT
    imports BOOL
    imports K-EQUAL
    imports JSON
    imports STRING
```

-   `+JSONs` appends two JSON lists.
-   `reverseJSONs` reverses a JSON list.

```k
    syntax JSONs ::= JSONs "+JSONs" JSONs [function]
 // ------------------------------------------------
    rule .JSONs   +JSONs JS' => JS'
    rule (J , JS) +JSONs JS' => J , (JS +JSONs JS')

    syntax JSONs ::= reverseJSONs    ( JSONs         ) [function]
                   | reverseJSONsAux ( JSONs , JSONs ) [function]
 // -------------------------------------------------------------
    rule reverseJSONs(JS) => reverseJSONsAux(JS, .JSONs)

    rule reverseJSONsAux(.JSONs, JS') => JS'
    rule reverseJSONsAux((J, JS:JSONs), JS') => reverseJSONsAux(JS, (J, JS'))
```

-   `qsortJSONs` quick-sorts a list of key-value pairs.
-   `sortedJSONs` is a predicate saying whether a given list of JSONs is sorted or not.

```k
    syntax JSONs ::= qsortJSONs ( JSONs )          [function]
                   | #entriesLT ( String , JSONs ) [function]
                   | #entriesGE ( String , JSONs ) [function]
 // ---------------------------------------------------------
    rule qsortJSONs(.JSONs)            => .JSONs
    rule qsortJSONs(KEY : VALUE, REST) => qsortJSONs(#entriesLT(KEY, REST)) +JSONs (KEY : VALUE , qsortJSONs(#entriesGE(KEY, REST)))

    rule #entriesLT(_KEY, .JSONs)              => .JSONs
    rule #entriesLT( KEY, (KEY': VALUE, REST)) => KEY': VALUE , #entriesLT(KEY, REST) requires         KEY' <String KEY
    rule #entriesLT( KEY, (KEY':     _, REST)) =>               #entriesLT(KEY, REST) requires notBool KEY' <String KEY

    rule #entriesGE(_KEY, .JSONs)              => .JSONs
    rule #entriesGE( KEY, (KEY': VALUE, REST)) => KEY': VALUE , #entriesGE(KEY, REST) requires         KEY' >=String KEY
    rule #entriesGE( KEY, (KEY':     _, REST)) =>               #entriesGE(KEY, REST) requires notBool KEY' >=String KEY

    syntax Bool ::= sortedJSONs ( JSONs ) [function]
 // ------------------------------------------------
    rule sortedJSONs( .JSONs   ) => true
    rule sortedJSONs( _KEY : _ ) => true
    rule sortedJSONs( (KEY : _) , (KEY' : VAL) , REST ) => KEY <=String KEY' andThenBool sortedJSONs((KEY' : VAL) , REST)
```

-   `qsortJSON_1V` quick-sorts a list of JSON objects by the JSON value of their first key.

```k
    syntax JSONs ::= "qsortJSON_1V"     "(" JSONs ")"                     [function]
                   | "qsortJSON_1V_aux" "(" String "," JSON "," JSONs ")" [function]
                   | "#entriesLT_1V"    "(" String "," JSONs ")"          [function]
                   | "#entriesGE_1V"    "(" String "," JSONs ")"          [function]
 // ---------------------------------------------------------------------------------
    rule qsortJSON_1V(.JSONs) => .JSONs
    rule qsortJSON_1V(({ _:String : KEY:JSON , _:JSONs } #as OBJ):JSON, REST:JSONs)
      => qsortJSON_1V_aux(JSON2String(KEY), OBJ, REST)

    rule qsortJSON_1V_aux(KEY, OBJ, REST)
      => qsortJSON_1V(#entriesLT_1V(KEY, REST)) +JSONs (OBJ , qsortJSON_1V(#entriesGE_1V(KEY, REST)))

    rule #entriesLT_1V(_KEY, .JSONs) => .JSONs
    rule #entriesLT_1V( KEY, (({ _:String : KEY', _:JSONs } #as OBJ):JSON, REST:JSONs):JSONs)
      => #if JSON2String(KEY') <String KEY
           #then OBJ , #entriesLT_1V(KEY, REST)
           #else       #entriesLT_1V(KEY, REST)
         #fi

    rule #entriesGE_1V(_KEY, .JSONs) => .JSONs
    rule #entriesGE_1V( KEY, (({ _:String : KEY', _:JSONs } #as OBJ):JSON, REST:JSONs):JSONs)
      => #if JSON2String(KEY') >=String KEY
           #then OBJ , #entriesGE_1V(KEY, REST)
           #else       #entriesGE_1V(KEY, REST)
         #fi
```

```k
endmodule
```

