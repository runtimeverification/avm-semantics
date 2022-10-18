module OPCODES-V5-SPEC
  imports VERIFICATION

// ecdsa_verify 	5 	x 	1700
// ecdsa_pk_decompress 	5 	x 	650
// ecdsa_pk_recover 	5 	x 	2000

// loads 	5 	heavy_check_mark 	1
claim <k> loads => . </k>
      <stack> 5 : XS => 8 : XS </stack>
      <scratch> 5 |-> 8 </scratch>

// stores 	5 	heavy_check_mark 	1
claim <k> stores => . </k>
      <stack> 8 : 5 : XS => XS </stack>
      <stacksize> S => S -Int 2 </stacksize>
      <scratch> .Map => (5 |-> 8) </scratch>

// cover 	5 	heavy_check_mark 	1
claim <k> cover 3 => . </k>
      <stack> 123 : 0 : 0 : 0 : XS => 0 : 0 : 0 : 123 : XS </stack>
      <stacksize> S </stacksize>
  requires S >=Int 4

claim <k> cover 3 => panic(STACK_UNDERFLOW) </k>
      <stack> 123 : 0 : 0 : .TStack </stack>
      <stacksize> 3 </stacksize>

// uncover 	5 	heavy_check_mark 	1
claim <k> uncover 3 => . </k>
      <stack> 0 : 0 : 0 : 123 : XS => 123 : 0 : 0 : 0 : XS </stack>
      <stacksize> S </stacksize>
  requires S >=Int 4

claim <k> uncover 3 => panic(STACK_UNDERFLOW) </k>
      <stack> 123 : 0 : 0 : .TStack </stack>
      <stacksize> 3 </stacksize>

// extract 	5 	heavy_check_mark 	1
claim <k> extract 2 3 => . </k>
      <stack> b"abcdefg" : XS => b"cde" : XS </stack>

// extract3 	5 	heavy_check_mark 	1
claim <k> extract3 => . </k>
      <stack> 3 : 2 : b"abcdefg" : XS => b"cde" : XS </stack>
      <stacksize> S => S -Int 2 </stacksize>

// extract_uint16 	5 	heavy_check_mark 	1
claim <k> extract_uint16 => . </k>
      <stack> 2 : b"\xff\xff\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// extract_uint32 	5 	heavy_check_mark 	1
claim <k> extract_uint32 => . </k>
      <stack> 2 : b"\xff\xff\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// extract_uint64 	5 	heavy_check_mark 	1
claim <k> extract_uint64 => . </k>
      <stack> 2 : b"\xff\xff\x00\x00\x00\x00\x00\x00\x00\x03\xff" : XS => 3 : XS </stack>
      <stacksize> S => S -Int 1 </stacksize>

// app_params_get 	5 	x 	1
// log 	5 	heavy_check_mark 	1
// itxn_begin 	5 	heavy_check_mark 	1
// itxn_field 	5 	heavy_check_mark 	1
// itxn_submit 	5 	heavy_check_mark 	1
// itxn 	5 	heavy_check_mark 	1
// itxna 	5 	heavy_check_mark 	1
// txnas 	5 	heavy_check_mark 	1
// gtxnas 	5 	heavy_check_mark 	1
// gtxnsas 	5 	heavy_check_mark 	1
// args 	5 	heavy_check_mark 	1    

endmodule
