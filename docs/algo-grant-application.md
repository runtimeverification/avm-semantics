* **Organization / Company Name**: Runtime Verification, Inc.

* **Project Name**: KTEAL: Formal Semantics for TEAL Smart Contract Analysis and Verification

* **Core Team & Experience**: Team lead: Georgy Lukyanov (Github: geo2a) has extensive experience auditing TEAL code, working on the KTEAL semantics and TEAL/PyTEAL analysis tools. Georgy's involvement to date with the project makes us confident on his ability to deliver. Advisor/Oversight: Everett Hildenbrandt (Github: ehildenb) helped develop numerous K semantics in the past, include KEVM (https://github.com/kframework/evm-semantics) and KWasm (https://github.com/kframework/wasm-semantics). Both semantics have been used for real-world verification of smart-contract code.

* **Short Project Description**: The development of formal analysis and verification tools for TEAL enabling concrete and symbolic execution, model-based testing and test coverage analysis, and correctness proofs on critical parts of TEAL smart contracts.

* **Elevator Pitch (up to 400 characters)**: Formally verifying correctness provides the highest levels of assurance. We provide formal-verification-based auditing services of EVM bytecode, which add significant value to developers and the ecosystem. Already we have audit clients who have asked for formal verification of their TEAL code. The project enables providing these services and allows developers to deploy provably correct code.

* **What Stage Is The Project In?**: We have a preliminary and incomplete prototype in K of TEAL v3 already developed and usable. The prototype can be used to run simple TEAL v3 contracts and prove some simple reachability properties.

* **Grant Amount Requested (In USD)**: 300000

* **Estimated Total Cost of Project (In USD)**: 420000

* **Provide The URL Of Your Project Repository**: https://github.com/runtimeverification/avm-semantics [Note: currently a private Github repo]

* **Are you building on any other layer 1 blockchain?**: Yes: Ethereum, Tezos, Cardano, Polkadot, and Cosmos.

* **What is your Website URL (if applicable)?**: https://runtimeverification.com/

* **Primary Contact**: Patrick MacKay, COO at Runtime Verification, [patrick.mackay@runtimeverification.com](mailto:patrick.mackay@runtimeverification.com)

* **Contact Name of Referral**: Ryan Terribilini

* **Where did you hear about SupaGrants?**: Friends and Twitter

## Company Description

Runtime Verification Inc. is a technology startup headquartered in the USA with staff spread across the globe, including Europe, South America, and Southeast Asia. We provide testing and verification services to public and private companies in the embedded and blockchain domains. In the latter we work with infrastructure builders as well as companies building products and providing services supported and/or powered by said infrastructure. The company was founded in 2010. It employs 50 people at the moment, and is looking to double in size in the next 12 to 18 months.

For the time being, blockchain safety tests are mostly lightweight static analysis tests (testing only the internal logic of source code), while dynamic analysis test (using the data generated as the codes are compiled and executed) increases coverage to find bugs as opposed to static analysis tests. Runtime Verification is a global leader in formal verification and is capable of directly verifying compiled binary code. Compared to the formal verification of source code, this catches bugs that are otherwise missed due to miscompilation.


## Provide a Technical Description of Your Solution

The solution is based on developing formal specifications of the TEAL language and TEAL's execution engine in the AVM in the K framework and deriving all artifacts and analysis tools from these specifications. The K framework is a language-agnostic formal tool for the development of programming languages tools. It encompasses many components developed in different languages carefully chosen to develop each component. Some of them are:

* K front-end: it defines a notation for rule-based specifications.
* Kore: is the intermediate representation of K. It is essentially a concrete syntax for matching logic, the logic foundation of K. K definitions are compiled to Kore.
* K's backends: the main backends today are comprised by the LLVM backend and the Haskell backend. The former provides efficient execution and state search capabilities to Kore definitions and the latter provides a fully-fledged symbolic machine to K. The Haskell backend in connection with an SMT solver give rise to a powerful theorem prover.
* The K approach to language-development encompasses the development of a formal semantics as a K description which is then used as the formal theory upon which properties of programs are done.


## Technical Roadmap & Statement of Work

### Motivation:

The Algorand DeFi ecosystem is experiencing a boom of new projects that utilise the platform's scalability and fast transaction finality. The developer community is vibrant, productive and supportive, as witnessed by the active developer-focused Discord community with nearly two thousand active members and many active discussions on Twitter. We also see a major surge of requests for security audits of Algorand smart contracts.

Runtime Verification Inc is a leading security audit service provider for smart contracts, and the Algorand Foundation's Security Partner. The Algorand auditors team at RV has grown significantly over the past months, primarily in response to this surge in audit requests. While the auditing services we provide for Algroand at the moment mostly comprise manual code review and pen-and-paper reasoning, we already have clients approaching us and requesting full mechanised formal verification of their smart contracts.
Besides traditional security audits, we have extensive experience of applying the K Framework to building mechanised formal proofs of smart contract correctness. The KEVM semantics of the Ethereum Virtual Machine is the bedrock of our verification toolchain for Ethereum smart contracts.

At RV, we approach smart contract security audits with a formal, mathematical outlook. We love formal methods! And we would like to share our passion for formal verification with the Algorand community. We believe that having a formal semantics of AVM and TEAL will widen adoption of formal verification among TEAL and PyTeal smart contract developers and auditors. Developing semantics is expensive though, and thus the grant becomes essential for us to provide formally-based high-quality services to the TEAL community. Moreover, in terms of community effect, this project will produce an open source semantics which anyone (developers, researchers, auditing firms, ... etc) can use to do program verification, and will be used to offer formal verification for key projects in the TEAL ecosystem. The k-dss project is a fair example of an open source semantics (KEVM) leading to real community value (securing DAI smart contracts).

