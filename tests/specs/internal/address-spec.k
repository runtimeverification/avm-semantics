module ADDRESS-SPEC
    imports VERIFICATION

    claim [address.empty.invalid]:
      <k> runLemma(IsAddressValid(""))
       => doneLemma(false)
      </k>

    claim [address.zero.valid]:
      <k> runLemma(IsAddressValid("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ"))
       => doneLemma(true)
    </k>

    // claim [padLeftBytes.correct]:
    //       <k> runLemma(lengthBytes(padLeftBytes(B, 32, 0)))
    //        => doneLemma(?X)
    //       </k>
    //   requires lengthBytes(B) ==Int 32
    //   ensures ?X ==Int 33

    // claim [padLeftBytes.correct]:
    //       <k> runLemma(padLeftBytes(B, 32, 0))
    //        => doneLemma(B)
    //       </k>
    //   requires B ==K b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    // claim [padLeftBytes.correct]:
    //       <k> runLemma(padLeftBytes(B, 32, 0))
    //        => doneLemma(B)
    //       </k>
    //   requires lengthBytes(B) ==Int 32

endmodule
