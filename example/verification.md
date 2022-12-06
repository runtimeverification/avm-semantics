```k
requires "kavm-mini.md"

module VERIFICATION
  imports KAVM-MINI

  rule Bytes2Int(Int2Bytes(I:Int, ENDIANNESS, SIGNEDNESS), ENDIANNESS, SIGNEDNESS) => I [simplification]

endmodule
```
