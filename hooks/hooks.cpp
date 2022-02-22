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

}
