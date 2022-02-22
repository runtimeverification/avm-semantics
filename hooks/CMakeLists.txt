cmake_minimum_required (VERSION 3.13)

execute_process(COMMAND which kompile           OUTPUT_VARIABLE KOMPILE_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND dirname ${KOMPILE_PATH} OUTPUT_VARIABLE K_BIN        OUTPUT_STRIP_TRAILING_WHITESPACE)
set(K_LIB     ${K_BIN}/../lib)
set(K_INCLUDE ${K_BIN}/../include)
list(APPEND CMAKE_MODULE_PATH ${K_LIB}/cmake/kframework)
include(LLVMKompilePrelude)
project (AlgorandClarity CXX)

set(KOMPILED_DIR $ENV{clarity_exec_dir}/$ENV{clarity_main_filename}-kompiled CACHE PATH "Location of definition.kore")
set(KOMPILE_USE_MAIN "main")
set(TARGET_NAME "interpreter")

set (CMAKE_CXX_STANDARD 14)
set (CMAKE_CXX_STANDARD_REQUIRED ON)
set (CMAKE_CXX_EXTENSIONS OFF)

add_executable(interpreter
	$ENV{PLUGIN_SUBMODULE}/plugin-c/plugin_util.cpp
	$ENV{PLUGIN_SUBMODULE}/plugin-c/crypto.cpp
	$ENV{PLUGIN_SUBMODULE}/plugin-c/blake2.cpp
	algorand.cpp
	base.cpp
	mnemonic.cpp
	hooks.cpp)

if(UNIX AND NOT APPLE)
	set(LINK_PROCPS procps)
elseif(APPLE)
	target_include_directories(interpreter
		PUBLIC /usr/local/include
		PUBLIC $ENV{SSL_ROOT}/include
		PUBLIC $ENV{BITCOIN_LIBEXEC}/include)
	target_link_directories(interpreter
		PUBLIC $ENV{SSL_ROOT}/lib
		PUBLIC $ENV{BITCOIN_LIBEXEC}/lib)
endif()

target_include_directories(interpreter
	PUBLIC $ENV{PLUGIN_SUBMODULE}/plugin-c
	PUBLIC ${K_INCLUDE}/kllvm)
target_link_directories(interpreter
	PUBLIC $ENV{LOCAL_LIB})

target_link_libraries(interpreter
	cryptopp secp256k1 ff curl sodium ssl crypto ${LINK_PROCPS})

include(LLVMKompile2)
