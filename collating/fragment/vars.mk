SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.
BIN_FRAGMENT_CLASSIFIER=$(OUT_DIR)/libfragment_classifier.so
OBJ_FRAGMENT_CLASSIFIER=$(BUILD_DIR)/fragment_classifier.o \
			$(BUILD_DIR)/ncd.o
CFLAGS_FRAGMENT_CLASSIFIER=-fPIC
LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname,
OBJ_TEST_NCD=$(BUILD_DIR)/ncd.o \
	     $(BUILD_DIR)/test_ncd.o
BIN_TEST_NCD=$(OUT_DIR)/test_ncd


