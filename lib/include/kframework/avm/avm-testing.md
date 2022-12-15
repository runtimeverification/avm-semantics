```k
requires "json.md"
requires "avm/txn.md"
requires "avm/blockchain.md"
requires "avm/avm-configuration.md"
requires "avm/avm-execution.md"
requires "avm/algod/algod-models.md"
requires "teal/teal-syntax.md"

module AVM-TESTING-SYNTAX
  imports TEAL-PARSER-SYNTAX
  imports STRING
  imports JSON

endmodule
```

KAVM Testing Framework
----------------------

This module implements a testing framework that executes JSON-based test scenarios with KAVM.

```k
module AVM-TESTING
  imports INT
  imports LIST
  imports BYTES
  imports ALGO-BLOCKCHAIN
  imports ALGO-TXN
  imports TEAL-CONSTANTS
  imports AVM-CONFIGURATION
  imports ALGOD-MODELS
  imports AVM-EXECUTION
  imports K-IO

  configuration
    <avm-testing>
      <kavm/>
      <state-dumps> .List </state-dumps>
    </avm-testing>
```

### Scenario validation

A valid testing scenario must have a unique `"setup-network"` stage as the first stage, followed by any amount of `"submit-transactions"` stages.
The following rules validate the parsed scenario JSON.

```k
  syntax Bool ::= isValidScenario(JSON) [function]
  //----------------------------------------------
  rule isValidScenario({ "stages": [ STAGES ]}) => setupStageIsUniqueAndComesFirst(STAGES)

  syntax Bool ::= setupStageIsUniqueAndComesFirst(JSONs) [function]
  //---------------------------------------------------------------
  rule setupStageIsUniqueAndComesFirst(.JSONs) => false
  rule setupStageIsUniqueAndComesFirst(FIRST, OTHERS:JSONs)
       => assertStageTypes("setup-network", FIRST) andBool
          assertStageTypes("submit-transactions", OTHERS)

  syntax Bool ::= assertStageTypes(String, JSONs) [function]
  //--------------------------------------------------------
  rule assertStageTypes(EXPECTED_TYPE, { "data" : _, "stage-type": STAGE_TYPE }
                                       , OTHER_STAGES:JSONs
                                       )
       => STAGE_TYPE ==String EXPECTED_TYPE andBool assertStageTypes(EXPECTED_TYPE, OTHER_STAGES)
  rule assertStageTypes(EXPECTED_TYPE, { "data": _, "expected-returncode": _, "stage-type": STAGE_TYPE }
                                       , OTHER_STAGES:JSONs
                                       )
       => STAGE_TYPE ==String EXPECTED_TYPE andBool assertStageTypes(EXPECTED_TYPE, OTHER_STAGES)
  rule assertStageTypes(_EXPECTED_TYPE, .JSONs) => true
```


### Scenario initialization

The input JSON is supplied as the `PGM` configuration variable, check for validity and then read by the `#readScenario` rule.
The `#readScenario` rule uses the rules defined in the `ALGOD-MODELS`[../avm/algod/algod-models.md] module
to initialize the `<blockchain>` (handled by the `#readSetupStage` rule) and `<transactions>` (handled by the `#readExecutionStage` rule)
cells of the configuration.

```k
  rule <k> INPUT:JSON => #readScenario(INPUT) ... </k>
    requires isValidScenario(INPUT)

  rule <k> INPUT:JSON => #panic(INVALID_JSON) ... </k> [owise]

  syntax TestingCommand ::= #readScenario(JSON)
  //-------------------------------------------
  rule <k> #readScenario({ "stages": [ SETUP_STAGE, EXECUTION_STAGES:JSONs ]})
        => #readSetupStage(SETUP_STAGE)
        ~> #readExecutionStages([EXECUTION_STAGES]) ...
       </k>
```

#### Setup stage
The `#readSetupStage` rule initializes the `<accountsMap>` cell with the provided state of the accounts.
Note that the applications and ASAs are part of the accounts' state as well, and are be stored in the `<appsCreated>` and `<assetsCreated>` cells of their creators.

```k
  syntax TestingCommand ::= #readSetupStage(JSON)
  //---------------------------------------------
  rule <k> #readSetupStage({ "data": {"accounts": ACCTS:JSON}
                           , "stage-type": "setup-network"
                           })
        => #setupAccounts(ACCTS) ...
       </k>
```

#### Transaction execution stage

```k
  syntax TestingCommand ::= #readExecutionStages(JSONs)
  //---------------------------------------------------
  rule <k> #readExecutionStages([.JSONs]) => .K ... </k>
  rule <k> #readExecutionStages([STAGE, .JSONs])
        => #readExecutionStage(STAGE) ...
       </k>
//  rule <k> #readExecutionStages(X) => #panic(INVALID_JSON) ~> #readExecutionStages(X) ... </k> [owise]

  syntax TestingCommand ::= #readExecutionStage(JSON)
  //-------------------------------------------------
  rule <k> #readExecutionStage({ "data": {"transactions": TXNS:JSON}
                               , "expected-returncode": EXPECTED_RETURN_CODE
                               , "stage-type": "submit-transactions"
                               })
        => #setupTransactions(TXNS) ~> #initGlobals() ~> #evalTxGroup()
        ~> #checkExecutionResults(EXPECTED_RETURN_CODE) ...
       </k>

  syntax TestingCommand ::= #checkExecutionResults(Int)
  //--------------------------------------------------------
  rule <k> #checkExecutionResults(EXPECTED_RETURN_CODE)
        => #dumpFinalState() ...
       </k>
       <returncode> RETURN_CODE => 0 </returncode>
   requires RETURN_CODE ==Int EXPECTED_RETURN_CODE

  rule <k> #checkExecutionResults(EXPECTED_RETURN_CODE)
        => .K ...
       </k>
       <returncode> RETURN_CODE => 1 </returncode>
   requires notBool (RETURN_CODE ==Int EXPECTED_RETURN_CODE)

  syntax TestingCommand ::= #dumpFinalState()
  //-----------------------------------------
  rule <k> #dumpFinalState()
        => #log(JSON2String({ "accounts": [ #dumpAccounts(<accountsMap> ACCS </accountsMap>)]
                            , "transactions": [ #dumpConfirmedTransactions(<transactions> TXNS </transactions>)]}))
        ...
       </k>
       <accountsMap>  ACCS </accountsMap>
       <transactions> TXNS </transactions>
       <state-dumps>
         ...
         ( .List
        => ListItem({ "accounts"     : [ #dumpAccounts(<accountsMap> ACCS </accountsMap>)                ]
                    , "transactions" : [ #dumpConfirmedTransactions(<transactions> TXNS </transactions>) ]
                    , .JSONs
                   })
         )
       </state-dumps>
```

```k
endmodule
```
