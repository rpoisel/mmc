# Set up the building environment: 
# C:\Program Files\Microsoft SDKs\Windows\v7.1>setenv /x64 /release /xp

# ================ START =================
SRC_DIR=src
INCLUDE_DIR=include
LOGGING=logging
FRAGMENT_CLASSIFIER=libfragment_classifier
BLOCK_COLLECTION=libblock_collection
BLOCK_READER=libblock_reader
#CFLAGS_FRAGMENT_CLASSIFIER=$(CFLAGS) -fPIC -Iinclude/entropy
#LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm -lpthread -lmagic #-lsvm
# ================= END ==================

all: $(BLOCK_READER).dll

$(LOGGING).obj: $(SRC_DIR)\$(LOGGING).c $(INCLUDE_DIR)\$(LOGGING).h
	cl /c $(SRC_DIR)\logging.c /I$(INCLUDE_DIR)

$(BLOCK_READER).dll: $(BLOCK_COLLECTION).dll $(FRAGMENT_CLASSIFIER).dll $(LOGGING).obj
	cl /c $(SRC_DIR)\block_reader.c /Iinclude /I$(INCLUDE_DIR)\magic
	cl /c $(SRC_DIR)\fragment_collection.c /I$(INCLUDE_DIR)
	link $(BLOCK_COLLECTION).lib $(FRAGMENT_CLASSIFIER).lib $(LOGGING).obj block_reader.obj fragment_collection.obj /DLL /out:$(BLOCK_READER).dll

$(FRAGMENT_CLASSIFIER).dll: $(LOGGING).obj
	cl /c $(SRC_DIR)\fragment_classifier.c /I$(INCLUDE_DIR) /I$(INCLUDE_DIR)\magic
	cl /c $(SRC_DIR)\entropy\entropy.c /I$(INCLUDE_DIR)\entropy /I$(INCLUDE_DIR)
	link .\lib\magic\dll64\magic.lib .\lib\tsk\win32\libtsk.lib \
		$(LOGGING).obj fragment_classifier.obj entropy.obj /DLL /out:$(FRAGMENT_CLASSIFIER).dll
    
# ================ START =================
#CFLAGS_BLOCK_COLLECTION=$(CFLAGS) -fPIC
#LDFLAGS_BLOCK_COLLECTION=-shared -Wl,-soname,
# ================= END ==================

$(BLOCK_COLLECTION).dll: $(LOGGING).obj
	cl /c $(SRC_DIR)\block_collection.c /I$(INCLUDE_DIR)
	link block_collection.obj $(LOGGING).obj /DLL /out:$(BLOCK_COLLECTION).dll

# ================ START =================
#CFLAGS_BLOCK_READER=$(CFLAGS) -fPIC
#LDFLAGS_BLOCK_READER=-shared -Wl,-soname, -L. -lfragment_classifier -lblock_collection
# ================= END ==================

# ================ START DATA SNIFFER =================
LDFLAGS_DATA_SNIFFER=-L. -lfragment_classifier
OBJ_DATA_SNIFFER=$(BUILD_DIR)/data_sniffer.o \
		 $(BUILD_DIR)/block_collection.o
BIN_DATA_SNIFFER=$(OUT_DIR)/data_sniffer
# ================= END DATA SNIFFER ==================

clean:
	del $(FRAGMENT_CLASSIFIER).* $(BLOCK_READER).* $(BLOCK_COLLECTION).* *.obj
