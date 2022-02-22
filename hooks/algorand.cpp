#include "algorand.h"
#include "base.h"
#include "mnemonic.h"

#include <iostream>
#include <map>
#include <sstream>
#include <vector>

#include <sodium.h>

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

std::string to_hex(const std::string& in) {
  std::stringstream ss;
  ss << std::hex << std::setfill('0');
  for (size_t i = 0; in.size() > i; i++) {
    ss << std::setw(2) << (int)(unsigned char)in[i] << ':';
  }
  return ss.str();
}
std::string to_hex(const bytes& in) {
  std::stringstream ss;
  ss << std::hex << std::setfill('0');
  for (size_t i = 0; in.size() > i; i++) {
    ss << std::setw(2) << (int)(unsigned char)in[i] << ':';
  }
  return ss.str();
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

std::ostream&
operator<<(std::ostream& os, const Address& addr) {
  os << addr.as_string;
  return os;
}

std::pair<bytes,bytes>
Account::generate_keys(bytes seed) {
  assert(sodium_init() >= 0);
  unsigned char ed25519_pk[crypto_sign_ed25519_PUBLICKEYBYTES];
  unsigned char ed25519_sk[crypto_sign_ed25519_SECRETKEYBYTES];

  crypto_sign_ed25519_seed_keypair(ed25519_pk, ed25519_sk, seed.data());
  auto pub = bytes{ed25519_pk, &ed25519_pk[sizeof(ed25519_pk)]};
  auto sec = bytes{ed25519_sk, &ed25519_sk[sizeof(ed25519_sk)]};
  return std::make_pair(pub, sec);
}

std::pair<bytes,bytes>
Account::generate_keys() {
  assert(sodium_init() >= 0);
  unsigned char ed25519_pk[crypto_sign_ed25519_PUBLICKEYBYTES];
  unsigned char ed25519_sk[crypto_sign_ed25519_SECRETKEYBYTES];

  crypto_sign_ed25519_keypair(ed25519_pk, ed25519_sk);
  auto pub = bytes{ed25519_pk, &ed25519_pk[sizeof(ed25519_pk)]};
  auto sec = bytes{ed25519_sk, &ed25519_sk[sizeof(ed25519_sk)]};
  return std::make_pair(pub, sec);
}

bytes
Account::seed() const {
  unsigned char ed25519_seed[crypto_sign_ed25519_SEEDBYTES];
  crypto_sign_ed25519_sk_to_seed(ed25519_seed, secret_key.data());
  return bytes{ed25519_seed, &ed25519_seed[sizeof(ed25519_seed)]};
}

bytes
Account::sign(std::string prefix, bytes msg) const {
  bytes concat{prefix.begin(), prefix.end()};
  concat.insert(concat.end(), msg.begin(), msg.end());
  return sign(concat);
}

bytes
Account::sign(bytes msg) const {
  assert(secret_key.size() == crypto_sign_ed25519_SECRETKEYBYTES);
  unsigned char sig[crypto_sign_ed25519_BYTES];
  crypto_sign_ed25519_detached(sig, 0, msg.data(), msg.size(), secret_key.data());
  auto s = bytes{sig, &sig[sizeof(sig)]};
  return s;

}

Account::Account(std::string address)
  : address(Address(address)) {
}

Account::Account(Address address)
  : address(address) {
}

Account::Account(bytes public_key, bytes secret_key)
  : address(Address(public_key)), secret_key(secret_key)  {
  assert(public_key.size() == crypto_sign_ed25519_PUBLICKEYBYTES);
  assert(secret_key.size() == crypto_sign_ed25519_SECRETKEYBYTES);
}

Account::Account(std::pair<bytes,bytes> key_pair) :
  Account(key_pair.first, key_pair.second) {
}

Account Account::from_mnemonic(std::string m) {
  auto seed = seed_from_mnemonic(m);
  auto keys = generate_keys(seed);
  return Account(keys.first, keys.second);
}

std::string Account::mnemonic() const {
  return mnemonic_from_seed(seed());
}

std::ostream&
operator<<(std::ostream& os, const Account& acct) {
  os << acct.address;
  return os;
}

bool is_present(bool b) {
  return b;
}
bool is_present(uint64_t u) {
  return u != 0;
}
bool is_present(std::string s) {
  return !s.empty();
}
bool is_present(bytes b) {
  return !b.empty();
}
bool is_present(Address a) {
  return !a.is_zero();
}
bool is_present(LogicSig lsig) {
  return is_present(lsig.logic);
};
bool is_present(MultiSig msig) {
  return msig.threshold > 0;
};
bool is_present(AssetParams ap) {
  return ap.key_count() > 0;
};
bool is_present(StateSchema schema) {
  return schema.ints > 0 || schema.byte_slices > 0;
};

template <typename E>
bool is_present(std::vector<E> list) {
  for (const auto& e : list)
    if (is_present(e)) return true;
  return false;
}



template <typename Stream, typename V>
int kv_pack(msgpack::packer<Stream>& o, const char* key, V value) {
  if (!is_present(value))
    return 0;
  o.pack(key);
  o.pack(value);
  return 1;
}

LogicSig LogicSig::sign(Account acct) const {
  auto sig = acct.sign("Program", logic);
  return LogicSig{logic, args, sig};
}

template <typename Stream>
msgpack::packer<Stream>& LogicSig::pack(msgpack::packer<Stream>& o) const {
  o.pack_map(1 + is_present(args) + is_present(sig));
  kv_pack(o, "arg", args);
  kv_pack(o, "l", logic);
  kv_pack(o, "sig", sig);
  return o;
}

Subsig::Subsig(bytes public_key, bytes signature)
  : public_key(public_key), signature(signature) { }

template <typename Stream>
msgpack::packer<Stream>& Subsig::pack(msgpack::packer<Stream>& o) const {
  o.pack_map(1 + is_present(signature));
  kv_pack(o, "pk", public_key);
  kv_pack(o, "s", signature);
  return o;
}

MultiSig::MultiSig(std::vector<Address> addrs, uint64_t threshold) :
  threshold(threshold ? threshold : addrs.size()) {
  for (const auto& addr : addrs) {
    sigs.push_back(Subsig(addr.public_key));
  }
}

template <typename Stream>
msgpack::packer<Stream>& MultiSig::pack(msgpack::packer<Stream>& o) const {
  o.pack_map(3);
  o.pack("subsigs"); o.pack(sigs);
  kv_pack(o, "thr", threshold);
  kv_pack(o, "v", version);
  return o;
}

int AssetParams::key_count() const {
  /* count the non-empty fields, for msgpack */
  int keys = 0;
  keys += is_present(total);
  keys += is_present(decimals);
  keys += is_present(default_frozen);
  keys += is_present(unit_name);
  keys += is_present(asset_name);
  keys += is_present(url);
  keys += is_present(meta_data_hash);
  keys += is_present(manager_addr);
  keys += is_present(reserve_addr);
  keys += is_present(freeze_addr);
  keys += is_present(clawback_addr);
  return keys;
}

template <typename Stream>
msgpack::packer<Stream>& AssetParams::pack(msgpack::packer<Stream>& o) const {
  o.pack_map(key_count());
  /* ordering is semantically ugly, but must be lexicographic */
  kv_pack(o, "an", asset_name);
  kv_pack(o, "au", url);
  kv_pack(o, "c", clawback_addr.public_key);
  kv_pack(o, "dc", decimals);
  kv_pack(o, "df", default_frozen);
  kv_pack(o, "f", freeze_addr);
  kv_pack(o, "m", manager_addr);
  kv_pack(o, "r", reserve_addr);
  kv_pack(o, "t", total);
  kv_pack(o, "un", unit_name);
  return o;
}

int StateSchema::key_count() const {
  /* count the non-empty fields, for msgpack */
  int keys = 0;
  keys += is_present(ints);
  keys += is_present(byte_slices);
  return keys;
}

template <typename Stream>
msgpack::packer<Stream>& StateSchema::pack(msgpack::packer<Stream>& o) const {
  o.pack_map(key_count());
  kv_pack(o, "nui", ints);
  kv_pack(o, "nbs", byte_slices);
  return o;
}
