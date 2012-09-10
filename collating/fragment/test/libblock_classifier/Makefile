RM=rm
CC=gcc
LDFLAGS=-ltsk3
CFLAGS=-g -Wall -I../../include

OBJ=classifier_test.o \

BIN=classifier_test.bin
LIB_CLASSIFIER_DIR=../..
LIB_CLASSIFIER_SO=libblock_classifier.so
LDFLAGS_CLASSIFIER=-L$(LIB_CLASSIFIER_DIR) -lblock_classifier

all: $(BIN)

$(BIN): $(LIB_CLASSIFIER_DIR)/$(LIB_CLASSIFIER_SO) $(OBJ)
	$(CC) -o $(BIN) $(LDFLAGS_CLASSIFIER) $(LDFLAGS) $(OBJ)

$(LIB_CLASSIFIER_DIR)/$(LIB_CLASSIFIER_SO):
	$(MAKE) -C $(LIB_CLASSIFIER_DIR)

%.o: %c
	$(CC) -c -o $< $@

.PHONY: all clean

clean:
	-$(RM) $(BIN) *.o

