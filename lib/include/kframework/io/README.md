Shared Modules
--------------

This subdirectory contains common modules shared by the various subsystems
defined in this repository. They provide basic definitions shared by all other
modules.


### Shared TEAL Modules

- [`teal-types.md`](./teal-types.md) defines basic types representing values in
  TEAL and various operations involving them.

- [`teal-constants.md`](./teal-constants.md) defines a set of integer constants
  TEAL uses, including transaction types and on-completion types.

- [`teal-fields.md`](./teal-fields.md) defines sets of fields that may be used
  as arguments to some specific opcodes in TEAL, such as `txn/txna` fields and
  `global` fields.

- [`teal-syntax.md`](./teal-syntax.md) defines the syntax of (textual) TEAL and
  the structure of its programs.

- [`additional-fields.md`](./additional-fields.md) defines an additional set of
  fields that cannot appear in TEAL but may be used in other subsystems.


### Shared Blockchain Modules

- [`txn.md`](./txn.md) provides a representation of all Algorand transaction
  types as nested K cell data structures along with data accessors.

- [`blockchain.md`](./blockchain.md) provides a representation of the state of
  the Algorand blockchain and along with state accessors.

- [`algod.md`](./algod.md) provides a representation of `algod`'s state.

- [`args.md`](./args.md) provides a representation of global arguments.


### Utility Modules

- [`buffered-io.md`](./buffered-io.md) gives an implementation of buffered IO in
  K for reading from and writing to the file system.

- [`json-ext.md`](./json-ext.md) gives an implementation of JSON in K and
  defines various JSON-processing functions.




