# Set up the building environment: 
# C:\Program Files\Microsoft SDKs\Windows\v7.0>setenv /x64 /release

# ================ START =================
FRAGMENT_CLASSIFIER=libfragment_classifier
#CFLAGS_FRAGMENT_CLASSIFIER=$(CFLAGS) -fPIC -Iinclude/entropy
#LDFLAGS_FRAGMENT_CLASSIFIER=-shared -Wl,-soname, -lm -lpthread -lmagic #-lsvm
# ================= END ==================

$(FRAGMENT_CLASSIFIER).dll: 
	cl /c src\fragment_classifier.c /Iinclude /Iinclude\pthreads /Iinclude\magic
	cl /c src\entropy\entropy.c /Iinclude\entropy /Iinclude
	link fragment_classifier.obj entropy.obj /DLL /out:$(FRAGMENT_CLASSIFIER).dll

# ================ START =================
BLOCK_COLLECTION=libblock_collection
#CFLAGS_BLOCK_COLLECTION=$(CFLAGS) -fPIC
#LDFLAGS_BLOCK_COLLECTION=-shared -Wl,-soname,
# ================= END ==================

$(BLOCK_COLLECTION).dll:
	cl /c src\block_collection.c /Iinclude
	link block_collection.obj /DLL /out:$(BLOCK_COLLECTION).dll

# ================ START =================
BLOCK_READER=libblock_reader
#CFLAGS_BLOCK_READER=$(CFLAGS) -fPIC
#LDFLAGS_BLOCK_READER=-shared -Wl,-soname, -L. -lfragment_classifier -lblock_collection
# ================= END ==================

$(BLOCK_READER).dll: $(BLOCK_COLLECTION).dll $(FRAGMENT_CLASSIFIER).dll
	cl /c src\block_reader.c /Iinclude /Iinclude\magic
	cl /c src\fragment_collection.c /Iinclude
	link $(BLOCK_COLLECTION).lib $(FRAGMENT_CLASSIFIER).lib block_reader.obj fragment_collection.obj /DLL /out:$(BLOCK_READER).dll

# ================ START DATA SNIFFER =================
LDFLAGS_DATA_SNIFFER=-L. -lfragment_classifier
OBJ_DATA_SNIFFER=$(BUILD_DIR)/data_sniffer.o \
		 $(BUILD_DIR)/block_collection.o
BIN_DATA_SNIFFER=$(OUT_DIR)/data_sniffer
# ================= END DATA SNIFFER ==================

all: $(BLOCK_READER).dll

clean:
	del $(FRAGMENT_CLASSIFIER).* $(BLOCK_READER).* $(BLOCK_COLLECTION).* *.obj
