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


class Account {
public:
  Account(std::string address);
  Account(Address address);
  Account(bytes public_key, bytes secret_key);
  Account(std::pair<bytes,bytes> key_pair);

  static Account from_mnemonic(std::string mnemonic);
  static std::pair<bytes,bytes> generate_keys();
  static std::pair<bytes,bytes> generate_keys(bytes seed);

  std::string mnemonic() const;
  bytes seed() const;
  bytes sign(std::string prefix, bytes msg) const;
  bytes sign(bytes msg) const;

  const bytes public_key() const { return address.public_key; }
  const Address address;
  const bytes secret_key;       // empty() if created from an address, not key
};
std::ostream& operator<<(std::ostream& os, const Account& acct);


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

class RestClient {
public:
  RestClient(std::string prefix, std::string authorization) :
    prefix(prefix), authorization(authorization) { }
  /**
   * @brief Return the requested information from the API using method
   * @param route API route.
   * @param method HTTP method to make the request with
   * @param request_body raw bytes to be sent as body of request
   * @return JsonResponse with the status code and JSON value from response
   */
  JsonResponse api(const std::string& route,
                   const std::string& method,
                   const std::string& request_body = "") const;

  /**
   * @brief Return the requested information from the API using a GET
   * @param route API route.
   * @return string containing the requested information.
   */
  JsonResponse get(const std::string& route) const;

  /**
   * @brief Return the requested information from the API using a POST
   * @param route API route.
   * @param body Raw bytes to send as body. "" means no body.
   * @return string containing the requested information.
   */
  JsonResponse post(const std::string& route, const std::string& body = "") const;

protected:
  std::string prefix;
  std::string authorization;
};

class AlgodClient : public RestClient {
public:
  /**
   * @brief Initialize the client. Reads ALGOD_ADDRESS, ALGOD_TOKEN
   * from environment.
   */
  AlgodClient();

  /**
   * @brief Initialize the client with passed address for algod and API token.
   */
  AlgodClient(std::string address, std::string token);

  JsonResponse genesis(void);
  bool healthy(void);
  std::string metrics(void);

  virtual std::string account_url(std::string address) const;
  JsonResponse account(std::string address);
  JsonResponse account(const Address& addr) { return account(addr.as_string); }
  JsonResponse account(const Account& acct) { return account(acct.address); }

  JsonResponse transactions_pending(std::string address, unsigned max = 0);
  JsonResponse application(std::string id);
  JsonResponse application(uint64_t id) { return asset(std::to_string(id)); }

  virtual std::string asset_url(std::string id) const;
  JsonResponse asset(std::string id);
  JsonResponse asset(uint64_t id) { return asset(std::to_string(id)); }

  JsonResponse block(uint64_t round);
  JsonResponse catchup(std::string catchpoint);
  JsonResponse abort_catchup(std::string catchpoint);
  JsonResponse supply();
  JsonResponse register_participation_key(std::string address, uint64_t fee, uint64_t key_dilution, bool no_wait, uint64_t lv);
  JsonResponse status();
  JsonResponse status_after(uint64_t block);

  JsonResponse teal_compile(std::string source);
  JsonResponse teal_dryrun(rapidjson::Value& request);

  JsonResponse database_get(Address contract_id, std::string key);
  JsonResponse database_get_with_prefix(Address contract_id, std::string key_prefix);

  virtual std::string submit_url() const;
  JsonResponse submit(std::string raw) const;
  JsonResponse transaction_pending(std::string txid = "");

  virtual std::string params_url() const;
  JsonResponse params();
};

class IndexerClient : RestClient {
public:
  /**
   * @brief Initialize the client. Reads INDEXER_ADDRESS, INDEXER_TOKEN
   * from environment.
   */
  IndexerClient();
  /**
   * @brief Initialize the client with passed address for indexer and API token.
   */
  IndexerClient(std::string address, std::string token);

  bool healthy(void);
  JsonResponse accounts(uint64_t limit=20, std::string next_page="",
                        uint64_t held_asset=0, uint64_t min_bal=0, uint64_t max_bal=0,
                        uint64_t optedin_app=0,
                        Address auth_addr=Address(), uint64_t as_of=0);
  JsonResponse account(Address addr, uint64_t round=0);
  JsonResponse block(uint64_t round=0);
};
#endif
