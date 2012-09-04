# g++ -g -o HowToUse_Dll HowToUse_Dll.cpp -ldl -lpthread

include vars_lnx.mk

CC=gcc
CXX=g++
PYTHON=python
CFLAGS=-g -Wall -O0 -Iinclude
CXXFLAGS=-g -Wall -O0 -Iinclude
LDFLAGS=-ldl -lpthread
LDFLAGS_CYTHON=-L.
MKDIR=mkdir
RM=rm
RMFLAGS=-rf

all:$(BIN_FRAGMENT_CLASSIFIER) $(BIN_BLOCK_READER)
	
$(BIN_FRAGMENT_CLASSIFIER): 
	$(MAKE) -f Makefile $(BIN_FRAGMENT_CLASSIFIER)

$(BIN_BLOCK_READER): 
	$(MAKE) -f Makefile $(BIN_BLOCK_READER)

.PHONY: clean all $(BIN_FRAGMENT_CLASSIFIER) $(BIN_BLOCK_READER)

clean:
	$(MAKE) -f Makefile clean

