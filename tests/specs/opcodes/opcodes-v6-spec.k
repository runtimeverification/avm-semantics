module OPCODES-V6-SPEC
  imports VERIFICATION

// acct_params_get f 	6 	not implemented 	1
// bsqrt 	6 	not implemented 	40
// divw 	6 	not implemented 	1
// itxn_next 	6 	implemented, not tested 	1
claim <k> itxn_next => . </k>

// gitxn t f 	6 	implemented, not tested 	1
// gitxna t f i 	6 	implemented, not tested 	1
// gloadss 	6 	implemented, not tested 	1
// itxnas f 	6 	not implemented 	1
// gitxnas t f 	6 	not implemented 	1 

endmodule
