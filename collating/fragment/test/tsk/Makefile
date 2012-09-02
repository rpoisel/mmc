RM=rm
CC=gcc
LDFLAGS=-ltsk3
CFLAGS=-g -Wall -I../../include

OBJ=tsk_test.o \

BIN=tsk_test
SRC_LOGGING=../../src/logging.c
OBJ_LOGGING=logging.o

all: $(BIN)

$(BIN): $(OBJ) $(OBJ_LOGGING)
	$(CC) -o $(BIN) $(LDFLAGS) $(OBJ) $(OBJ_LOGGING)

$(OBJ_LOGGING): $(SRC_LOGGING)
	$(CC) -c -o $(OBJ_LOGGING) $(CFLAGS) $(SRC_LOGGING)

%.o: %c
	$(CC) -c -o $< $@

.PHONY: all clean

clean:
	-$(RM) $(BIN) *.o

