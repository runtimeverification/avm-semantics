Logic Signature Argument Representation
=======================================

```k
require "teal-types.md"

module TXN-ARGS
  imports TEAL-TYPES
  imports DOMAINS

  // Args cell
  configuration
    <args> .Map </args>  // Int |-> TValue

  // Accessor function

  syntax MaybeTValue ::= getArgument(Int) [function]
  //------------------------------------------
  rule [[ getArgument(I) => A ]]
       <args> ... I |-> A ... </args>

  rule [[ getArgument(I) => NoTValue ]]
       <args> Args </args>
    requires notBool (I in_keys(Args))
endmodule
```
