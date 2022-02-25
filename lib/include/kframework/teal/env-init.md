```k
requires "teal-execution.md"
```

This module is a hard-coded TEAL environment used to test the TEAL interpreter
definition. Eventually, it will be replaced by a custom environment loader that
reads in the environment definition from input files.

```k
module TEAL-ENVIRONMENT-INITIALIZATION
  imports TEAL-INTERPRETER-STATE

  // Global Field Initializer
  // ------------------------
  rule <k> initGlobals => . ... </k>
    <globals>
      <groupSize>            _ => 3 </groupSize>
      <globalRound>          _ => 6 </globalRound>
      <latestTimestamp>      _ => 50  </latestTimestamp>
      <currentApplicationID> _ => 0 </currentApplicationID>
      <currentApplicationAddress> _ => 0 </currentApplicationAddress>
    </globals>


  // Transaction Group Initializer
  // -----------------------------
  rule <k> initTxnGroup => .K ... </k>
       <txGroup>
         <txGroupID> _ => 0 </txGroupID>
         <currentTx> _ => 0 </currentTx>
         <transactions> .Bag => (
           <transaction>
             <txID> 0 </txID>
             <txHeader>
               <fee>         500  </fee>
               <firstValid>  10 </firstValid>
               <lastValid>   11 </lastValid>
               <genesisHash> "0" </genesisHash>
               <sender>      DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </sender>
               <txType>      "pay" </txType>
               <typeEnum>    @ pay </typeEnum>
               <group>       0 </group>
               <genesisID>   "0" </genesisID>
               <lease>       "" </lease>
               <note>        "" </note>
               <rekeyTo>     getGlobalField(ZeroAddress) </rekeyTo>
             </txHeader>
             <payTxFields>
               <receiver>         DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE") </receiver>
               <amount>           50000 </amount>
               <closeRemainderTo> getGlobalField(ZeroAddress) </closeRemainderTo>
             </payTxFields>
           </transaction>
           <transaction>
             <txID> 1 </txID>
             <txHeader>
               <fee>         2000  </fee>
               <firstValid>  11 </firstValid>
               <lastValid>   12 </lastValid>
               <genesisHash> "0" </genesisHash>
               <sender>      DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE") </sender>
               <txType>      "pay" </txType>
               <typeEnum>    @ pay </typeEnum>
               <group>       1 </group>
               <genesisID>   "0" </genesisID>
               <lease>       "" </lease>
               <note>        "" </note>
               <rekeyTo>     getGlobalField(ZeroAddress) </rekeyTo>
             </txHeader>
             <payTxFields>
               <receiver>         DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </receiver>
               <amount>           50005 </amount>
               <closeRemainderTo> getGlobalField(ZeroAddress) </closeRemainderTo>
             </payTxFields>
           </transaction>
           <transaction>
             <txID> 2 </txID>
             <txHeader>
               <fee>         500  </fee>
               <firstValid>  10 </firstValid>
               <lastValid>   11 </lastValid>
               <genesisHash> "0" </genesisHash>
               <sender>      DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </sender>
               <txType>      "appl" </txType>
               <typeEnum>    @ appl </typeEnum>
               <group>       2 </group>
               <genesisID>   "0" </genesisID>
               <lease>       "" </lease>
               <note>        "" </note>
               <rekeyTo>     getGlobalField(ZeroAddress) </rekeyTo>
             </txHeader>
             <payTxFields>
               <receiver> NoTValue </receiver>
               <amount>   NoTValue </amount>
               <closeRemainderTo> NoTValue </closeRemainderTo>
             </payTxFields>
             <appCallTxFields>
               <applicationID>     42 </applicationID>
               <onCompletion>      0 </onCompletion>
               <accounts>
                 DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY")
                 DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE")
               </accounts>
               <approvalProgram>   "" </approvalProgram>
               <clearStateProgram> "" </clearStateProgram>
               <applicationArgs>
                 Int2Bytes(39, BE, Unsigned)
                 Int2Bytes(100, BE, Unsigned)
                 Int2Bytes(0, BE, Unsigned)
                 Int2Bytes(0, BE, Unsigned)
                 Int2Bytes(10000000000, BE, Unsigned)
                 normalize("USD")
                 Int2Bytes(4, BE, Unsigned)
                 Int2Bytes(50, BE, Unsigned)
               </applicationArgs>
               <foreignApps>       "" </foreignApps>
               <foreignAssets>     "" </foreignAssets>
               <globalStateSchema>
                 <globalNui> 0 </globalNui>
                 <globalNbs> 0 </globalNbs>
               </globalStateSchema>
               <localStateSchema>
                 <localNui> 0 </localNui>
                 <localNbs> 0 </localNbs>
               </localStateSchema>
             </appCallTxFields>
             <keyRegTxFields>
               <votePk>           NoTValue </votePk>
               <selectionPK>      NoTValue </selectionPK>
               <voteFirst>        NoTValue </voteFirst>
               <voteLast>         NoTValue </voteLast>
               <voteKeyDilution>  NoTValue </voteKeyDilution>
               <nonparticipation> NoTValue </nonparticipation>
             </keyRegTxFields>
             <assetConfigTxFields>
               <configAsset> NoTValue </configAsset>
               <assetParams>
                 <configTotal>         NoTValue </configTotal>
                 <configDecimals>      NoTValue </configDecimals>
                 <configDefaultFrozen> NoTValue </configDefaultFrozen>
                 <configUnitName>      NoTValue </configUnitName>
                 <configAssetName>     NoTValue </configAssetName>
                 <configAssetURL>      NoTValue </configAssetURL>
                 <configMetaDataHash>  NoTValue </configMetaDataHash>
                 <configManagerAddr>   NoTValue </configManagerAddr>
                 <configReserveAddr>   NoTValue </configReserveAddr>
                 <configFreezeAddr>    NoTValue </configFreezeAddr>
                 <configClawbackAddr>  NoTValue </configClawbackAddr>
               </assetParams>
             </assetConfigTxFields>
             <assetTransferTxFields>
               <xferAsset>     NoTValue </xferAsset>
               <assetAmount>   NoTValue </assetAmount>
               <assetReceiver> NoTValue </assetReceiver>
               <assetASender>  NoTValue </assetASender>
               <assetCloseTo>  NoTValue </assetCloseTo>
             </assetTransferTxFields>
             <assetFreezeTxFields>
               <freezeAccount> NoTValue </freezeAccount>
               <freezeAsset>   NoTValue </freezeAsset>
               <assetFrozen>   NoTValue </assetFrozen>
             </assetFreezeTxFields>
           </transaction>
           <transaction>
             <txID> 3 </txID>
             <txHeader>
               <fee>         500  </fee>
               <firstValid>  10 </firstValid>
               <lastValid>   11 </lastValid>
               <genesisHash> "0" </genesisHash>
               <sender>      DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </sender>
               <txType>      "appl" </txType>
               <typeEnum>    @ appl </typeEnum>
               <group>       3 </group>
               <genesisID>   "0" </genesisID>
               <lease>       "" </lease>
               <note>        "" </note>
               <rekeyTo>     getGlobalField(ZeroAddress) </rekeyTo>
             </txHeader>
             <appCallTxFields>
               <applicationID>     0 </applicationID>
               <onCompletion>      0 </onCompletion>
               <accounts>
                 DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY")
                 DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE")
               </accounts>
               <approvalProgram>   "" </approvalProgram>
               <clearStateProgram> "" </clearStateProgram>
               <applicationArgs>
                 Int2Bytes(39, BE, Unsigned)
                 Int2Bytes(100, BE, Unsigned)
                 Int2Bytes(0, BE, Unsigned)
                 Int2Bytes(0, BE, Unsigned)
                 Int2Bytes(10000000000, BE, Unsigned)
                 normalize("USD")
                 Int2Bytes(4, BE, Unsigned)
                 Int2Bytes(50, BE, Unsigned)
               </applicationArgs>
               <foreignApps>       "" </foreignApps>
               <foreignAssets>     "" </foreignAssets>
               <globalStateSchema>
                 <globalNui> 0 </globalNui>
                 <globalNbs> 0 </globalNbs>
               </globalStateSchema>
               <localStateSchema>
                 <localNui> 0 </localNui>
                 <localNbs> 0 </localNbs>
               </localStateSchema>
             </appCallTxFields>
           </transaction>
         )
         </transactions>
       </txGroup>

  // Logic Signature Argument Initializer
  // ------------------------------------
  rule <k> initArgs => . ... </k>
       <args> _ => (
         0 |-> 0 // base32 {23232323232323}:>B32Encoded
         1 |-> DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY")
       )
       </args>

  // Blockchain Environment Initializer
  // ----------------------------------
  rule <k> initBlockchain => .K ... </k>
    <blockchain>
      <accountsMap>
        _ => (
        <account>
          <address> DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </address>
          <balance> 1500000   </balance>
          <status>  0   </status>
          <round>   1   </round>
          <preRewards> 1000 </preRewards>
          <rewards> 25000 </rewards>
          <key>   DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </key>
          <appsCreated>
            <app>
              <appID>         0 </appID>
              <approvalPgm>   normalize("This is a dummy string") </approvalPgm>
              <clearStatePgm> normalize("This is another dummy string") </clearStatePgm>
              <globalState>
                <globalInts>  15 </globalInts>
                <globalBytes> 20 </globalBytes>
                <globalStorage> 0 |-> 100  1 |-> 200 </globalStorage>
              </globalState>
              <localState>
                <localInts>  5 </localInts>
                <localBytes> 10 </localBytes>
              </localState>
            </app>
          </appsCreated>
          <appsOptedIn>
            <optInApp>
              <optInAppID> 0 </optInAppID>
              <localStorage> .Map </localStorage>
            </optInApp>
          </appsOptedIn>
          <assetsCreated> .Bag </assetsCreated>
          <assetsOptedIn>
            <optInAsset>
              <optInAssetID> 39 </optInAssetID>
              <optInAssetBalance> 100 </optInAssetBalance>
              <optInAssetFrozen>  0 </optInAssetFrozen>
            </optInAsset>
          </assetsOptedIn>
        </account>
        <account>
          <address> DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE") </address>
          <balance> 3000000   </balance>
          <status>  0   </status>
          <round>   1   </round>
          <preRewards> 100 </preRewards>
          <rewards> 35000 </rewards>
          <key>   DecodeAddressString("STF6TH6PKINM4CDIQHNSC7QEA4DM5OJKKSACAPWGTG776NWSQOMAYVGOQE") </key>
          <appsCreated>
            <app>
              <appID>         1 </appID>
              <approvalPgm>   normalize("This is yet another dummy string") </approvalPgm>
              <clearStatePgm> normalize("one more") </clearStatePgm>
              <globalState>
                <globalInts>  15 </globalInts>
                <globalBytes> 20 </globalBytes>
                <globalStorage> 10 |-> 1000  20 |-> 200 </globalStorage>
              </globalState>
              <localState>
                <localInts>  5 </localInts>
                <localBytes> 10 </localBytes>
              </localState>
            </app>
          </appsCreated>
          <appsOptedIn>
            <optInApp>
              <optInAppID> 1 </optInAppID>
              <localStorage> .Map </localStorage>
            </optInApp>
            <optInApp>
              <optInAppID> 0 </optInAppID>
              <localStorage> .Map </localStorage>
            </optInApp>
          </appsOptedIn>
          <assetsCreated>
            <asset>
              <assetID>       39 </assetID>
              <assetName>     normalize("Dollar") </assetName>
              <assetUnitName>      normalize("USD") </assetUnitName>
              <assetTotal>         10000000000 </assetTotal>
              <assetDecimals>      2 </assetDecimals>
              <assetDefaultFrozen> 0 </assetDefaultFrozen>
              <assetURL>           NoTValue </assetURL>
              <assetMetaDataHash>  NoTValue </assetMetaDataHash>
              <assetManagerAddr>   DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY") </assetManagerAddr>
              <assetReserveAddr>   NoTValue </assetReserveAddr>
              <assetFreezeAddr>    NoTValue </assetFreezeAddr>
              <assetClawbackAddr>  NoTValue </assetClawbackAddr>
            </asset>
          </assetsCreated>
          <assetsOptedIn>
            <optInAsset>
              <optInAssetID> 39 </optInAssetID>
              <optInAssetBalance> 100 </optInAssetBalance>
              <optInAssetFrozen>  0 </optInAssetFrozen>
            </optInAsset>
          </assetsOptedIn>
        </account>
        )
      </accountsMap>
      <appCreator> M => M[0 <- DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY")]  </appCreator>
      <assetCreator> M => M[39 <- DecodeAddressString("6Z3C3LDVWGMX23BMSYMANACQOSINPFIRF77H7N3AWJZYV6OH6GWTJKVMXY")]  </assetCreator>
      <blocks>       .Map </blocks>
      <blockheight> 0 </blockheight>
    </blockchain>

endmodule
```
