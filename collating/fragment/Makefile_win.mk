# Set up the building environment: 
# C:\Program Files\Microsoft SDKs\Windows\v7.0>setenv /x64 /release

LIBFRAGMENT_CLASSIFIER=libfragment_classifier

all: $(LIBFRAGMENT_CLASSIFIER).dll

$(LIBFRAGMENT_CLASSIFIER).dll: 
    cl /c src\fragment_classifier.c /Iinclude /I. 
    cl /c src\entropy/entropy.c /Iinclude /Iinclude\entropy /I. 
    link fragment_classifier.obj entropy /DLL /out:$(LIBFRAGMENT_CLASSIFIER).dll 
    
clean:
    del $(LIBFRAGMENT_CLASSIFIER).* *.obj
