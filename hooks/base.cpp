#include "base.h"


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
