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

OUT_DIR=.
BIN_FRAGMENT_CONTEXT=$(OUT_DIR)/fragment_context.so
PYTHON_FLAGS_FRAGMENT_CONTEXT=setup.py build_ext -i
CLEANUP_FILES=\
	      fragment_context.c \
	      fragment_context.so \

all:$(BIN_FRAGMENT_CONTEXT)
	
$(BIN_FRAGMENT_CONTEXT): $(BIN_FRAGMENT_CLASSIFIER)
	LDFLAGS=$(LDFLAGS_CYTHON) $(PYTHON) $(PYTHON_FLAGS_FRAGMENT_CONTEXT)

$(BIN_FRAGMENT_CLASSIFIER): 
	$(MAKE) -f Makefile $(BIN_FRAGMENT_CLASSIFIER)

.PHONY: clean

clean:
	$(RM) $(RMFLAGS) $(BUILD_DIR)
	$(RM) $(RMFLAGS) $(CLEANUP_FILES)
	$(MAKE) -f Makefile clean

