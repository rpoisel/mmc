SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.

LBITS := $(shell getconf LONG_BIT)

# ================ START FRAGMENT CLASSIFIER =================
BIN_FRAGMENT_CLASSIFIER=$(OUT_DIR)/libfragment_classifier.so
OBJ_FRAGMENT_CLASSIFIER=$(BUILD_DIR)/logging.o \
			$(BUILD_DIR)/fragment_classifier.o \
			$(BUILD_DIR)/fragment_collection.o \
			$(BUILD_DIR)/block_collection.o \
			$(BUILD_DIR)/block_reader.o \
			$(BUILD_DIR)/entropy/entropy.o \

CFLAGS_FRAGMENT_CLASSIFIER=$(CFLAGS) -fPIC \
			   -Iinclude/entropy \
			   -Iinclude/magic

ifeq ($(LBITS),64)
    LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm \
	-lpthread -Llib/magic/linux-x86_64 -lmagic #-lsvm
else
    LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm \
	-lpthread -Llib/magic/linux-i686 -lmagic #-lsvm
endif
# ================= END FRAGMENT CLASSIFIER ==================

# ================ START DATA SNIFFER =================
LDFLAGS_DATA_SNIFFER=
ifeq ($(LBITS),64)
    LDFLAGS_DATA_SNIFFER=-lm \
	-lpthread -Llib/magic/linux-x86_64 -lmagic #-lsvm
else
    LDFLAGS_DATA_SNIFFER=-lm \
	-lpthread -Llib/magic/linux-i686 -lmagic #-lsvm
endif
OBJ_DATA_SNIFFER=$(BUILD_DIR)/data_sniffer.o \
		 $(BUILD_DIR)/logging.o \
		 $(BUILD_DIR)/fragment_classifier.o \
		 $(BUILD_DIR)/fragment_collection.o \
		 $(BUILD_DIR)/block_collection.o \
		 $(BUILD_DIR)/entropy/entropy.o \

BIN_DATA_SNIFFER=$(OUT_DIR)/data_sniffer
# ================= END DATA SNIFFER ==================

