# Set up the building environment as described in: 
# http://wiki.cython.org/64BitCythonExtensionsOnWindows
# C:\Program Files\Microsoft SDKs\Windows\v7.0>set DISTUTILS_USE_SDK=1
# C:\Program Files\Microsoft SDKs\Windows\v7.0>setenv /x64 /release

LIBFRAGMENT_CLASSIFIER=libfragment_classifier
FRAGMENT_CONTEXT=fragment_context

all: $(FRAGMENT_CONTEXT)

$(FRAGMENT_CONTEXT): $(LIBFRAGMENT_CLASSIFIER).dll
    python setup.py build_ext -i

$(LIBFRAGMENT_CLASSIFIER).dll: 
    cl /c src\fragment_classifier.c /Iinclude /I. 
    cl /c src\entropy/entropy.c /Iinclude /Iinclude\entropy /I. 
    link fragment_classifier.obj entropy /DLL /out:$(LIBFRAGMENT_CLASSIFIER).dll 
    
clean:
    del $(LIBFRAGMENT_CLASSIFIER).* *.obj *.pyd
	del $(FRAGMENT_CONTEXT).c
    rmdir /S /Q build
