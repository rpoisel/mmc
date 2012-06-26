SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.

LBITS := $(shell getconf LONG_BIT)

# ================ START FRAGMENT CLASSIFIER =================
BIN_FRAGMENT_CLASSIFIER=$(OUT_DIR)/libfragment_classifier.so
OBJ_FRAGMENT_CLASSIFIER= $(BUILD_DIR)/fragment_classifier.o \
			 $(BUILD_DIR)/entropy/entropy.o
CFLAGS_FRAGMENT_CLASSIFIER=$(CFLAGS) -fPIC -Iinclude/entropy
ifeq ($(LBITS),64)
    LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm \
	-lpthread -Llib/magic/linux-x86_64 -lmagic #-lsvm
else
    LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm \
	-lpthread -Llib/magic/linux-i686 -lmagic #-lsvm
endif
# ================= END FRAGMENT CLASSIFIER ==================

# ================ START BLOCK READER =================
BIN_BLOCK_READER=$(OUT_DIR)/libblock_reader.so
OBJ_BLOCK_READER= $(BUILD_DIR)/block_reader.o \
		  $(BUILD_DIR)/fragment_collection.o
CFLAGS_BLOCK_READER=$(CFLAGS) -fPIC
LDFLAGS_BLOCK_READER=-shared -Wl,-soname, -L. \
		     -lfragment_classifier \
		     -lblock_collection
# ================= END BLOCK READER ==================

# ================ START BLOCK COLLECTION =================
BIN_BLOCK_COLLECTION=$(OUT_DIR)/libblock_collection.so
OBJ_BLOCK_COLLECTION= $(BUILD_DIR)/block_collection.o
CFLAGS_BLOCK_COLLECTION=$(CFLAGS) -fPIC
LDFLAGS_BLOCK_COLLECTION=-shared -Wl,-soname,
# ================= END BLOCK COLLECTION ==================

# ================ START DATA SNIFFER =================
LDFLAGS_DATA_SNIFFER=-L. -lfragment_classifier
OBJ_DATA_SNIFFER=$(BUILD_DIR)/data_sniffer.o \
		 $(BUILD_DIR)/block_collection.o
BIN_DATA_SNIFFER=$(OUT_DIR)/data_sniffer
# ================= END DATA SNIFFER ==================

