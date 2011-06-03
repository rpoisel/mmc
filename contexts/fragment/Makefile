# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

CC=gcc
CXX=g++
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl -lpthread
MKDIR=mkdir
RM=rm
RMFLAGS=-rf

SRC_DIR=src
BUILD_DIR=build
OUT_DIR=.
BIN_FRAGMENT_CONTEXT=$(OUT_DIR)/libfragment_context.so
SRC_FRAGMENT_CONTEXT=fragment_context.c
OBJ_FRAGMENT_CONTEXT=$(SRC_FRAGMENT_CONTEXT:%.c=%.o)
CFLAGS_FRAGMENT_CONTEXT=-fPIC
LDFLAGS_FRAGMENT_CONTEXT=-shared -Wl,-soname,

all: $(BIN_FRAGMENT_CONTEXT)
	
$(BIN_FRAGMENT_CONTEXT): init $(BUILD_DIR)/$(OBJ_FRAGMENT_CONTEXT)
	$(CC) $(LDFLAGS_FRAGMENT_CONTEXT) $(LDFLAGS) -o $(BIN_FRAGMENT_CONTEXT) $(BUILD_DIR)/$(OBJ_FRAGMENT_CONTEXT)

$(BUILD_DIR)/$(OBJ_FRAGMENT_CONTEXT): $(SRC_DIR)/$(SRC_FRAGMENT_CONTEXT)
	$(CC) -c $(CFLAGS) $(CFLAGS_FRAGMENT_CONTEXT) -o $@ $<

init:
	@if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	@if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi

.PHONY: clean

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(BIN_FRAGMENT_CONTEXT)

