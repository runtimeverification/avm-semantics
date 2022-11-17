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

extern "C" {

size_t hook_LIST_size_long(list * l);
block * hook_LIST_get_long(list * l, ssize_t idx);
block * hook_KREFLECTION_parseKORE(SortString kore);

bool hook_KAVM_check_address(struct string *input) {
  unsigned char *input_data = (unsigned char*) input->data;
  return Address::is_valid(std::string(input_data, input_data + len(input)));
}

struct string *hook_KAVM_address_decode(struct string *input) {
  // decode address literal
  Address addr(std::string((const char *)input->data, len(input)));

  // prepare output data
  size_t output_len = addr.public_key.size();
  struct string *output = (struct string *)koreAllocToken(output_len + sizeof(struct string));
  set_len(output, output_len);
  memcpy(output->data, addr.public_key.data(), output_len);

  return output;
}

struct string *hook_KAVM_address_encode(struct string *input) {
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

struct string *hook_KAVM_b64_decode(struct string *input) {
  auto encoded = std::string((const char *)input->data, len(input));
  auto decoded = b64_decode(encoded);
  auto decoded_str = std::string(decoded.begin(), decoded.end());

  // prepare output data
  size_t output_len = decoded_str.size();
  struct string *output = (struct string *)koreAllocToken(output_len + sizeof(struct string));
  set_len(output, output_len);
  memcpy(output->data, decoded_str.c_str(), output_len);

  return output;
}

struct string *hook_KAVM_b64_encode(struct string *input) {
  // decode address literal
  auto decoded = std::string((const char *)input->data, len(input));
  auto decoded_bytes = bytes(decoded.begin(), decoded.end());
  auto encoded = b64_encode(decoded_bytes, true);

  // prepare output data
  size_t output_len = encoded.size();
  struct string *output = (struct string *)koreAllocToken(output_len + sizeof(struct string));
  set_len(output, output_len);
  memcpy(output->data, encoded.c_str(), output_len);

  return output;
}

}
