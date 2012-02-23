# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

include vars.mk

CC=gcc
CXX=g++
PYTHON=python
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl -lpthread -lz
LDFLAGS_CYTHON=-L.
MKDIR=mkdir
RM=rm
RMFLAGS=-rf

all: $(BIN_FRAGMENT_CLASSIFIER) $(BIN_TEST_NCD)

$(BIN_FRAGMENT_CLASSIFIER): init $(OBJ_FRAGMENT_CLASSIFIER)
	$(CC) -o $(BIN_FRAGMENT_CLASSIFIER) $(OBJ_FRAGMENT_CLASSIFIER) $(LDFLAGS_FRAGMENT_CLASSIFIER) $(LDFLAGS) 

$(BIN_TEST_NCD): init $(OBJ_TEST_NCD)
	$(CC) -o $(BIN_TEST_NCD) $(OBJ_TEST_NCD) $(LDFLAGS) 

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) -c $(CFLAGS) $(CFLAGS_FRAGMENT_CLASSIFIER) -o $@ $<

init:
	@if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	@if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(BIN_FRAGMENT_CLASSIFIER)
	$(RM) $(RMFLAGS) $(BIN_TEST_NCD)

