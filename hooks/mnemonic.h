#ifndef MNEMONIC_H
#define MNEMONIC_H

#include <vector>

typedef std::vector<unsigned char> bytes;

bytes sha512_256(bytes input);
#endif
