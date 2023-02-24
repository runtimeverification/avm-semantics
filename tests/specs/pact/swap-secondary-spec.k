module SWAP-SECONDARY-SPEC
  imports VERIFICATION

  claim
  <kavm>
    <k>
      #evalTxGroup( ) => .K
    </k>
    <returncode>
      4 => ?RETURN_CODE
    </returncode>
    <returnstatus>
      "" => ?_
    </returnstatus>
    <transactions>
      (<transaction>
        <txID> Int2String(AXFER_TX_ID:Int) </txID>
        <txHeader>
          <groupID> Int2String(GROUP_ID:Int) </groupID>
          <groupIdx> AXFER_TX_GROUP_IDX:Int </groupIdx>
          <sender>
            SENDER_ADDR:Bytes
          </sender>
          <txType> "axfer" </txType>
          <typeEnum> @axfer </typeEnum>
          <rekeyTo> _TXN1_REKEY_TO:Bytes </rekeyTo>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <assetTransferTxFields>
            <xferAsset> SECONDARY_ASSET_ID_TXN:Int </xferAsset>
            <assetAmount> AMOUNT </assetAmount>
            <assetReceiver> 
              CONTRACT_ACCOUNT_ADDR_TXN:Bytes
            </assetReceiver>
            <assetASender> PARAM_ZERO_ADDR </assetASender>
            <assetCloseTo> PARAM_ZERO_ADDR </assetCloseTo>
          </assetTransferTxFields>
        </txnTypeSpecificFields>
        <resume> false </resume>
        ...
      </transaction>
      <transaction>
        <txID> Int2String(APPL_TX_ID:Int) </txID>
        <txHeader>
          <groupID> Int2String(GROUP_ID:Int) </groupID>
          <groupIdx> APPL_TX_GROUP_IDX:Int </groupIdx>
          <sender>
            SENDER_ADDR
          </sender>
          <txType> "appl" </txType>
          <typeEnum> @appl </typeEnum>
          <rekeyTo> _TXN2_REKEY_TO:Bytes </rekeyTo>
          <firstValid> 0 </firstValid>
          <lastValid> 0 </lastValid>
          ...
        </txHeader>
        <txnTypeSpecificFields>
          <appCallTxFields>
            <applicationID> APP_ID </applicationID>
            <onCompletion> @ NoOp </onCompletion>
            <foreignAssets> PRIMARY_ASSET_ID_TXN:Int SECONDARY_ASSET_ID_TXN:Int </foreignAssets>
            <applicationArgs> b"SWAP" Int2Bytes(MIN_EXPECTED, BE, Unsigned) </applicationArgs>
            ...
          </appCallTxFields>
        </txnTypeSpecificFields>
        <resume> false </resume>
        ...
      </transaction>) => ?_
    </transactions>
    <avmExecution>
      <currentTx>
        Int2String(APPL_TX_ID) => ?_
      </currentTx>
      <txnDeque>
        <deque>
          (ListItem(Int2String(AXFER_TX_ID))
          ListItem(Int2String(APPL_TX_ID))) => ?_
        </deque>
        <dequeIndexSet>
          (SetItem(Int2String(AXFER_TX_ID))
          SetItem(Int2String(APPL_TX_ID))) => ?_
        </dequeIndexSet>
      </txnDeque>
      <currentTxnExecution>
        <globals>
          <groupSize>
            0 => ?_
          </groupSize>
          <globalRound>
            6 => ?_
          </globalRound>
          <latestTimestamp>
            50 => ?_
          </latestTimestamp>
          <currentApplicationID>
            0 => ?_
          </currentApplicationID>
          <currentApplicationAddress>
            b"" => ?_
          </currentApplicationAddress>
          <creatorAddress>
            b"" => ?_
          </creatorAddress>
        </globals>
        <teal>
          <pc>
            0 => ?_
          </pc>
          <program>
            .Map => ?_
          </program>
          <mode>
            undefined => ?_
          </mode>
          <version>
            1 => ?_
          </version>
          <stack>
            .TStack => ?_
          </stack>
          <stacksize>
            0 => ?_
          </stacksize>
          <jumped>
            false => ?_
          </jumped>
          <labels>
            .Map => ?_
          </labels>
          <callStack>
            .List => ?_
          </callStack>
          <scratch>
            .Map => ?_
          </scratch>
          <intcblock>
            .Map => ?_
          </intcblock>
          <bytecblock>
            .Map => ?_
          </bytecblock>
        </teal>
        <effects>
          .List => ?_
        </effects>
        <lastTxnGroupID>
          "" => ?_
        </lastTxnGroupID>
      </currentTxnExecution>
      <innerTransactions>
        .List => ?_
      </innerTransactions>
      <activeApps>
        .Set => ?_
      </activeApps>
      <touchedAccounts>
        .List => ?_
      </touchedAccounts>
    </avmExecution>
    <blockchain>
      <accountsMap>
        <account>
          <address>
            ASSET_CREATOR_ADDRESS
          </address>
          <balance>
            _ASSET_CREATOR_BALANCE:Int
          </balance>
          <minBalance>
            _ASSET_CREATOR_MIN_BALANCE:Int
          </minBalance>
          <round>
            0
          </round>
          <preRewards>
            0
          </preRewards>
          <rewards>
            0
          </rewards>
          <status>
            0
          </status>
          <key>
            PARAM_ZERO_ADDR
          </key>
          <appsCreated>
            .Bag
          </appsCreated>
          <appsOptedIn>
            .Bag
          </appsOptedIn>
          <assetsCreated>
            asset(PRIMARY_ASSET_ID:Int, (pow64) -Int 1, 0, PARAM_ZERO_ADDR)
            asset(SECONDARY_ASSET_ID:Int, (pow64) -Int 1, 0, PARAM_ZERO_ADDR)
          </assetsCreated>
          <assetsOptedIn>
            assetHolding(PRIMARY_ASSET_ID, _ASSET_CREATOR_ASSET1_BALANCE:Int)
            assetHolding(SECONDARY_ASSET_ID, _ASSET_CREATOR_ASSET2_BALANCE:Int)
          </assetsOptedIn>
          <boxes>
            .Bag
          </boxes>
        </account> 
        <account>
          <address>
            SENDER_ADDR
          </address>
          <balance>
            SENDER_BALANCE:Int
          </balance>
          <minBalance>
            SENDER_MIN_BALANCE:Int
          </minBalance>
          <round>
            0
          </round>
          <preRewards>
            0
          </preRewards>
          <rewards>
            0
          </rewards>
          <status>
            0
          </status>
          <key>
            PARAM_ZERO_ADDR
          </key>
          <appsCreated>
            .Bag
          </appsCreated>
          <appsOptedIn>
            .Bag
          </appsOptedIn>
          <assetsCreated>
            .Bag
          </assetsCreated>
          <assetsOptedIn>
            ((assetHolding(PRIMARY_ASSET_ID, SENDER_ASSET1_INITIAL_BALANCE)) => 
              (assetHolding(PRIMARY_ASSET_ID, ?SENDER_ASSET1_FINAL_BALANCE)))
            ((assetHolding(SECONDARY_ASSET_ID, SENDER_ASSET2_INITIAL_BALANCE)) =>
              (assetHolding(SECONDARY_ASSET_ID, ?SENDER_ASSET2_FINAL_BALANCE)))
              ...
          </assetsOptedIn>
          <boxes>
            .Bag
          </boxes>
        </account>
        <account>
          <address>
            CONTRACT_CREATOR_ADDR:Bytes
          </address>
          <balance>
            _CONTRACT_CREATOR_BALANCE:Int
          </balance>
          <minBalance>
            _CONTRACT_CREATOR_MIN_BALANCE:Int
          </minBalance>
          <round>
            0
          </round>
          <preRewards>
            0
          </preRewards>
          <rewards>
            0
          </rewards>
          <status>
            0
          </status>
          <key>
            PARAM_ZERO_ADDR
          </key>
          <appsCreated>
            <app>
              <appID>
                APP_ID:Int
              </appID>
              <approvalPgmSrc>
                cpmmApprovalMacro(PRIMARY_ASSET_ID, SECONDARY_ASSET_ID, _ADMIN_AND_TREASURY_ADDRESS, FEE_BPS, PACT_FEE_BPS)
              </approvalPgmSrc>
              <clearStatePgmSrc>
                #pragma version 6
                int 1
                return
              </clearStatePgmSrc>
              <approvalPgm>
                "f8c21b5d5a2333918522f20debe4764d5bd1ebcf0974ef07a6102757a87f9aaefb7b066d66c453bfb557eab1cbca33188bb3a581c2498c6fab5f3ca8a227b580.teal"
              </approvalPgm>
              <clearStatePgm>
                "31b9e960de315f23379617f8de86afcd5f9ee74e06c60846eff6a7b3236298d70f9110b495e0bfd6f8f863dc6e8e9e66256306cf2e58d4fdf20adf7ad9a9ac81.teal"
              </clearStatePgm>
              <globalState>
                <globalNumInts>
                  9
                </globalNumInts>
                <globalNumBytes>
                  4
                </globalNumBytes>
                <globalBytes>
                  b"ADMIN"         |-> CONTRACT_CREATOR_ADDR
                  b"CONFIG"        |-> b"\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x01,"
                  b"CONTRACT_NAME" |-> b"PACT AMM"
                  b"TREASURY"      |-> CONTRACT_CREATOR_ADDR
                </globalBytes>
                <globalInts>
                  b"A"              |-> (AMM_ASSET1_BALANCE_STORED => ?AMM_ASSET1_FINAL_BALANCE_STORED)
                  b"B"              |-> (AMM_ASSET2_BALANCE_STORED => ?AMM_ASSET2_FINAL_BALANCE_STORED)
                  b"FEE_BPS"        |-> FEE_BPS
                  b"L"              |-> _LIQUIDITY:Int
                  b"LTID"           |-> LT_ID:Int
                  b"PACT_FEE_BPS"   |-> PACT_FEE_BPS
                  b"PRIMARY_FEES"   |-> (PRIMARY_FEES_INITIAL:Int => ?PRIMARY_FEES_FINAL)
                  b"SECONDARY_FEES" |-> (SECONDARY_FEES_INITIAL:Int => ?SECONDARY_FEES_FINAL)
                  b"VERSION"        |-> 2
                </globalInts>
              </globalState>
              <localState>
                <localNumInts>
                  0
                </localNumInts>
                <localNumBytes>
                  0
                </localNumBytes>
              </localState>
              <extraPages>
                NoTValue
              </extraPages>
            </app>
          </appsCreated>
          <appsOptedIn>
            .Bag
          </appsOptedIn>
          <assetsCreated>
            .Bag
          </assetsCreated>
          <assetsOptedIn>
            .Bag
          </assetsOptedIn>
          <boxes>
            .Bag
          </boxes>
        </account> 
        <account>
          <address>
            CONTRACT_ACCOUNT_ADDR:Bytes
          </address>
          <balance>
            CONTRACT_ACCOUNT_BALANCE:Int
          </balance>
          <minBalance>
            CONTRACT_ACCOUNT_MIN_BALANCE:Int
          </minBalance>
          <round>
            0
          </round>
          <preRewards>
            0
          </preRewards>
          <rewards>
            0
          </rewards>
          <status>
            0
          </status>
          <key>
            PARAM_ZERO_ADDR
          </key>
          <appsCreated>
            .Bag
          </appsCreated>
          <appsOptedIn>
            .Bag
          </appsOptedIn>
          <assetsCreated>
            asset(LT_ID, (pow64) -Int 1, 0, PARAM_ZERO_ADDR)
          </assetsCreated>
          <assetsOptedIn>
            ((assetHolding(PRIMARY_ASSET_ID, AMM_ASSET1_BALANCE_REAL)) =>
              (assetHolding(PRIMARY_ASSET_ID, ?AMM_ASSET1_FINAL_BALANCE)))
            ((assetHolding(SECONDARY_ASSET_ID, AMM_ASSET2_BALANCE_REAL)) =>
              (assetHolding(SECONDARY_ASSET_ID, ?AMM_ASSET2_FINAL_BALANCE)))
            (assetHolding(LT_ID, _AMM_LT_BALANCE:Int))
            ...
          </assetsOptedIn>
          <boxes>
            .Bag
          </boxes>
        </account> 
      </accountsMap>
      <appCreator>
        .Map [APP_ID <- CONTRACT_CREATOR_ADDR]
      </appCreator>
      <assetCreator>
        PRIMARY_ASSET_ID   |-> ASSET_CREATOR_ADDRESS
        SECONDARY_ASSET_ID |-> ASSET_CREATOR_ADDRESS
        LT_ID              |-> CONTRACT_ACCOUNT_ADDR
      </assetCreator>
      <blocks>
        .Map => ?_
      </blocks>
      <blockheight>
        0 => ?_
      </blockheight>
      <nextAssetID>
        _NEXT_ASSET_ID:Int => ?_
      </nextAssetID>
      <nextAppID>
        _NEXT_APP_ID:Int => ?_
      </nextAppID>
      <nextTxnID>
        NEXT_TX_ID:Int => ?_
      </nextTxnID>
      <nextGroupID>
        NEXT_GROUP_ID:Int => ?_
      </nextGroupID>
      <txnIndexMap>
        .Bag => ?_
      </txnIndexMap>
    </blockchain>
    ...
  </kavm>
  requires #rangeUInt( 64, AMOUNT )
   andBool #rangeUInt( 64, SENDER_ASSET1_INITIAL_BALANCE )
   andBool #rangeUInt( 64, SENDER_ASSET2_INITIAL_BALANCE )
   andBool #rangeUInt( 64, AMM_ASSET1_BALANCE_STORED )
   andBool #rangeUInt( 64, AMM_ASSET2_BALANCE_STORED )
   andBool #rangeUInt( 64, AMM_ASSET1_BALANCE_REAL )
   andBool #rangeUInt( 64, AMM_ASSET2_BALANCE_REAL )
   andBool #rangeUInt( 64, PRIMARY_FEES_INITIAL )
   andBool #rangeUInt( 64, SECONDARY_FEES_INITIAL )
   andBool #rangeUInt( 64, MIN_EXPECTED )
   andBool #rangeUInt( 64, FEE_BPS )
   andBool #rangeUInt( 64, PACT_FEE_BPS )

   andBool getAppAddressBytes(APP_ID) ==K CONTRACT_ACCOUNT_ADDR
   andBool APP_ID >Int 0

   // Balances always start off above the minumum balance because any transaction group that ends with this being
   // violated will reject.
   andBool SENDER_BALANCE           >=Int SENDER_MIN_BALANCE
   andBool CONTRACT_ACCOUNT_BALANCE >=Int CONTRACT_ACCOUNT_MIN_BALANCE

   // Stored fees amount shouldn't overflow (should be impossible because the total amount of an asset cannot
   // exceed 2^64 - 1)
