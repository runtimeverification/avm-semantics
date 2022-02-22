#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstddef>
#include <iostream>
#include <random>

#include "runtime/alloc.h"
#include "runtime/header.h"
#include "algorand.h"
#include "base.h"
#include "mnemonic.h"

static blockheader header_int() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("inj{SortInt{}, SortResult{}}"));
  }

  return header;
}

static blockheader header_bool() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("inj{SortBool{}, SortResult{}}"));
  }

  return header;
}

static blockheader header_string() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("inj{SortString{}, SortResult{}}"));
  }

  return header;
}

static blockheader header_address() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("inj{SortAddressLiteral{}, SortResult{}}"));
  }

  return header;
}

static blockheader header_error() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("LblError{}"));
  }

  return header;
}

static blockheader header_notvalue() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("LblNoTValue{}"));
  }

  return header;
}

static blockheader header_tvaluelist() {
  static blockheader header = {(uint64_t)-1};

  if (header.hdr == -1) {
    header = getBlockHeaderForSymbol((uint64_t)getTagForSymbolName("inj{SortTValueList{}, SortMaybeTValue{}}"));
  }

  return header;
}

struct int_inj {
  blockheader h;
  mpz_ptr contents;
};

struct bool_inj {
  blockheader h;
  bool contents;
};

struct string_inj {
  blockheader h;
  string *contents;
};

static block *intResult(uint64_t i) {
  int_inj *retBlock = (int_inj*)(koreAlloc(sizeof(int_inj)));
  retBlock->h = header_int();
  mpz_t result;
  mpz_init_set_ui(result, i);
  retBlock->contents = move_int(result);
  return (block*)retBlock;
}

static block *boolResult(bool b) {
  bool_inj *retBlock = (bool_inj *)(koreAlloc(sizeof(bool_inj)));
  retBlock->h = header_bool();
  retBlock->contents = b;
  return (block*)(retBlock);
}

static block *stringResult(std::string s, blockheader header = header_string()) {
  string_inj *retBlock = (string_inj*)(koreAlloc(sizeof(string_inj)));
  retBlock->h = header;
  string *result = static_cast<string *>(koreAllocToken(sizeof(string) + s.size()));
  set_len(result, s.size());
  memcpy(result->data, s.c_str(), s.size());
  retBlock->contents = result;
  return (block*)retBlock;
}

static block *addressResult(Address a) {
  return stringResult("@" + a.as_string, header_address());
}

static block *errorResult(std::string s) {
  return stringResult(s, header_error());
}

struct value_cell {
  blockheader h;
  union {
    string_inj *str;
    int_inj *i;
    bool_inj *b;
    block *list;
  };
};

struct value_list {
  blockheader h;
  union {
    string_inj *str;
    int_inj *i;
    bool_inj *b;
  };
  value_list *list;
};

struct txn_header {
  blockheader h;
  value_cell *fee;
  value_cell *firstValid;
  value_cell *lastValid;
  value_cell *genesisHash;
  value_cell *sender;
  value_cell *txType;
  value_cell *typeEnum;
  value_cell *group;
  value_cell *genesisId;
  value_cell *lease;
  value_cell *note;
  value_cell *rekeyTo;
};

struct pay_txn {
  blockheader h;
  value_cell *receiver;
  value_cell *amount;
  value_cell *closeRemainderTo;
};

struct schema_cell {
  blockheader h;
  value_cell *nui;
  value_cell *nbs;
};

struct app_call_txn {
  blockheader h;
  value_cell *applicationId;
  value_cell *onCompletion;
  value_cell *accounts;
  value_cell *approvalProgram;
  value_cell *clearStateProgram;
  value_cell *applicationArgs;
  value_cell *foreignApps;
  value_cell *foreignAssets;
  schema_cell *globalStateSchema;
  schema_cell *localStateSchema;
};

struct key_reg_txn {
  blockheader h;
  value_cell *votePk;
  value_cell *selectionPk;
  value_cell *voteFirst;
  value_cell *voteLast;
  value_cell *voteKeyDilution;
  value_cell *nonparticipation;
};

