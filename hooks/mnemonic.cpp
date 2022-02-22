#include "mnemonic.h"

#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <stdexcept>
#include <cassert>

#include <openssl/evp.h>

#include "base.h"

extern std::map<std::string, int> word_map;
extern std::vector<std::string> word_vec;

std::map<std::string, int> make_word_map(std::string s) {
  std::map<std::string, int> map;

  auto iss = std::istringstream{s};
  std::string word;

  int i = 0;
  while (iss >> word) {
    map[word] = i;
    i++;
  }

  return map;
}

std::vector<std::string> make_word_vector(std::string s) {
  std::vector<std::string> vec;

  auto iss = std::istringstream{s};
  std::string word;

  while (iss >> word) {
    vec.push_back(word);
  }

  return vec;
}

int word_lookup(std::string word) {
  auto entry = word_map.find(word);
  if (entry == word_map.end())
    throw std::invalid_argument(word.c_str());
  return entry->second;
}

uint16_t checksum(bytes b) {
  auto hash = sha512_256(b);
  auto ints = b2048_encode(bytes{hash.begin(), hash.begin()+2});
  return ints[0];
}

std::string mnemonic_from_seed(bytes seed) {
  std::string mnemonic;
  for (const int i : b2048_encode(seed)) {
    mnemonic.append(word_vec[i]+" ");
  }
  mnemonic.append(word_vec[checksum(seed)]);
  return mnemonic;
}




bytes seed_from_mnemonic(std::string mnemonic) {
  std::vector<std::string> words = make_word_vector(mnemonic);
  auto checkword = words.back();
  words.pop_back();
  if (words.size() != 24)
    throw std::invalid_argument(std::to_string(words.size()+1) + " words");
  auto checkval = word_lookup(checkword);
  bytes seed;
  // this part is base conversion, 11 to 8. see base.cpp
  unsigned val = 0;
  int bits = 0;
  for (const auto& word : words) {
    val |= word_lookup(word) << bits;
    bits += 11;
    while (bits >= 8) {
      seed.push_back(val & 0xFF);
      val >>= 8;
      bits -= 8;
    }
  }
  if (bits > 0)
    seed.push_back(val & 0xFF);

  assert(!*(seed.end()-1));      // last byte is supposed to be zero
  seed.pop_back();               // and unneeded
  auto check = checksum(seed);
  if (check != checkval) {
    throw std::invalid_argument(word_vec[check] + " != " + word_vec[checkval]);
  }
  return seed;
}

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

std::vector<std::string> word_vec = make_word_vector(english);
