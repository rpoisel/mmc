RM=del
CC=cl
LDFLAGS=-ltsk3
CFLAGS=-g -Wall

SRC=tsk_test.c
OBJ=tsk_test.obj
BIN=tsk_test.exe

all: $(BIN)

$(OBJ): $(SRC)
	cl \
		/nologo \
		/W3 \
		/DNDEBUG \
		/D"WIN32" \
		/D"_CONSOLE" \
		/I..\..\include \
		/c \
		$(SRC) \
		/Fo$(OBJ)

$(BIN): $(OBJ)
	link \
		/subsystem:windows \
		/NODEFAULTLIB:MSVCRT \
		/MACHINE:x64 \
		/NXCOMPAT \
		/LTCG \
		/INCREMENTAL:NO \
		/SUBSYSTEM:CONSOLE \
		/LIBPATH:"C:\dev\sleuthkit-4.0.0b1\win32\Release" \
		/LIBPATH:"C:\dev\libewf-20120813\msvscpp\Release" \
		/out:$(BIN) \
		zlib.lib \
		libewf.lib \
		libtsk.lib \
		$(OBJ)

notused: $(OBJ)
	link \
		/subsystem:windows \
		/MACHINE:x86 \
		/NODEFAULTLIB:MSVCRT \
		/SUBSYSTEM:WINDOWS \
		/LIBPATH:"..\..\lib\tsk\win32" \
		/out:$(BIN) \
		libtsk.lib \
		gdi32.lib \
		user32.lib \
		kernel32.lib \
		$(OBJ)

.PHONY: all clean

clean:
	-$(RM) $(BIN) *.obj

