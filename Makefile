# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

CC=gcc
CXX=g++
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl -lpthread
MKDIR=mkdir
RM=rm
RMFLAGS=-rf

SRC_DIR=src
BUILD_DIR=build
OUT_DIR=contexts
BIN_FRAG_MM_META=$(OUT_DIR)/frag_mm_meta_context
SRC_FRAG_MM_META=\
	      frag_mm_meta_context.cpp \

OBJ_FRAG_MM_META=$(SRC_FRAG_MM_META:%.cpp=$(BUILD_DIR)/%.o)

all: $(BIN_FRAG_MM_META)
	
$(BIN_FRAG_MM_META): init $(OBJ_FRAG_MM_META)
	$(CXX) -o $(BIN_FRAG_MM_META) $(OBJ_FRAG_MM_META) $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

init:
	@if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	@if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi

.PHONY: clean

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(BIN_FRAG_MM_META)

