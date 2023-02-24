module AXFER-SPEC
  imports VERIFICATION

  claim [main]:
  <kavm>
    <k>
      #evalTxGroup( ) => .K
    </k>
    <returncode>
      4 => 0
    </returncode>
    <returnstatus>
      "" => ?_
    </returnstatus>
    <transactions>
      (<transaction>
        <txID> "0" </txID>
        <txHeader>
          <groupID> "0" </groupID>
          <groupIdx> 0 </groupIdx>
          <sender> FAUCET_ADDRESS </sender>
          <txType> "axfer" </txType>
          <typeEnum> @axfer </typeEnum>
          <rekeyTo> PARAM_ZERO_ADDR </rekeyTo>
          <fee> 0 </fee>
          _
        </txHeader>
        <txnTypeSpecificFields>
          <assetTransferTxFields>
            <xferAsset>     PRIMARY_ASSET_ID </xferAsset>
            <assetAmount>   PRIMARY_TRANSFER_AMOUNT </assetAmount>
            <assetReceiver> CONTRACT_ADDRESS </assetReceiver>
            <assetASender>  PARAM_ZERO_ADDR </assetASender>
            <assetCloseTo>  PARAM_ZERO_ADDR </assetCloseTo>
          </assetTransferTxFields>
        </txnTypeSpecificFields>
        <resume> false </resume>
        _
      </transaction>) => ?_
    </transactions>
    <avmExecution>
      <currentTx>
        "0" => ?_
      </currentTx>
      <deque> ListItem("0") => ?_ </deque>
      <dequeIndexSet> SetItem("0") </dequeIndexSet>
      <currentTxnExecution>
        <globals> _ => ?_ </globals>
        <teal>    _ => ?_  </teal>
        <effects> .List </effects>
        <lastTxnGroupID> _ => ?_ </lastTxnGroupID>
      </currentTxnExecution>
      <innerTransactions> .List </innerTransactions>
      <activeApps> .Set </activeApps>
      <touchedAccounts> .List => ?_ </touchedAccounts>
    </avmExecution>
    <blockchain>
      <accountsMap>
        <account>
          <address> FAUCET_ADDRESS </address>
          <balance> FAUCET_BALANCE => ?FAUCET_BALANCE_POST </balance>
          <minBalance> FAUCET_MIN_BALANCE </minBalance>
          <assetsCreated>
            asset(PRIMARY_ASSET_ID, 18446744073709551615, 6, FAUCET_ADDRESS)
            asset(SECONDARY_ASSET_ID, 18446744073709551615, 6, FAUCET_ADDRESS)
          </assetsCreated>
          <assetsOptedIn>
            (assetHolding(PRIMARY_ASSET_ID, FAUCET_PRIMARY_BALANCE) => assetHolding(PRIMARY_ASSET_ID, ?FAUCET_PRIMARY_BALANCE_POST))
            (assetHolding(SECONDARY_ASSET_ID, FAUCET_SECONDARY_BALANCE) => assetHolding(SECONDARY_ASSET_ID, ?FAUCET_SECONDARY_BALANCE_POST))
          </assetsOptedIn>
          _
        </account>
        <account>
          <address> TREASURY_ADDRESS </address>
          <balance> TREASURY_BALANCE </balance>
          <minBalance> TREASURY_MIN_BALANCE </minBalance>
          <appsCreated>
            <app>
              <appID>
                1
              </appID>
              <approvalPgmSrc>
                cpmmApprovalMacro(PRIMARY_ASSET_ID, SECONDARY_ASSET_ID, TREASURY_ADDRESS_LITERAL, FEE_BPS, PACT_FEE_BPS)
              </approvalPgmSrc>
              <clearStatePgmSrc>
                #pragma version 6 int 1
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
                  b"ADMIN" |-> TREASURY_ADDRESS
                  b"CONFIG" |-> b"\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x01,"
                  b"CONTRACT_NAME" |-> b"PACT AMM"
                  b"TREASURY" |-> TREASURY_ADDRESS
                </globalBytes>
                <globalInts>
                  b"A" |-> 0
                  b"B" |-> 0
                  b"FEE_BPS" |-> 300
                  b"L" |-> 0
                  b"LTID" |-> 3
                  b"PACT_FEE_BPS" |-> 10
                  b"PRIMARY_FEES" |-> 0
                  b"SECONDARY_FEES" |-> 0
                  b"VERSION" |-> 2
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
          _
        </account>
        <account>
          <address>
            CONTRACT_ADDRESS
          </address>
          <balance>
            CONTRACT_BALANCE => ?CONTRACT_BALANCE_POST
          </balance>
          <minBalance>
            CONTRACT_MIN_BALANCE
          </minBalance>
          <assetsCreated>
            asset(LT_ASSET_ID, 18446744073709551615, 6, CONTRACT_ADDRESS)
          </assetsCreated>
          <assetsOptedIn>
            (assetHolding(PRIMARY_ASSET_ID, CONTRACT_PRIMARY_BALANCE) => assetHolding(PRIMARY_ASSET_ID, ?CONTRACT_PRIMARY_BALANCE_POST))
            (assetHolding(SECONDARY_ASSET_ID, CONTRACT_SECONDARY_BALANCE) => assetHolding(SECONDARY_ASSET_ID, ?CONTRACT_SECONDARY_BALANCE_POST))
            assetHolding(LT_ASSET_ID, 18446744073709551615)
          </assetsOptedIn>
          _
        </account>
      </accountsMap>
      <appCreator>
        1 |-> TREASURY_ADDRESS
      </appCreator>
      <assetCreator>
        PRIMARY_ASSET_ID   |-> FAUCET_ADDRESS
        SECONDARY_ASSET_ID |-> FAUCET_ADDRESS
        LT_ASSET_ID        |-> CONTRACT_ADDRESS
      </assetCreator>
      <nextAssetID>
        4
      </nextAssetID>
      <nextAppID>
        2
      </nextAppID>
      <nextTxnID>
        1
      </nextTxnID>
      <nextGroupID>
        1
      </nextGroupID>
      <txnIndexMap>
        .Bag => ?_
      </txnIndexMap>
      _
    </blockchain>
    _
  </kavm>
  requires true
   // parameters for cpmmApprovalMacro to instantiate the contract's TEAL
   andBool FEE_BPS            ==Int 300
   andBool PACT_FEE_BPS       ==Int 10
   // note that the three asset ids involved are symbolic, but must obey these constraitns
   andBool SECONDARY_ASSET_ID >Int  PRIMARY_ASSET_ID
   andBool LT_ASSET_ID        >Int  SECONDARY_ASSET_ID

   // faucet account parameters
   andBool FAUCET_ADDRESS            ==K b";9E%\x1b\x0f\xa5W\xfak\xd2PY\xbam1\xcaJ<\x1b%v\x0b\xe9H_x\xc3GV\xb8~"
   andBool #range(PARAM_MIN_BALANCE  <= FAUCET_MIN_BALANCE     <= pow64)
   andBool #range(FAUCET_MIN_BALANCE <= FAUCET_BALANCE         <= pow64)
   andBool #range(0                  <= FAUCET_PRIMARY_BALANCE <= pow64)

   // contract account parameters
   andBool CONTRACT_ADDRESS            ==K b"\xb0\xa5\xe9\xd5\xe9\x88d\x08\x9dm\xd6\xf5\xe5\xc6\x9d\x0e*\x9c\xd1H\xd5S\xdd\x88\x16V0q\x93\x9d\xeeL"
   andBool #range(PARAM_MIN_BALANCE    <= CONTRACT_MIN_BALANCE     <= pow64)
   andBool #range(CONTRACT_MIN_BALANCE <= CONTRACT_BALANCE         <= pow64)
   andBool #range(0                    <= CONTRACT_PRIMARY_BALANCE <= pow64)

   // treasury (and also deployer) account parameters
   andBool TREASURY_ADDRESS            ==K b"\x13NaRe\xeb{\xd8\x8d0\xe0NP\xdc\xc3\xcf\xe3}\x01\xe6\x14/\xdc\xdd\xe9\x90\x01\xbe4#9U"
   andBool TREASURY_ADDRESS_LITERAL    ==K String2TealAddress("CNHGCUTF5N55RDJQ4BHFBXGDZ7RX2APGCQX5ZXPJSAA34NBDHFKRNHDXKY")
   andBool #range(PARAM_MIN_BALANCE    <= TREASURY_MIN_BALANCE <= pow64)
   andBool #range(TREASURY_MIN_BALANCE <= TREASURY_BALANCE     <= pow64)

   // the sum of balances of all participants must not exceed total Algo supply
   andBool #range(0 <= FAUCET_BALANCE +Int CONTRACT_BALANCE +Int TREASURY_BALANCE <= pow64)

   // constraints on symbolic asset transfer amount
   andBool PRIMARY_TRANSFER_AMOUNT >=Int 0
   andBool PRIMARY_TRANSFER_AMOUNT <Int FAUCET_PRIMARY_BALANCE

  ensures true
   andBool ?FAUCET_BALANCE_POST         ==Int FAUCET_BALANCE
   andBool ?FAUCET_PRIMARY_BALANCE_POST ==Int FAUCET_PRIMARY_BALANCE -Int PRIMARY_TRANSFER_AMOUNT
   andBool ?FAUCET_SECONDARY_BALANCE_POST ==Int FAUCET_SECONDARY_BALANCE

   andBool ?CONTRACT_BALANCE_POST         ==Int CONTRACT_BALANCE
   andBool ?CONTRACT_PRIMARY_BALANCE_POST ==Int CONTRACT_PRIMARY_BALANCE +Int PRIMARY_TRANSFER_AMOUNT
   andBool ?CONTRACT_SECONDARY_BALANCE_POST ==Int CONTRACT_SECONDARY_BALANCE

endmodule
