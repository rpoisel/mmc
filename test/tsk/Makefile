RM=rm
GCC=gcc
LDFLAGS=-ltsk3
CFLAGS=-g -Wall

OBJ=tsk_test.o \

BIN=tsk_test

all: $(BIN)

$(BIN): $(OBJ)
	$(GCC) -o $(BIN) $(LDFLAGS) $(OBJ)

%.o: %c
	$(GCC) -c -o $< $@

.PHONY: all clean

clean:
	-$(RM) $(BIN) *.o

