{
  description = "A flake for the KAVM Semantics";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/b01f185e4866de7c5b5a82f833ca9ea3c3f72fc4";
    k-framework.url = "github:runtimeverification/k";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.url = "github:runtimeverification/rv-nix-tools";
    poetry2nix.follows = "pyk/poetry2nix";
    blockchain-k-plugin.url = "github:runtimeverification/blockchain-k-plugin/f8a93660317c377fc7a16b3d49b0518892354a28";
    blockchain-k-plugin.inputs.flake-utils.follows = "k-framework/flake-utils";
    blockchain-k-plugin.inputs.nixpkgs.follows = "k-framework/nixpkgs";
    pyk.url = "github:runtimeverification/pyk/v0.1.362";
    pyk.inputs.flake-utils.follows = "k-framework/flake-utils";
    pyk.inputs.nixpkgs.follows = "k-framework/nixpkgs";

  };
  outputs = { self, k-framework, nixpkgs, flake-utils, poetry2nix
    , blockchain-k-plugin, rv-utils, pyk }:
    let
      overlay = final: prev:
        let
          k = k-framework.packages.${prev.system}.k;
          kavm-deps = prev.stdenv.mkDerivation {
            pname = "kavm-deps";
            version = self.rev or "dirty";
            buildInputs = with prev; [
              autoconf
              automake
              cmake
              clang
              cryptopp.dev
              gmp
              openssl.dev
              pkg-config
              procps
              libtool
            ];

            src = prev.stdenv.mkDerivation {
              name = "kavm-deps-${self.rev or "dirty"}-src";
              phases = [ "installPhase" ];
              src = ./Makefile;
              installPhase = ''
                mkdir $out
                cp $src $out/Makefile
                chmod -R u+w $out
                mkdir -p $out/deps/plugin
                cp -rv ${prev.blockchain-k-plugin-src}/* $out/deps/plugin/
              '';
            };

            dontUseCmakeConfigure = true;

            buildPhase = ''
              make \
                APPLE_SILICON=${if prev.stdenv.isAarch64 && prev.stdenv.isDarwin then "true" else "false"} \
                SHELL=$SHELL \
                plugin-deps -j$(nproc)
            '';

            enableParallelBuilding = true;

            installPhase = ''
              mkdir -p $out
              mv .build/usr/* $out/
            '';
          };

          kavm = prev.poetry2nix.mkPoetryApplication {
            # buildInputs = [ prev.python311Packages.pip ];
            python = prev.python310;
            projectDir = ./kavm;
            overrides = prev.poetry2nix.overrides.withoutDefaults
              (finalPython: prevPython: {
                 pyk = prev.pyk-python310;
                 pycryptodomex = prevPython.pycryptodomex.overridePythonAttrs
                       (
                         old: {
                           buildInputs = (old.buildInputs or [ ]) ++ [ prevPython.setuptools ];
                         }
                       );
                 pynacl = prevPython.pynacl.overridePythonAttrs
                       (
                         old: {
                           buildInputs = (old.buildInputs or [ ]) ++ [ prevPython.setuptools ];
                         }
                       );
              });
            preferWheels = true;
            # We remove `"dev"` from `checkGroups`, so that poetry2nix does not try to resolve dev dependencies.
            checkGroups = [ ];
            propagatedBuildInputs = [ k prev.llvm-backend ];
          };
        in {
          avm-semantics = prev.stdenv.mkDerivation {
            pname = "avm-semantics";
            version = self.rev or "dirty";
            buildInputs = with prev; [
              kavm
              cryptopp.dev
              curl.dev
              fmt
              secp256k1
              msgpack
              openssl.dev
              procps
              poetry
            ];
            nativeBuildInputs = [ prev.makeWrapper ];

            src = prev.nix-gitignore.gitignoreSourcePure [
              ./.gitignore
              ".github/"
              "result*"
              "*.nix"
              "deps/"
              "kavm/"
            ] ./.;

            dontUseCmakeConfigure = true;

            postPatch = ''
              substituteInPlace ./Makefile \
                --replace 'pip install --editable $(PY_KAVM_DIR)' 'echo "Skip installing kavm with pip"' \
                --replace '$(VENV_DIR)/pyvenv.cfg' ' ' \
                --replace 'plugin-deps $(hook_includes)' '$(hook_includes)'
            '';

            enableParallelBuilding = true;

            buildPhase = ''
              mkdir -p .build/usr/
              cp -r ${kavm-deps}/* .build/usr/
              chmod -R u+w .build/
              make \
                SKIP_POETRY_RUN=1 SHELL=$SHELL VENV_ACTIVATE=true \
                ${if prev.stdenv.isDarwin then "UNAME_S=" else ""} \
                build
            '';

            installPhase = ''
              mkdir -p $out
              mv .build/usr/* $out/
              ln -s ${k} $out/lib/kavm/kframework
            '';
          };
          kavm-deps = kavm-deps;

          # rebuild the kavm executable, giving it the newly determined path to the K definition
          kavm = kavm.overrideAttrs (oldAttrs: {
            buildInputs = oldAttrs.buildInputs or [] ++ [ prev.makeWrapper prev.python311.pkgs.pip ];
            postInstall = oldAttrs.postInstall or "" + ''
              wrapProgram $out/bin/kavm \
                --set KAVM_DEFINITION_DIR ${(toString final.avm-semantics) + "/lib/kavm/avm-llvm/avm-testing-kompiled"} \
                --set KAVM_VERIFICATION_DEFINITION_DIR ${(toString final.avm-semantics) + "/lib/kavm/avm-haskell/verification-kompiled"}
            '';
          });
        };
    in flake-utils.lib.eachSystem [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: { llvm-backend-release = false; })
            k-framework.overlay
            blockchain-k-plugin.overlay
            poetry2nix.overlay
            pyk.overlay
            overlay
          ];
        };
      in {
        packages.default = pkgs.avm-semantics;
        packages = {
          inherit (pkgs) kavm-deps avm-semantics kavm;

          check-submodules = rv-utils.lib.check-submodules pkgs {
            inherit k-framework blockchain-k-plugin;
          };

          update-from-submodules =
            rv-utils.lib.update-from-submodules pkgs ./flake.lock {
              k-framework.submodule = "deps/k";
              blockchain-k-plugin.submodule = "deps/plugin";
            };
        };
        devShell = pkgs.kavm.dependencyEnv.overrideAttrs(old: {
          shellHook = ''
            echo "Welcome to KAVM!"
            export KAVM_DEFINITION_DIR=${(toString pkgs.avm-semantics) + "/lib/kavm/avm-llvm/avm-testing-kompiled"}
            echo KAVM definition is at $KAVM_DEFINITION_DIR
          '';
          });
      }) // {
        overlays.default = nixpkgs.lib.composeManyExtensions [
          k-framework.overlay
          blockchain-k-plugin.overlay
          overlay
        ];
      };
}
