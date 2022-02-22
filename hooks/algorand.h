#ifndef ALGORAND_H
#define ALGORAND_H

#include <memory>

#define RAPIDJSON_HAS_STDSTRING 1
#include "rapidjson/document.h"

#include <msgpack.hpp>

std::ostream& operator<<(std::ostream& os, const rapidjson::Value&);
std::string json_to_string(const rapidjson::Value&);

std::string maybe_env(std::string name, std::string def = "");
std::string require_env(std::string name);

struct JsonResponse {
  int status;
  std::unique_ptr<rapidjson::Document> json;
  rapidjson::Value& operator[](const std::string& name) const {
    return (*json)[name];
  }
  bool succeeded() const { return status == 200; }
};
std::ostream& operator<<(std::ostream& os, const JsonResponse& jr);

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



namespace msgpack {
  MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {
    namespace adaptor {
      template<>
      struct pack<Address> {
        template <typename Stream>
        packer<Stream>&
        operator()(msgpack::packer<Stream>& o, Address const& v) const {
          // We can't use MSGPACK_DEFINE because we don't want to
          // encode an "outer" object here, we just want an Address to
          // encode the public_key as if that was the whole object.
          return o.pack(v.public_key);
        }
      };

    } // namespace adaptor
  } // MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS)
}

#endif
