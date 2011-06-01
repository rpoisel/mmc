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
OUT_DIR=contexts
BIN_FRAGMENT_CONTEXT=$(OUT_DIR)/fragment/libfragment_context.so
SRC_FRAGMENT_CONTEXT=fragment_context.c
OBJ_FRAGMENT_CONTEXT=$(SRC_FRAGMENT_CONTEXT:%.c=%.o)
CFLAGS_FRAGMENT_CONTEXT=-fPIC
LDFLAGS_FRAGMENT_CONTEXT=-shared -Wl,-soname,

BIN_FRAG_MM_META=$(OUT_DIR)/media/frag_mm_meta_context
SRC_FRAG_MM_META=frag_mm_meta_context.cpp
OBJ_FRAG_MM_META=$(SRC_FRAG_MM_META:%.cpp=%.o)


all: $(BIN_FRAG_MM_META) $(BIN_FRAGMENT_CONTEXT)
	
$(BIN_FRAG_MM_META): init $(BUILD_DIR)/$(OBJ_FRAG_MM_META)
	$(CXX) -o $(BIN_FRAG_MM_META) $(BUILD_DIR)/$(OBJ_FRAG_MM_META) $(LDFLAGS)

$(BUILD_DIR)/$(OBJ_FRAG_MM_META): $(SRC_DIR)/$(SRC_FRAG_MM_META)
	$(CXX) -c $(CXXFLAGS) -o $@ $<

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
	$(RM) $(RMFLAGS) $(BIN_FRAG_MM_META)
	$(RM) $(RMFLAGS) $(BIN_FRAGMENT_CONTEXT)

