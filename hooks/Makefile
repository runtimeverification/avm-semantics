SOURCE := algorand.cpp base.cpp mnemonic.cpp

OS := $(shell uname -s)

ifeq ($(OS),Darwin)
# On MacOS, brew installed openssl does not end up in system
# locations, so we need to be explicit.
IFLAGS += -I/usr/local/opt/openssl/include
LFLAGS += -L/usr/local/opt/openssl/lib
endif

LIBS   += -lcurl -lcrypto

CC = c++
CCFLAGS += -std=c++14

.cpp.o:
	$(CC) $(CCFLAGS) $(IFLAGS) -c $<

example: $(subst .cpp,.o,$(SOURCE)) example.o
	$(CC) $(CCFLAGS) $(LFLAGS) $^ $(LIBS) -o $@

# Build dependencies, expressed for brew on MacOS
brew-deps:
	brew install libsodium msgpack-gxx openssl

clean:
	rm -f $(subst .cpp,.o,$(SOURCE)) example.o example

algorand.o: algorand.h
base.o: base.h
mnemonic.o: mnemonic.h
example.o: algorand.h
