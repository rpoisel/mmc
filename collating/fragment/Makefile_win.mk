# Set up the building environment as described in: 
# http://wiki.cython.org/64BitCythonExtensionsOnWindows
# C:\Program Files\Microsoft SDKs\Windows\v7.0>set DISTUTILS_USE_SDK=1
# C:\Program Files\Microsoft SDKs\Windows\v7.0>setenv /x64 /release

LIBFRAGMENT_CLASSIFIER=libfragment_classifier
FRAGMENT_CONTEXT=fragment_context

all: $(FRAGMENT_CONTEXT)
    move build\lib.win-amd64-2.7\fragment_context.pyd . 

$(FRAGMENT_CONTEXT): $(LIBFRAGMENT_CLASSIFIER).dll
    python setup.py build_ext 

$(LIBFRAGMENT_CLASSIFIER).dll: 
    cl src\fragment_classifier.c src\ncd.c /Iinclude /I. lib\zlib-1.2.5\dllx64\zlibwapi.lib /link /DLL /out:$(LIBFRAGMENT_CLASSIFIER).dll
    
clean:
    del $(LIBFRAGMENT_CLASSIFIER).* *.obj *.pyd
    rmdir /S /Q build
