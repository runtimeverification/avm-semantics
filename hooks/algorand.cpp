#include "algorand.h"
#include "base.h"
#include "mnemonic.h"

Address::Address() :
  Address("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ") {
}

// Address::Address(const Address& rhs) :
//   as_string(rhs.as_string),
//   public_key(rhs.public_key) {
// }

bool
Address::is_zero() const {
  return public_key == bytes{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                             0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
}

Address::Address(std::string address) :
  Address(address, b32_decode(address)) {
}

Address::Address(std::string address, bytes with_checksum) :
  as_string(address),
  public_key(bytes{with_checksum.begin(), with_checksum.begin()+32}) {
  assert(as_string.size() == 58);
  assert(public_key.size() == 32);
}

static bytes
checksummed(bytes public_key) {
  bytes copy(public_key);
  auto hash = sha512_256(public_key);
  copy.insert(copy.end(), hash.end()-4, hash.end());
  return copy;
}

Address::Address(bytes public_key) : Address(public_key,  checksummed(public_key)) { }

Address::Address(bytes public_key, bytes checksummed) :
  as_string(b32_encode(checksummed)),
  public_key(public_key) {
  assert(as_string.size() == 58);
  assert(public_key.size() == 32);
}

bool Address::is_valid(const std::string address) {
  return address.size() == 58
      && uses_b32_alphabet(address)
      && Address::is_valid_checksummed(b32_decode(address));
}

bool Address::is_valid_checksummed(const bytes checksummed_key) {
  if (checksummed_key.size() != 36) return false;
  bytes key = bytes{checksummed_key.begin(), checksummed_key.begin()+32};
  return checksummed_key == checksummed(key);
}

std::ostream&
operator<<(std::ostream& os, const Address& addr) {
  os << addr.as_string;
  return os;
}
