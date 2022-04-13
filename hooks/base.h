#ifndef BASE_H
#define BASE_H

#include <string>
#include <vector>

typedef std::vector<unsigned char> bytes;

std::string b32_encode(const bytes& in);
bytes b32_decode(const std::string& in);

bool uses_b32_alphabet(const std::string& in);

#endif
