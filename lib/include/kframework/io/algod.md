Algod Node Abstraction
======================

```k
require "../avm/teal/teal-types.md"
require "../avm/additional-fields.md"

module ALGOD
  imports ADDITIONAL-FIELDS
  imports DOMAINS

  configuration
    <algod>
      <dVersions>    0     </dVersions>  // TODO: This should be a list
      <dGenesisID>   0     </dGenesisID>
      <dGenesisHash> ""    </dGenesisHash>
    </algod>

  // Accessor function

  syntax TValue ::= getAlgodVersionInfo(VersionField) [function]
  //------------------------------------------------------------
  rule [[ getAlgodVersionInfo(Versions) => V ]]
       <dVersions> V </dVersions>

  rule [[ getAlgodVersionInfo(GenesisID) => V ]]
       <dGenesisID> V </dGenesisID>

  rule [[ getAlgodVersionInfo(GenesisHash) => V ]]
       <dGenesisHash> V </dGenesisHash>

endmodule
