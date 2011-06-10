RM=rm
GCC=gcc
LDFLAGS=-g -Wall -lz

OBJ=zpipe.o \

BIN = zpipe

all: $(BIN)

$(BIN): $(OBJ)
	$(GCC) -o $(BIN) $(LDFLAGS) $(OBJ)

%.o: %c
	$(GCC) -c -o $< $@

.PHONY: all clean

clean:
	$(RM) $(BIN) *.o

