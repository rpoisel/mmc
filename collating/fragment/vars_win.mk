# standard: compile for 64 bit windows
LBITS := 64

SRC_DIR=src/pipe
BUILD_DIR=build/pipe/$(LBITS)
OUT_DIR=lib/pipe/dll$(LBITS)

# ================ START FRAGMENT CLASSIFIER =================
BIN_LIBPIPE=$(OUT_DIR)/libpipe.dll
IMPLIB_LIBPIPE=$(OUT_DIR)/libpipe.la
OBJ_LIBPIPE=$(BUILD_DIR)/pipe.o \

CFLAGS_LIBPIPE=$(CFLAGS) -Wall -Wextra -Wpointer-arith \
			   -fstrict-aliasing -std=c99 \
			   -DFORTIFY_SOURCE=2 -pipe -pedantic \
			   -Iinclude/pipe

LDFLAGS_LIBPIPE=-shared -Wl,--out-implib,$(IMPLIB_LIBPIPE)

ifeq ($(LBITS),64)
CC=x86_64-w64-mingw32-gcc
CXX=x86_64-w64-mingw32-g++
else
CC=i686-w64-mingw32-gcc
CXX=i686-w64-mingw32-g++
endif
# ================= END FRAGMENT CLASSIFIER ==================

