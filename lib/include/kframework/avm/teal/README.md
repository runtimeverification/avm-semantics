TEAL Interpreter
================

Modules in this directory define the semantics of stateful and stateless teal programs:

* [`teal-driver.md`](./teal-driver.md) defines the semantics of the various TEAL opcodes and specifies how a TEAL program is interpreted.
* [`teal-execution.md`](./teal-execution.md) defines the execution flow of the interpreter:
  - [Interpreter Initialization](./teal-execution.md#teal-interpreter-initialization)
  - [Execution](./teal-execution.md#teal-execution)
  - [Interpreter Finalization](./teal-execution.md#teal-interpreter-finalization)
  - [TEAL Panic Behaviors](./teal-execution.md#panic-behaviors)
* [`teal-stack.md`](./teal-stack.md) defines the K representation of TEAL stack and the associated operations.
