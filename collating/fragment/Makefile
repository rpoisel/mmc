# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

include vars_lnx.mk

CC=gcc
CXX=g++
PYTHON=python
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl
MKDIR=mkdir
CP=cp
RM=rm
RMFLAGS=-rf

all: $(BIN_FRAGMENT_CLASSIFIER) $(BIN_DATA_SNIFFER)

$(BIN_FRAGMENT_CLASSIFIER): $(OBJ_FRAGMENT_CLASSIFIER)
	$(CC) -o $(BIN_FRAGMENT_CLASSIFIER) $(OBJ_FRAGMENT_CLASSIFIER) $(LDFLAGS_FRAGMENT_CLASSIFIER) $(LDFLAGS) 

$(BIN_DATA_SNIFFER): $(OBJ_DATA_SNIFFER) $(BIN_FRAGMENT_CLASSIFIER)
	$(CC) -o $(BIN_DATA_SNIFFER) $(OBJ_DATA_SNIFFER) $(LDFLAGS) $(LDFLAGS_DATA_SNIFFER)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c 
	@$(MAKE) init
	$(CC) -c $(CFLAGS) $(CFLAGS_FRAGMENT_CLASSIFIER) $(CFLAGS_BLOCK_READER) -o $@ $<

init:
	@if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	@if [ ! -d $(BUILD_DIR)/entropy ] ; then $(MKDIR) -p $(BUILD_DIR)/entropy ; fi
	@if [ ! -d $(BUILD_DIR)/pipe ] ; then $(MKDIR) -p $(BUILD_DIR)/pipe ; fi
	@if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(BIN_FRAGMENT_CLASSIFIER)
	$(RM) $(RMFLAGS) $(BIN_DATA_SNIFFER)

