#include "base.h"


#define B64DIGITS "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

std::string b64_encode(const bytes& in, bool padded) {
  std::string out;
  out.reserve(4 + (4*in.size()/3));

  int val = 0;
  int bits = 0;
  for (auto c : in) {
    val = (val << 8) + c;
    bits += 8;
    while (bits >= 6) {
      out.push_back(B64DIGITS[(val>>(bits-6))&0x3F]);
      bits -= 6;
    }
  }
  if (bits > 0)
    out.push_back(B64DIGITS[(val<<(6-bits))&0x3F]);
  while (padded && out.size() % 4)
    out.push_back('=');
  return out;
}

std::vector<int> decode64_digits() {
  std::vector<int> table(256, -1);
  for (int i=0; i<64; i++)
    table[B64DIGITS[i]] = i;
  return table;
}


bytes b64_decode(const std::string &in) {
  static std::vector<int> dd = decode64_digits();

  bytes out;
  out.reserve(3*in.size()/4);

  int val = 0;
  int bits = 0;
  for (auto c : in) {
    if (dd[c] == -1)             // bail on any non-b64 digit
      break;
    val = (val << 6) + dd[c];
    bits += 6;
    if (bits >= 8) {
      out.push_back(char((val>>(bits-8))&0xFF));
      bits -= 8;
    }
  }
  return out;
}

// Surely I should write an implementation that avoids the almost
// cutnpaste job here.


#define B32DIGITS "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

std::string b32_encode(const bytes& in) {
  std::string out;
  out.reserve(8 + (8*in.size()/5));

  int val = 0;
  int bits = 0;
  for (auto c : in) {
    val = (val << 8) + c;
    bits += 8;
    while (bits >= 5) {
      out.push_back(B32DIGITS[(val>>(bits-5))&0x1F]);
      bits -= 5;
    }
  }
  if (bits > 0)
    out.push_back(B32DIGITS[(val<<(5-bits))&0x1F]);
  return out;
}

std::vector<int> decode32_digits() {
  std::vector<int> table(256, -1);
  for (int i=0; i<32; i++)
    table[B32DIGITS[i]] = i;
  return table;
}


bytes b32_decode(const std::string &in) {
  static std::vector<int> dd = decode32_digits();

  bytes out;
  out.reserve(5*in.size()/8);

  int val = 0;
  int bits = 0;
  for (auto c : in) {
    if (dd[c] == -1)             // bail on any non-b32 digit
      break;
    val = (val << 5) + dd[c];
    bits += 5;
    if (bits >= 8) {
      out.push_back(char((val>>(bits-8))&0xFF));
      bits -= 8;
    }
  }
  return out;
}

bool uses_b32_alphabet(const std::string& in) {
  static std::vector<int> dd = decode32_digits();
  for (auto c : in) {
    if (dd[c] == -1) return false;
  }
  return true;
}
