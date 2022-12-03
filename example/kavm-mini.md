```k
module KAVM-MINI
  imports STRING
  imports BYTES
  imports INT
  imports K-EQUAL
  imports BOOL

  configuration
    <kavm>
      <k> $PGM:K </k>
      <stack> .TStack </stack>
      <pc> 0 </pc>
      <program> .Map </program>
      <currentTx> "" </currentTx>
      <transactions>
        <transaction multiplicity="*" type="Map">
          <txID> "" </txID>
          <pgm> .TealProgram </pgm>
          <args> .BytesList </args>
          <foreignAccounts> .BytesList </foreignAccounts>
        </transaction>
      </transactions>
      <accounts>
        <account multiplicity="*" type="Map">
          <address> .Bytes </address>
          <balance> 0 </balance>
        </account>
      </accounts>
    </kavm>

  syntax KItem ::= #executeTxn(String)

  syntax KItem ::= #loadPgm(TealProgram)

  syntax KItem ::= #fetchOpcode()

  syntax KItem ::= #incrementPC()

  syntax Int ::= "MAX_UINT_64" [macro]

  rule MAX_UINT_64 => 18446744073709551615

  syntax BytesList ::= Bytes BytesList
                     | ".BytesList"
  syntax Bytes ::= BytesList "[" Int "]" [function]

  syntax TValue ::= Int | Bytes
  syntax TStack ::= TValue ":" TStack
                  | ".TStack"


  syntax TealCommand ::= "pay"
                       | "+"
                       | "btoi"
                       | "int" Int
                       | "bytes" Bytes
                       | "arg" Int
                       | "account" Int

  syntax TealProgram ::= TealCommand TealProgram
                       | ".TealProgram"

  rule <k> #executeTxn(TX_ID) => #loadPgm(PGM) ~> #fetchOpcode() ... </k>
       <currentTx> _ => TX_ID </currentTx>
       <pc> _ => 0 </pc>
       <program> _ => .Map </program>
       <stack> _ => .TStack </stack>
       <transaction>
         <txID> TX_ID </txID>
         <pgm> PGM </pgm>
         ...
       </transaction>

  rule <k> #loadPgm(TC:TealCommand TP:TealProgram) => #loadPgm(TP) ... </k>
       <program> PROGRAM => PROGRAM [size(PROGRAM) <- TC] </program>

  rule <k> #loadPgm(.TealProgram) => . ... </k>

  rule <k> #fetchOpcode() => PGM[PC] ~> #incrementPC() ~> #fetchOpcode() ... </k>
       <pc> PC </pc>
       <program> PGM </program>
    requires PC <Int size(PGM)

  rule <k> #fetchOpcode() => . ... </k>
       <pc> PC </pc>
       <program> PGM </program>
    requires PC >=Int size(PGM)

  rule <k> #incrementPC() => . ... </k>
       <pc> PC => PC +Int 1 </pc>

  rule <k> pay => . ... </k>
       <stack> AMOUNT:Int : TO:Bytes : FROM:Bytes : XS:TStack => XS </stack>
       <account>
         <address> FROM </address>
         <balance> FROM_BAL => FROM_BAL -Int AMOUNT </balance>
       </account>
       <account>
         <address> TO </address>
         <balance> TO_BAL => TO_BAL +Int AMOUNT </balance>
       </account>
    requires FROM_BAL >=Int AMOUNT

  rule <k> + => . ... </k>
       <stack> I2:Int : I1:Int : XS:TStack => (I1 +Int I2) : XS </stack>
    requires I1 +Int I2 <=Int MAX_UINT_64

  rule <k> btoi => . ... </k>
       <stack> B:Bytes : XS:TStack => Bytes2Int(B, BE, Unsigned) : XS </stack>

  rule <k> int I => . ... </k>
       <stack> XS:TStack => I : XS </stack>

  rule <k> bytes B => . ... </k>
       <stack> XS:TStack => B : XS </stack>

  rule <k> arg I => . ... </k>
       <stack> XS:TStack => ARGS[I] : XS </stack>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <args> ARGS </args>
         ...
       </transaction>

  rule <k> account I => . ... </k>
       <stack> XS:TStack => ACCTS[I] : XS </stack>
       <currentTx> TX_ID </currentTx>
       <transaction>
         <txID> TX_ID </txID>
         <foreignAccounts> ACCTS </foreignAccounts>
         ...
       </transaction>

  rule (B:Bytes _:BytesList) [ 0 ] => B
  rule (_:Bytes BL:BytesList) [ N:Int ] => BL [ N -Int 1 ]
    requires N >Int 0
  
endmodule
```