struct asset_params {
  blockheader h;
  value_cell *total;
  value_cell *decimals;
  value_cell *defaultFrozen;
  value_cell *unitName;
  value_cell *name;
  value_cell *url;
  value_cell *metadataHash;
  value_cell *manager;
  value_cell *reserve;
  value_cell *freeze;
  value_cell *clawback;
};

struct asset_config_txn {
  blockheader h;
  value_cell *configAsset;
  asset_params *params;
};

struct asset_transfer_txn {
  blockheader h;
  value_cell *xferAsset;
  value_cell *amount;
  value_cell *receiver;
  value_cell *asender;
  value_cell *closeTo;
};

struct asset_freeze_txn {
  blockheader h;
  value_cell *account;
  value_cell *asset;
  value_cell *frozen;
};

struct txn {
  blockheader h;
  block *id;
  txn_header *hdr;
  pay_txn *pay;
  app_call_txn *app_call;
  key_reg_txn *key_reg;
  asset_config_txn *asset_config;
  asset_transfer_txn *asset_transfer;
  asset_freeze_txn *asset_freeze;
};

struct txn_inj {
  blockheader h;
  txn *tx;
};

static uint64_t makeInt(mpz_ptr i) {
  if (!mpz_fits_ulong_p(i)) {
    throw std::invalid_argument("Integer out of range");
  }
  return mpz_get_ui(i);
}

static std::string makeStr(string *s) {
  return std::string(s->data, len(s));
}

static bytes makeVec(string *s) {
  std::string str = makeStr(s);
  return bytes(str.begin(), str.end());
}

static Address makeAddr(string *s) {
  std::string tokenStr = makeStr(s);
  return Address(tokenStr.substr(1));
}

static AssetParams makeAssetParams(asset_params *params) {
  AssetParams result;
  result.total = makeInt(params->total->i->contents);
  result.decimals = makeInt(params->decimals->i->contents);
  result.default_frozen = params->defaultFrozen->b->contents;
  result.unit_name = makeStr(params->unitName->str->contents);
  result.asset_name = makeStr(params->name->str->contents);
  result.url = makeStr(params->url->str->contents);
  result.meta_data_hash = makeVec(params->metadataHash->str->contents);
  result.manager_addr = makeAddr(params->manager->str->contents);
  result.reserve_addr = makeAddr(params->reserve->str->contents);
  result.freeze_addr = makeAddr(params->freeze->str->contents);
  result.clawback_addr = makeAddr(params->clawback->str->contents);
  return result;
}

static StateSchema makeSchema(schema_cell *schema) {
  return StateSchema(makeInt(schema->nui->i->contents), makeInt(schema->nbs->i->contents));
}

static std::list<uint64_t> makeIntList(block *val) {
  uint32_t tag;
  if (is_leaf_block(val)) {
    tag = (uint64_t)val >> 32;
  } else {
    tag = tag_hdr(val->h.hdr);
  }
  if (tag == tag_hdr(header_int().hdr)) {
    std::list<uint64_t> result;
    result.push_back(makeInt(((int_inj *)val)->contents));
    return result;
  } else if (tag == tag_hdr(header_notvalue().hdr)) {
    std::list<uint64_t> result;
    return result;
  } else if (tag == tag_hdr(header_tvaluelist().hdr)) {
    return makeIntList((block *)((value_cell *)val)->list);
  } else {
    value_list *l = (value_list *)val;
    std::list<uint64_t> result = makeIntList((block *)l->list);
    result.push_front(makeInt(l->i->contents));
    return result;
  }
}

static std::list<Address> makeAddrList(block *val) {
  uint32_t tag;
  if (is_leaf_block(val)) {
    tag = (uint64_t)val >> 32;
  } else {
    tag = tag_hdr(val->h.hdr);
  }
  if (tag == tag_hdr(header_address().hdr)) {
    std::list<Address> result;
    result.push_back(makeAddr(((string_inj *)val)->contents));
    return result;
  } else if (tag == tag_hdr(header_notvalue().hdr)) {
    std::list<Address> result;
    return result;
  } else if (tag == tag_hdr(header_tvaluelist().hdr)) {
    return makeAddrList((block *)((value_cell *)val)->list);
  } else {
    value_list *l = (value_list *)val;
    std::list<Address> result = makeAddrList((block *)l->list);
    result.push_front(makeAddr(l->str->contents));
    return result;
  }
}

