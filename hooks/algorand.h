#ifndef ALGORAND_H
#define ALGORAND_H

#include <memory>

#include <msgpack.hpp>

typedef std::vector<unsigned char> bytes;

class Address {
public:
  Address();                    // Constructs the ZERO address
  Address(std::string b32form);
  Address(bytes public_key);
  std::string as_string;
  bytes public_key;
  bool is_zero() const;
private:
  Address(std::string s, bytes with_csum);
  Address(bytes public_key, bytes with_csum);
};
inline bool operator==(const Address& lhs, const Address& rhs) {
  return lhs.as_string == rhs.as_string && lhs.public_key == rhs.public_key;
}
inline bool operator!=(const Address& lhs, const Address& rhs) {
  return !(lhs == rhs);
}
inline bool operator <(const Address& lhs, const Address& rhs ) {
  return lhs.as_string < rhs.as_string;
}

std::ostream& operator<<(std::ostream& os, const Address& addr);

#endif
