SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.

# ================ START =================
BIN_FRAGMENT_CLASSIFIER=$(OUT_DIR)/libfragment_classifier.so
OBJ_FRAGMENT_CLASSIFIER=$(BUILD_DIR)/fragment_classifier.o
CFLAGS_FRAGMENT_CLASSIFIER=$(CFLAGS) -fPIC
LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname,
# ================= END ==================

# ================ START NCD =================
BUILD_DIR_NCD=$(BUILD_DIR)/ncd
SRC_DIR_NCD=$(SRC_DIR)/ncd
BIN_FRAGMENT_CLASSIFIER_NCD=$(OUT_DIR)/libfragment_classifier_ncd.so
OBJ_FRAGMENT_CLASSIFIER_NCD=$(BUILD_DIR_NCD)/fragment_classifier_ncd.o \
			$(BUILD_DIR_NCD)/ncd.o
CFLAGS_FRAGMENT_CLASSIFIER_NCD=$(CFLAGS) -fPIC -Iinclude/ncd
LDFLAGS_FRAGMENT_CLASSIFIER_NCD=-lz -shared -Wl,-soname,
LDFLAGS_TEST_NCD=-lz
OBJ_TEST_NCD=$(BUILD_DIR_NCD)/ncd.o \
	     $(BUILD_DIR_NCD)/test_ncd.o
BIN_TEST_NCD=$(OUT_DIR)/test_ncd
# ================= END NCD ==================

# ================ START SKEL =================
BUILD_DIR_SKEL=$(BUILD_DIR)/skel
SRC_DIR_SKEL=$(SRC_DIR)/skel
BIN_FRAGMENT_CLASSIFIER_SKEL=$(OUT_DIR)/libfragment_classifier_skel.so
OBJ_FRAGMENT_CLASSIFIER_SKEL=$(BUILD_DIR_SKEL)/fragment_classifier_skel.o 
CFLAGS_FRAGMENT_CLASSIFIER_SKEL=$(CFLAGS) -fPIC -Iinclude/skel
LDFLAGS_FRAGMENT_CLASSIFIER_SKEL=-shared -Wl,-soname,
# ================= END SKEL ==================

# ================ START DATA SNIFFER =================
LDFLAGS_DATA_SNIFFER=-L. -lfragment_classifier
OBJ_DATA_SNIFFER=$(BUILD_DIR)/data_sniffer.o
BIN_DATA_SNIFFER=$(OUT_DIR)/data_sniffer
# ================= END DATA SNIFFER ==================