static std::list<bytes> makeVecList(block *val) {
  uint32_t tag;
  if (is_leaf_block(val)) {
    tag = (uint64_t)val >> 32;
  } else {
    tag = tag_hdr(val->h.hdr);
  }
  if (tag == tag_hdr(header_string().hdr)) {
    std::list<bytes> result;
    result.push_back(makeVec(((string_inj *)val)->contents));
    return result;
  } else if (tag == tag_hdr(header_notvalue().hdr)) {
    std::list<bytes> result;
    return result;
  } else if (tag == tag_hdr(header_tvaluelist().hdr)) {
    return makeVecList((block *)((value_cell *)val)->list);
  } else {
    value_list *l = (value_list *)val;
    std::list<bytes> result = makeVecList((block *)l->list);
    result.push_front(makeVec(l->str->contents));
    return result;
  }
}

static int rollback_depth = 0;
static const uint64_t MIN_FEE = 1000;
static const uint64_t MAX_LIFETIME = 1000;
static bool DEBUG = maybe_env("ALGOD_DEBUG").size() > 0;

class SpeculationClient : public AlgodClient {
  std::string token;
  bool managed_speculation = false;

  JsonResponse speculate(uint64_t round) {
    return post("/v2/blocks/" + std::to_string(round) + "/speculation");
  }
public:
  JsonResponse boundary(std::string op) {
    // std::cerr << token << " " << op << std::endl;
    auto resp = post("/v2/speculation/" + token + "/" + op);
    // std::cerr << resp << std::endl;
    return resp;
  }

  std::string account_url(std::string address) const {
    // & instead of ? becasue base class already uses ?format=json
    return AlgodClient::account_url(address) + "&speculation=" + token;
  }
  std::string asset_url(std::string id) const {
    return AlgodClient::asset_url(id) + "?speculation=" + token;
  }
  std::string submit_url() const {
    return AlgodClient::submit_url() + "?speculation=" + token;
  }
  std::string params_url() const {
    return AlgodClient::params_url() + "?speculation=" + token;
  }

public:
  SpeculationClient(uint64_t round) : AlgodClient() {
    auto speculation = speculate(round);
    if (!speculation.succeeded()) {
      std::cerr << speculation << std::endl;
      throw std::invalid_argument("ALGOD_ADDRESS ("+prefix+") does not support speculation");
    }
    token = speculation["token"].GetString();
    managed_speculation = true;
    assert(token.size());
  }

  SpeculationClient(std::string token) : AlgodClient(), token(token) {
    assert(token.size());
  }

  ~SpeculationClient() {
    if (managed_speculation) {
      // get the speculation context destroyed, if it was created in process
      post("/v2/speculation/" + token + "/delete");
      // It would be more REST-ish to perform a DELETE on the resource url.
    }
  }
};

AlgodClient* get_client() {
  static AlgodClient* client = 0;
  if (client)
    return client;

  // Use a supplied token, so multiple invocations can "read their writes"
  auto token = maybe_env("SPECULATION_TOKEN");
  if (token.size()) {
    return client = new SpeculationClient(token);
  }

  // Use a supplied round, 0 indicates "latest"
  auto round = maybe_env("SPECULATION_ROUND");
  if (round.size()) {
    return client = new SpeculationClient(stoi(round));
  }

  // No speculation, so we operate directly against blockchain. Not
  // clear this makes much sense (especially if submitting
  // transactions) but retaining this behaviour for testing
  // convenience if a speculative algod is unavailable.
  std::cerr << "Not speculating! Use SPECULATION_ROUND or SPECULATION_TOKEN." << std::endl;
  return client = new AlgodClient;
}

/* Just the info we need to make transactions */
struct TxParms {
  uint64_t fv;
  bytes genesis_hash;
};

TxParms* get_params(AlgodClient* client) {
  static TxParms* parms = 0;
  if (!parms) {
    auto resp = client->params();
    if (!resp.succeeded()) {
      throw std::invalid_argument(client->params_url() + " failed");
    }
    parms = new TxParms{
      resp["last-round"].GetUint64(),
      b64_decode(resp["genesis-hash"].GetString())
    };
  }
  return parms;
}

