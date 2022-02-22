#ifndef BASE_H
#define BASE_H

#include <string>
#include <vector>

typedef std::vector<unsigned char> bytes;

std::string b32_encode(const bytes& in);
bytes b32_decode(const std::string& in);

std::vector<uint16_t> b2048_encode(const bytes& in);
bytes b2048_decode(const std::vector<uint16_t> &in);

#endif