//    andBool SECONDARY_FEES_INITIAL +Int PACT_FEE_AMOUNT <Int pow64
   andBool PACT_FEE_BPS <=Int 10000

   // Restriction on the Pact fee imposed on contract creation (needed to prove product does not decrease.)
   andBool PACT_FEE_BPS <=Int FEE_BPS /Int 2

   // Asset IDs are positive integers in Algorand.
   andBool PRIMARY_ASSET_ID >Int 0
   andBool SECONDARY_ASSET_ID >Int 0

   // We are looking at a swap call, which consists of an axfer followed by an appl transaction. This can
   // occur anywhere within a larger transaction group.
   andBool AXFER_TX_ID >=Int 0
   andBool APPL_TX_ID >=Int 0
   andBool AXFER_TX_GROUP_IDX >=Int 0
   andBool APPL_TX_GROUP_IDX >=Int 0
   andBool APPL_TX_GROUP_IDX ==Int AXFER_TX_GROUP_IDX +Int 1

   // Implementation-specific requirements. Transaction IDs and groups are all unique.
   andBool NEXT_TX_ID >Int APPL_TX_ID
   andBool NEXT_TX_ID >Int AXFER_TX_ID
   andBool NEXT_GROUP_ID >Int GROUP_ID
   
   // Aliases
   // Amount of secondary asset transfered to the sender, before fee is applies (not including Pact fee)
   andBool PRIMARY_AMOUNT ==Int (AMOUNT *Int AMM_ASSET1_BALANCE_STORED) /Int (AMOUNT +Int AMM_ASSET2_BALANCE_STORED)
   // Amount taken by the Pact fee
   andBool PACT_FEE_AMOUNT ==Int (PRIMARY_AMOUNT *Int PACT_FEE_BPS) /Int 10000
   // Amount of secondary asset transfered to the sender, after fee is applies (not including Pact fee)
   andBool PRIMARY_AMOUNT_TAXED ==Int (PRIMARY_AMOUNT *Int (10000 -Int FEE_BPS)) /Int 10000

   andBool PRIMARY_ASSET_ID_TXN ==K PRIMARY_ASSET_ID
   andBool SECONDARY_ASSET_ID_TXN ==K SECONDARY_ASSET_ID
   andBool CONTRACT_ACCOUNT_ADDR_TXN ==K CONTRACT_ACCOUNT_ADDR

  ensures 
     (     
      // Reserve product does not decrease (For successful swap)
            (AMM_ASSET1_BALANCE_STORED       *Int  AMM_ASSET2_BALANCE_STORED 
      <=Int ?AMM_ASSET1_FINAL_BALANCE_STORED *Int ?AMM_ASSET2_FINAL_BALANCE_STORED)

      // Real asset balances cannot drop below tracked asset balances
      andBool ((AMM_ASSET2_BALANCE_STORED <=Int AMM_ASSET2_BALANCE_REAL) impliesBool (?AMM_ASSET2_FINAL_BALANCE_STORED <=Int ?AMM_ASSET2_FINAL_BALANCE))
      andBool ((AMM_ASSET1_BALANCE_STORED <=Int AMM_ASSET1_BALANCE_REAL) impliesBool (?AMM_ASSET1_FINAL_BALANCE_STORED <=Int ?AMM_ASSET1_FINAL_BALANCE))


      andBool ?SENDER_ASSET1_FINAL_BALANCE ==Int SENDER_ASSET1_INITIAL_BALANCE +Int PRIMARY_AMOUNT_TAXED
      andBool ?SENDER_ASSET2_FINAL_BALANCE ==Int SENDER_ASSET2_INITIAL_BALANCE -Int AMOUNT
      andBool ?AMM_ASSET1_FINAL_BALANCE ==Int AMM_ASSET1_BALANCE_REAL -Int PRIMARY_AMOUNT_TAXED
      andBool ?AMM_ASSET2_FINAL_BALANCE ==Int AMM_ASSET2_BALANCE_REAL +Int AMOUNT
      andBool ?AMM_ASSET1_FINAL_BALANCE_STORED ==Int AMM_ASSET1_BALANCE_STORED -Int PRIMARY_AMOUNT_TAXED -Int PACT_FEE_AMOUNT
      andBool ?AMM_ASSET2_FINAL_BALANCE_STORED ==Int AMM_ASSET2_BALANCE_STORED +Int AMOUNT
      andBool ?PRIMARY_FEES_FINAL ==Int PRIMARY_FEES_INITIAL +Int PACT_FEE_AMOUNT
      andBool ?SECONDARY_FEES_FINAL ==Int SECONDARY_FEES_INITIAL
    
    )
    // If transaction group execution is not successful, there will be no change to blockchain state.
    orBool ?RETURN_CODE >Int 0

// claim <k> runLemma(true orBool X:Bytes in_optedInAssets(<assetsOptedIn> Y </assetsOptedIn>)) => doneLemma(true) </k>

endmodule
