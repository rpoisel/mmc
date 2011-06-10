RM=rm
GCC=gcc
LDFLAGS=-lz
CFLAGS=-g -Wall

OBJ=zbuf.o \

BIN = zbuf

all: $(BIN)

$(BIN): $(OBJ)
	$(GCC) -o $(BIN) $(LDFLAGS) $(OBJ)

%.o: %c
	$(GCC) -c -o $< $@

.PHONY: all clean

clean:
	$(RM) $(BIN) *.o

