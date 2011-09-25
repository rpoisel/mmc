# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

CC=gcc
CXX=g++
PYTHON=python
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl -lpthread -lz
MKDIR=mkdir
RM=rm
RMFLAGS=-rf

SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.
BIN_FRAGMENT_CLASSIFIER=$(OUT_DIR)/libfragment_classifier.so
OBJ_FRAGMENT_CLASSIFIER=$(BUILD_DIR)/fragment_classifier.o \
			$(BUILD_DIR)/ncd.o
OBJ_TEST_NCD=$(BUILD_DIR)/ncd.o \
	     $(BUILD_DIR)/test_ncd.o
BIN_TEST_NCD=$(OUT_DIR)/test_ncd
PYTHON_FLAGS_FRAGMENT_CONTEXT=build_ext -i
CFLAGS_FRAGMENT_CLASSIFIER=-fPIC
LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname,
CLEANUP_FILES=\
	      fragment_context.c \
	      fragment_context.so \
	      libfragment_classifier.so \

all:  $(BIN_FRAGMENT_CLASSIFIER)
	$(PYTHON) setup.py $(PYTHON_FLAGS_FRAGMENT_CONTEXT)
$(BIN_FRAGMENT_CLASSIFIER): init $(OBJ_FRAGMENT_CLASSIFIER)
	$(CC) $(LDFLAGS_FRAGMENT_CLASSIFIER) $(LDFLAGS) -o $(BIN_FRAGMENT_CLASSIFIER) $(OBJ_FRAGMENT_CLASSIFIER)

$(BIN_TEST_NCD): init $(OBJ_TEST_NCD)
	$(CC) $(LDFLAGS) -o $(BIN_TEST_NCD) $(OBJ_TEST_NCD)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) -c $(CFLAGS) $(CFLAGS_FRAGMENT_CLASSIFIER) -o $@ $<
init:
	@if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	@if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi

.PHONY: clean

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(BIN_FRAGMENT_CLASSIFIER)
	$(RM) $(RMFLAGS) $(BIN_TEST_NCD)
	$(RM) $(RMFLAGS) $(CLEANUP_FILES)

