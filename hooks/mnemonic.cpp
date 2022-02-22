#include "mnemonic.h"

#include <iostream>

#include <openssl/evp.h>

#include "base.h"

// libsodium/nacl does not implement this truncated form of sha512,
// which is NOT simply the first 256 bits of the sha512 hash.
bytes sha512_256(bytes input) {
  unsigned char result[32];
  EVP_MD_CTX *ctx = EVP_MD_CTX_new();
  bool success = ctx != NULL
      && EVP_DigestInit_ex(ctx, EVP_sha512_256(), NULL) == 1
      && EVP_DigestUpdate(ctx, input.data(), input.size()) == 1
      && EVP_DigestFinal_ex(ctx, result, NULL) == 1;
  if (! success) throw std::runtime_error("openssl sha512_256 EVP_Digest runtime error");
  EVP_MD_CTX_free(ctx);
  return bytes(result, result+sizeof(result));
}
