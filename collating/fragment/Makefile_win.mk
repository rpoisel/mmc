# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

include vars_win.mk

#CC=x86_64-w64-mingw32-gcc
#CXX=x86_64-w64-mingw32-g++
PYTHON=python
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=
MKDIR=mkdir
CP=cp
RM=rm
RMFLAGS=-rf

all: $(BIN_LIBPIPE)

$(BIN_LIBPIPE): $(OBJ_LIBPIPE)
	$(CC) -o $(BIN_LIBPIPE) $(LDFLAGS_LIBPIPE) $(LDFLAGS) $(OBJ_LIBPIPE)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c 
	if [ ! -d $(BUILD_DIR) ] ; then $(MKDIR) -p $(BUILD_DIR) ; fi
	if [ ! -d $(OUT_DIR) ] ; then $(MKDIR) -p $(OUT_DIR) ; fi
	$(CC) -c $(CFLAGS) $(CFLAGS_LIBPIPE) -o $@ $<

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(OUT_DIR)

