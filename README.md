**UNDER CONSTRUCTION**

-   `make deps`: build K.
-   `make build`: build KTeal.
-   `make test`: run tests.

Code
====

K files are located in `lib/include/kframework/`.

Shared Modules
--------------

This subdirectory contains common modules shared by the various subsystems
defined in this repository. They provide basic definitions shared by all other
modules.

This is in subdirectory `common`.

### Shared TEAL Modules

- [`teal-types.md`](./lib/include/kframework/common/teal-types.md) defines basic types representing values in TEAL and various operations involving them.
- [`teal-constants.md`](./lib/include/kframework/common/teal-constants.md) defines a set of integer constants TEAL uses, including transaction types and on-completion types.
- [`teal-fields.md`](./lib/include/kframework/common/teal-fields.md) defines sets of fields that may be used as arguments to some specific opcodes in TEAL, such as `txn/txna` fields and `global` fields.
- [`teal-syntax.md`](./lib/include/kframework/common/teal-syntax.md) defines the syntax of (textual) TEAL and the structure of its programs.
- [`additional-fields.md`](./lib/include/kframework/common/additional-fields.md) defines an additional set of fields that cannot appear in TEAL but may be used in other subsystems.

### Shared Blockchain Modules

- [`txn.md`](./lib/include/kframework/common/txn.md) provides a representation of all Algorand transaction types as nested K cell data structures along with data accessors.
- [`blockchain.md`](./lib/include/kframework/common/blockchain.md) provides a representation of the state of the Algorand blockchain and along with state accessors.
- [`args.md`](./lib/include/kframework/common/args.md) provides a representation of global arguments.

AVM Code
--------

This is in subdirectory `avm`.

- [`teal-stack.md`](./lib/include/kframework/avm/teal-stack.md): Everyone needs a stack and so does Teal.
- [`env-init.md`](./lib/include/kframework/avm/env-init.md): A dirty hack.
- [`driver.md`](./lib/include/kframework/avm/driver.md): Testing harness.
