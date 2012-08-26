CAT=/bin/cat
RM=/bin/rm
RM_FLAGS=-rf
FILE=/usr/bin/file
FILE_FLAGS=--compile --magic-file 

OUT=media

all: animation jpeg png
	$(CAT) animation jpeg png > $(OUT)
	$(FILE) $(FILE_FLAGS) $(OUT)

.PHONY: clean

clean: 
	$(RM) $(RM_FLAGS) $(OUT) *.mgc