### Goals:

This project intends to build:
1. a formal, executable and open-source semantics of TEAL available to everyone;
2. through the Haskell backend of K, a symbolic execution engine and a formal verification tool for TEAL smart contracts;
3. through the LLVM backend of K, a simulation and unit-testing framework (with coverage analysis) with performance that is comparable to that of the reference implementation.

### Non-goals:

We do not intend to build a replacement of the existing Algorand node implementation, therefore the model does not encompass the block consensus and validation rewards.


### Project Scope:

We envision the semantics to take as input the following:
1. an Algorand blockchain state, i.e. the lists and states of Accounts, ASAs and Applications;
2. a description of an atomic transaction group; and perform the group's evaluation. The result should be either approval and the commitment of the new, altered blockchain state, or denial and the rollback to the previous valid state before group evaluation (see the attached TEAL execution flowchart). Note that, at least for now, we do not intend to model the evaluation of several transaction groups or the wider Algorand consensus.

### Project Phases and Timeline:

1. Discovery phase (2 weeks). Over the past year, we have accumulated a number of internal developments, both in K and other languages, that model TEAL. More specifically, We have an existing prototype semantics that model the execution of a single transaction and TEAL v3. Additionally, we have developed semantics in K for other blockchain virtual machines. We need to consolidate the knowledge and develop a semantics architecture in the K framework that supports current (and future) versions of TEAL and the AVM.
**Deliverables**: Semantics architecture, description of the data structures and algorithms in form of flowcharts and natural language descriptions.

2. Development phase (7 weeks). Following the architecture developed in the discovery phase, we will develop the semantics as a collection of K Framework modules. We will implement the semantics of all TEAL opcodes, the execution cycle of a single TEAL transaction and the execution cycle of an atomic transaction group. We will work closely with the implementors of KEVM to make use of their experience. More specifically, we need to accomplish the following tasks:
    - Bring the current unfinished KTEAL semantics (which supports TEAL v3) up-to-date with the architecture developed in the Discovery Phase (2 weeks)
    - Implement remaining TEAL v4 opcodes (1 week)
    - Implement inner transactions support (2 weeks)
    - Implement remaining TEAL v5 opcodes (1 week)
    - research and implement the recently added TEAL v6 features (1 week)
    **Deliverables**: A complete and executable semantics of TEAL in K Framework. Unit-tests for individual opcode semantics. Limited integration tests in form of simple TEAL programs.

3. Testing phase (4 weeks) The testing phase will focus on enlarging the unit and integration test suite, and on adding symbolic proofs. The symbolic proof development will proceed bottom-up:
    - First, we will develop correctness proofs for arithmetic opcodes, such as add, mul, div, etc. We will consider both uint64 and byte versions (1 week).
    - Second, we will work on proofs of correctness of control-flow operations, such as conditional jumps, loops and procedure calls (1 week).
    - Finally, we will verify a number of simple algorithms implemented in TEAL (2 weeks).
The purpose of the basic symbolic proof suite is to both serve as a sanity-check for the semantics, and to showcase the methodology of constructing specification for simple TEAL programs. It is essential for the specification to be clear and concise, and to only mention the state they absolutely must refer to. This becomes vital to retain ease of understanding as we scale up to larger proofs.
**Deliverables**: A substantial suite of concrete unit-tests and symbolic proofs of correctness of TEAL programs.

4. Case-study phase (4 weeks) Having the complete semantics in place, we will work on developing an add-on that will leverage the semantics to perform property-based testing of TEAL smart contracts:
   - Provide a simple Python bindings to supply the semantics with the initial network state and the transaction group
   - Leverage existing testing frameworks in the Python ecosystem, like `pytest` and Hypothesis, to drive the test generation and execution process
**Deliverables**:
    - A prototype command-line tool for describing and checking properties of TEAL smart contracts by testing
    - Python bindings to enable programmatic interaction with the semantics
    - Examples of properties and testing scenarios for a real-world smart contract

### Key Milestones:

There is one key milestone for each project phase as described above. The key milestones are as follows:
- (2 weeks) Informal description of the semantics architecture of TEAL and its structures and behavior
- (7 weeks) An executable, formal semantics for TEAL in K along with a set of tools (interpreter, symbolic execution engine, formal verifier)
- (4 weeks) A test suite and a proof suite for TEAL (with documentation)
- (4 weeks) A case-study property testing tool developed on top of the semantics

### Future Work

We give a number of directions for developing the semantics and the tools on top of it in the future:

- **Automatic symbolic proofs of common properties**
  We have in the past developed a library of symbolic properties to test the compliance with ERC20 standard, which we have deployed as a push-button web-based tool (See https://erc20.fireflyblockchain.com/). The Algorand ecosystem has already seen a number of smart contract exploits that could have been prevented by a well-defined automated analysis. We propose to build such an automated analysis tool by collecting a curated set of properties and automatically checking them by symbolically executing the contract's code.

- **From property-testing to formal proof**
  The practise shows that for smart contract developers, it is relatively easy to make the jump from writing unit tests to writing property tests. When we get the engineers hooked on the property testing, we can seamlessly turn many property tests into symbolic proofs, without requiring any addition import from the user. Under the hood, the semantics will now be run in symbolic mode with the Haskell backend, and instead of testing the program with a randomly generated set of inputs, it will be executed symbolically.

- **Community outreach: conference talks and workshops**
  We are very happy to be vocal about our work, and present in to the community in an accessible way. We can deliver talks at developer conferences showcasing the semantics and add-on tools, as well as workshops for diverse audiences for hands-on expedience.