extern const std::string english;

std::map<std::string, int> word_map = make_word_map(english);


std::map<Address, Account> cosigners = {
  {Address{"GXBNLU4AXQABPLHXJDMTG2YXSDT4EWUZACT7KTPFXDQW52XPTIUS5OZ5HQ"},
   Account::from_mnemonic("ritual such year foil grow marble opinion sense arrow off busy liberty tennis merry dove quick cycle host segment style october furnace draft absent sample")},
  {Address{"SRUOGD3JR7OA6MP2SKRROTQBDGFF7MV3OXISI3AGKAQVOEIH4BZEMMYUAE"},
   Account::from_mnemonic("robust tornado future shock hidden truck churn tennis inch grain advice gate scare cement credit fatal social arrow much doll palm motion reduce able pool")},
  {Address{"WZ6J5IOJYMIWPD3A44VOSSMGCBVTLV4PRKH655SGRZ5CV33YWEPSLR6DMA"},
   Account::from_mnemonic("tiger walnut viable grace weasel swear nut fog trust slot earn measure gravity gallery drama awake spatial mandate genre sadness evoke true sound absorb source")},
};

extern "C" {

size_t hook_LIST_size_long(list * l);
block * hook_LIST_get_long(list * l, ssize_t idx);
block * hook_KREFLECTION_parseKORE(SortString kore);

struct string *hook_CLARITY_address_decode(struct string *input) {
  // decode address literal
  Address addr(std::string((const char *)input->data, len(input)));

  // prepare output data
  size_t output_len = addr.public_key.size();
  struct string *output = (struct string *)koreAllocToken(output_len + sizeof(struct string));
  set_len(output, output_len);
  memcpy(output->data, addr.public_key.data(), output_len);

  return output;
}

struct string *hook_CLARITY_address_encode(struct string *input) {
  // encode address bytes
  unsigned char *input_data = (unsigned char*) input->data;
  Address addr(bytes(input_data, input_data + len(input)));

  // prepare output data
  size_t output_len = addr.as_string.size();
  struct string *output = (struct string *)koreAllocToken(output_len + sizeof(struct string));
  set_len(output, output_len);
  memcpy(output->data, addr.as_string.c_str(), output_len);

  return output;
}

static int random_int() {
  static unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
  static std::default_random_engine generator(seed);
  static std::uniform_int_distribution<int> distribution;
  return distribution(generator);
}

bool hook_CLARITY_apply(SortList txns) {
  auto client = get_client();
  auto params = get_params(client);
  size_t len = hook_LIST_size_long(txns);
  std::vector<Transaction> decodedTxns;
  for (size_t i = 0; i < len; i++) {
    txn *tx = ((txn_inj *)hook_LIST_get_long(txns, i))->tx;
    // hdr fields first
    auto sender = makeAddr(tx->hdr->sender->str->contents);
    auto fee = std::max(makeInt(tx->hdr->fee->i->contents), MIN_FEE);
    auto fv = makeInt(tx->hdr->firstValid->i->contents);
    if (!fv)
      fv = params->fv;
    auto lv = makeInt(tx->hdr->lastValid->i->contents);
    if (!lv)
      lv = fv + MAX_LIFETIME;
    auto genid = makeStr(tx->hdr->genesisId->str->contents);
    auto genhash = makeVec(tx->hdr->genesisHash->str->contents);
    if (genhash.empty())
      genhash = params->genesis_hash;
    auto lease = makeVec(tx->hdr->lease->str->contents);
    auto note = makeVec(tx->hdr->note->str->contents);
    if (note.empty()) {
      auto s = std::to_string(random_int());
      note = bytes{s.begin(), s.end()};
    }
    auto rekey = makeAddr(tx->hdr->rekeyTo->str->contents);

    // Now switch on type
    std::string txType = makeStr(tx->hdr->txType->str->contents);
    if (txType == "pay") {
      std::cerr << std::string(rollback_depth, ' ') << "pay " << sender << std::endl;
      decodedTxns.push_back(Transaction::payment(
            sender,
            makeAddr(tx->pay->receiver->str->contents),
            makeInt(tx->pay->amount->i->contents),
            makeAddr(tx->pay->closeRemainderTo->str->contents),
            fee, fv, lv, genid, genhash, lease, note, rekey));

    } else if (txType == "acfg") {
      std::cerr << std::string(rollback_depth, ' ') << "acfg " << sender << std::endl;
      decodedTxns.push_back(Transaction::asset_config(
            sender,
            makeInt(tx->asset_config->configAsset->i->contents),
            makeAssetParams(tx->asset_config->params),
            fee, fv, lv, genid, genhash, lease, note, rekey));
    } else if (txType == "axfer") {
      std::cerr << std::string(rollback_depth, ' ') << "axfer " << sender << std::endl;
      decodedTxns.push_back(Transaction::asset_transfer(
            sender,
            makeInt(tx->asset_transfer->xferAsset->i->contents),
            makeInt(tx->asset_transfer->amount->i->contents),
            makeAddr(tx->asset_transfer->receiver->str->contents),
            makeAddr(tx->asset_transfer->asender->str->contents),
            makeAddr(tx->asset_transfer->closeTo->str->contents),
            fee, fv, lv, genid, genhash, lease, note, rekey));
    } else if (txType == "afrz") {
      std::cerr << std::string(rollback_depth, ' ') << "afrz " << sender << std::endl;
      decodedTxns.push_back(Transaction::asset_freeze(
            sender,
            makeAddr(tx->asset_freeze->account->str->contents),
            makeInt(tx->asset_freeze->asset->i->contents),
            tx->asset_freeze->frozen->b->contents,
            fee, fv, lv, genid, genhash, lease, note, rekey));
    } else if (txType == "appl") {
      std::cerr << std::string(rollback_depth, ' ') << "appl " << sender << std::endl;
      std::list<Address> addrs = makeAddrList(tx->app_call->accounts->list);
      std::list<bytes> args = makeVecList(tx->app_call->applicationArgs->list);
      std::list<uint64_t> apps = makeIntList(tx->app_call->foreignApps->list);
      std::list<uint64_t> assets = makeIntList(tx->app_call->foreignAssets->list);
      decodedTxns.push_back(Transaction::app_call(
            sender,
            makeInt(tx->app_call->applicationId->i->contents),
            makeInt(tx->app_call->onCompletion->i->contents),
            std::vector<Address>(addrs.begin(), addrs.end()),
            makeVec(tx->app_call->approvalProgram->str->contents),
            makeVec(tx->app_call->clearStateProgram->str->contents),
            std::vector<bytes>(args.begin(), args.end()),
            std::vector<uint64_t>(apps.begin(), apps.end()),
            std::vector<uint64_t>(assets.begin(), assets.end()),
            makeSchema(tx->app_call->globalStateSchema),
            makeSchema(tx->app_call->localStateSchema),

            fee, fv, lv, genid, genhash, lease, note, rekey));
    } else {
      throw std::invalid_argument("Invalid TXN type");
    }
  }

  std::vector<SignedTransaction> txgroup;
  for (auto& txn : decodedTxns) {
    Address need = txn.sender;  // Should consider rekeying
    auto signer = cosigners.find(need);
    if (signer == cosigners.end()) {
      if (DEBUG)
        std::cerr << "No cosigner for " << txn << std::endl;
      // Currently there's no signature check done, so we'll just use
      // the first cosigner.  This is "wrong", of course, but for now
      // we can do easier testing by allowing every possible txn.
      signer = cosigners.begin();
    }
    txgroup.push_back(txn.sign(signer->second));
  }
  auto resp = client->submit(txgroup);
  if (DEBUG)
    std::cerr << resp << std::endl;
  return resp.status == 200;
}

bool hook_CLARITY_checkpoint(void) {
  std::cerr << std::string(rollback_depth++, ' ') << "checkpoint" << std::endl;
  auto client = get_client();
  auto spec = dynamic_cast<SpeculationClient*>(client);
  if (!spec)
    return true;
  auto resp = spec->boundary("checkpoint");
  return resp.succeeded();
}

bool hook_CLARITY_commit(void) {
  std::cerr << std::string(--rollback_depth, ' ') << "commit" << std::endl;
  auto client = get_client();
  auto spec = dynamic_cast<SpeculationClient*>(client);
  if (!spec)
    return true;
  auto resp = spec->boundary("commit");
  return resp.succeeded();
}

bool hook_CLARITY_rollback(void) {
  std::cerr << std::string(--rollback_depth, ' ') << "rollback!" << std::endl;
  auto client = get_client();
  auto spec = dynamic_cast<SpeculationClient*>(client);
  if (!spec)
    return true;
  auto resp = spec->boundary("rollback");
  return resp.succeeded();
}

bool hook_CLARITY_assert(SortString argData, SortString teal) {
  std::string argDataStr = makeStr(argData);
  std::string tealStr    = makeStr(teal);
  std::cerr << "onchain-assert(" << argDataStr << ", " << tealStr << ")" << std::endl;
  bool success;
  success = true;
  return success;
}

bool hook_CLARITY_contractCommitment(SortString commitment) {
  std::string stdStr = makeStr(commitment);
  // ...
  bool success;
  if (success) {
    std::string result;
    return stringResult(result);
  } else {
    std::string errorMsg;
    return errorResult(errorMsg);
  }
}

typedef string *SortAddressLiteral;

block *hook_CLARITY_databaseGet(SortAddressLiteral contractID, SortString key) {
  Address addr = makeAddr(contractID);
  auto client = get_client();
  auto resp = client->database_get(addr, makeStr(key));
  if (DEBUG)
    std::cerr << resp << std::endl;

  // HTTP status code
  if (!resp.succeeded()) {
    return errorResult(resp["message"].GetString());
  // Member existence and type
  } else if (!resp.json->HasMember("value") || !resp["value"].IsString()) {
    return errorResult("Ill-formed JSON response: member value not found or not string type!");
  // Member has valid type
  } else {
    return stringResult(std::string(resp["value"].GetString(), resp["value"].GetStringLength()));
  }

}

bool hook_CLARITY_accountExists(SortAddressLiteral address) {
  Address addr = makeAddr(address);

  auto client = get_client();
  auto acct = client->account(addr);
  return acct["amount"].GetUint64() > 0;
}

SortInt hook_CLARITY_balance(SortAddressLiteral address) {
  Address addr = makeAddr(address);

  auto client = get_client();
  auto acct = client->account(addr);
  uint64_t balance = acct["amount"].GetUint64();
  mpz_t balanceZ;
  mpz_init_set_ui(balanceZ, balance);
  return move_int(balanceZ);
}

bool hook_CLARITY_assetExists(SortInt assetIdZ) {
  uint64_t assetId = makeInt(assetIdZ);
  auto client = get_client();
  auto resp = client->asset(assetId);
  return resp.succeeded();
}

struct Holding {
  uint64_t amount;
  uint64_t assetId;
  Address creator;
  bool frozen;
};

std::unique_ptr<Holding> holding(Address addr, uint64_t id) {
  auto client = get_client();
  auto resp = client->account(addr);
  if (!resp.succeeded()) {
    return 0;
  }
  auto& assets = resp["assets"];
  for (auto asset = assets.Begin(); asset != assets.End(); asset++) {
    auto aid = (*asset)["asset-id"].GetUint64();
    if (aid == id)
      return std::make_unique<Holding>(Holding{
          (*asset)["amount"].GetUint64(),
          (*asset)["asset-id"].GetUint64(),
          Address{(*asset)["creator"].GetString()},
          (*asset)["is-frozen"].GetBool()});
  }
  return 0;
}

bool hook_CLARITY_assetOptedIn(SortInt assetIdZ, SortAddressLiteral address) {
  uint64_t assetId = makeInt(assetIdZ);
  Address addr = makeAddr(address);

  std::unique_ptr<Holding> h = holding(addr, assetId);
  return h ? true : false;
}

block *hook_CLARITY_assetBalance(SortInt assetIdZ, SortAddressLiteral address) {
  uint64_t assetId = makeInt(assetIdZ);
  Address addr = makeAddr(address);

  std::unique_ptr<Holding> h = holding(addr, assetId);
  if (h) {
    return intResult(h->amount);
  } else {
    std::string errorMsg("NO OPT-IN");
    return errorResult(errorMsg);
  }
}

block *hook_CLARITY_assetFrozen(SortInt assetIdZ, SortAddressLiteral address) {
  uint64_t assetId = makeInt(assetIdZ);
  Address addr = makeAddr(address);

  std::unique_ptr<Holding> h = holding(addr, assetId);
  if (h) {
    return boolResult(h->frozen);
  } else {
    std::string errorMsg("NO OPT-IN");
    return errorResult(errorMsg);
  }
}

typedef block *SortAssetParamsField;

block *hook_CLARITY_assetParam(SortAssetParamsField f, SortInt assetIdZ) {
  uint64_t assetId = makeInt(assetIdZ);

  SortAssetParamsField assetTotal = leaf_block(getTagForSymbolName("LblAssetTotal{}"));
  SortAssetParamsField assetDecimals = leaf_block(getTagForSymbolName("LblAssetDecimals{}"));
  SortAssetParamsField assetDefaultFrozen = leaf_block(getTagForSymbolName("LblAssetDefaultFrozen{}"));
  SortAssetParamsField assetUnitName = leaf_block(getTagForSymbolName("LblAssetUnitName{}"));
  SortAssetParamsField assetName = leaf_block(getTagForSymbolName("LblAssetName{}"));
  SortAssetParamsField assetURL = leaf_block(getTagForSymbolName("LblAssetURL{}"));
  SortAssetParamsField assetMetadataHash = leaf_block(getTagForSymbolName("LblAssetMetadataHash{}"));
  SortAssetParamsField assetManager = leaf_block(getTagForSymbolName("LblAssetManager{}"));
  SortAssetParamsField assetReserve = leaf_block(getTagForSymbolName("LblAssetReserve{}"));
  SortAssetParamsField assetFreeze = leaf_block(getTagForSymbolName("LblAssetFreeze{}"));
  SortAssetParamsField assetClawback = leaf_block(getTagForSymbolName("LblAssetClawback{}"));

  auto client = get_client();
  auto resp = client->asset(assetId);
  if (!resp.succeeded()) {
    return errorResult(resp["message"].GetString());
  }

  auto& params = resp["params"];
  // Not everything is "omitempty", but seems little harm in checking
  // each, in case that changes.
  if (f == assetTotal) {
    if (!params.HasMember("total"))
      return intResult(0);
    return intResult(params["total"].GetUint64());
  } else if (f == assetDecimals) {
    if (!params.HasMember("decimals"))
      return intResult(0);
    return intResult(params["decimals"].GetUint64());
  } else if (f == assetDefaultFrozen) {
    if (!params.HasMember("default-frozen"))
      return boolResult(false);
    return boolResult(params["default-frozen"].GetBool());
  } else if (f == assetUnitName) {
    if (!params.HasMember("unit-name"))
      return stringResult("");
    return stringResult(params["unit-name"].GetString());
  } else if (f == assetName) {
    if (!params.HasMember("name"))
      return stringResult("");
    return stringResult(params["name"].GetString());
  } else if (f == assetURL) {
    if (!params.HasMember("url"))
      return stringResult("");
    return stringResult(params["url"].GetString());
  } else if (f == assetMetadataHash) {
    if (!params.HasMember("metadata-hash"))
      return stringResult("");
    return stringResult(params["metadata-hash"].GetString());
  } else if (f == assetManager) {
    if (!params.HasMember("manager"))
      return addressResult(Address());
    return addressResult(Address(params["manager"].GetString()));
  } else if (f == assetReserve) {
    if (!params.HasMember("reserve"))
      return addressResult(Address());
    return addressResult(Address(params["reserve"].GetString()));
  } else if (f == assetFreeze) {
    if (!params.HasMember("freeze"))
      return addressResult(Address());
    return addressResult(Address(params["freeze"].GetString()));
  } else if (f == assetClawback) {
    if (!params.HasMember("clawback"))
      return addressResult(Address());
    return addressResult(Address(params["clawback"].GetString()));
  } else {
    throw std::invalid_argument("Invalid asset parameter field");
  }
}

}

