{
  description = "A flake for the KAVM Semantics";

  inputs = {
    k-framework.url = "github:runtimeverification/k";
    nixpkgs.follows = "k-framework/nixpkgs";
    flake-utils.follows = "k-framework/flake-utils";
    rv-utils.url = "github:runtimeverification/rv-nix-tools";
    poetry2nix.follows = "pyk/poetry2nix";
    blockchain-k-plugin.url =
      "github:runtimeverification/blockchain-k-plugin/8fdc74e3caf254aa3952393dbb0368d2c98c321a";
    blockchain-k-plugin.inputs.flake-utils.follows = "k-framework/flake-utils";
    blockchain-k-plugin.inputs.nixpkgs.follows = "k-framework/nixpkgs";
    # pyk.url = "github:runtimeverification/pyk/v0.1.30";
    pyk.url = "path:/home/sam/git/pyk";
    pyk.inputs.flake-utils.follows = "k-framework/flake-utils";
    pyk.inputs.nixpkgs.follows = "k-framework/nixpkgs";

  };
  outputs = { self, k-framework, nixpkgs, flake-utils, poetry2nix
    , blockchain-k-plugin, rv-utils, pyk }:
    let
      buildInputs = pkgs: k:
        with pkgs; [
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

      overlay = final: prev:
        let
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
              make SHELL=${prev.bash}/bin/bash plugin-deps
            '';

            enableParallelBuilding = true;

            installPhase = ''
              mkdir -p $out
              mv .build/usr/* $out/
            '';
          };
        in {
          inherit kavm-deps;
          kavm = let
            k = k-framework.packages.${prev.system}.k;
            kavm-bin = prev.poetry2nix.mkPoetryApplication {
              python = prev.python310;
              projectDir = ./kavm;
              overrides = prev.poetry2nix.overrides.withDefaults
                (finalPython: prevPython: { pyk = prev.python310Packages.pyk; });
              groups = [ ];
              # We remove `"dev"` from `checkGroups`, so that poetry2nix does not try to resolve dev dependencies.
              checkGroups = [ ];
              propagatedBuildInputs = [ k prev.llvm-backend ];
            };
          in prev.stdenv.mkDerivation {
            pname = "kavm";
            version = self.rev or "dirty";
            buildInputs = with prev; [
              kavm-bin
              cryptopp.dev
              curl.dev
              secp256k1
              msgpack
              openssl.dev
              procps
            ];

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
                --replace '$(MAKE) build -C $(PY_KAVM_DIR)' 'echo "Skip py-kavm"' \
                --replace 'py-kavm $(VENV_DIR)/pyvenv.cfg' ' ' \
                --replace 'plugin-deps $(hook_includes)' '$(hook_includes)'
            '';

            enableParallelBuilding = true;

            buildPhase = ''
              mkdir -p .build/usr/
              cp -r ${kavm-deps}/* .build/usr/
              chmod -R u+w .build/
              make SHELL=${prev.bash}/bin/bash VENV_ACTIVATE=true build
            '';

            installPhase = ''
              mkdir -p $out
              mv .build/usr/* $out/
              ln -s ${k} $out/lib/kavm/kframework
              mkdir $out/bin
              ln -s ${kavm-bin}/bin/kavm $out/bin/
            '';

          };

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
        packages.default = pkgs.kavm;

        apps = {
          compare-profiles = flake-utils.lib.mkApp {
            drv = pkgs.stdenv.mkDerivation {
              name = "compare-profiles";
              src = ./package/nix;
              installPhase = ''
                mkdir -p $out/bin
                cp profile.py $out/bin/compare-profiles
              '';
            };
          };
        };

        packages = {
          inherit (pkgs) kavm kavm-deps;

          check-submodules = rv-utils.lib.check-submodules pkgs {
            inherit k-framework blockchain-k-plugin;
          };

          update-from-submodules =
            rv-utils.lib.update-from-submodules pkgs ./flake.lock {
              k-framework.submodule = "deps/k";
              blockchain-k-plugin.submodule = "deps/plugin";
            };
        };
      }) // {
        overlays.default = nixpkgs.lib.composeManyExtensions [
          k-framework.overlay
          blockchain-k-plugin.overlay
          overlay
        ];
      };
}
