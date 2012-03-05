import struct

cimport cfragment_context

cdef class FileType:
    FT_NONE = 0
    FT_TXT = 1
    FT_HTML = 2
    FT_XML = 3
    FT_JPG = 4
    FT_DOC = 5
    FT_PDF = 6
    FT_H264 = 7

cdef class CFragmentClassifier:

    cdef cfragment_context.FragmentClassifier * _c_fragment_context

# Cython docs, see
# http://groups.google.com/group/cython-users/browse_thread/thread/895500ddbbf1367c?pli=1
# http://stackoverflow.com/questions/6165293/wrap-c-struct-with-array-member-for-access-in-python-swig-cython-ctypes
# http://docs.python.org/library/struct.html
# http://docs.cython.org/src/userguide/extension_types.html

    def __cinit__(self, pOptions, pTypes):
        cdef cfragment_context.ClassifyT lTypes[128]
        lCnt = 0
        for lType in pTypes:
            lTypes[lCnt].mType = lType['mType']
            lTypes[lCnt].mStrength = lType['mStrength']
            lCnt += 1
        self._c_fragment_context = cfragment_context.fragment_classifier_new_ct(
                NULL, 
                0,
                pOptions.fragmentsize,
                lTypes,
                lCnt)
        if self._c_fragment_context is NULL:
            raise MemoryError()

    def __dealloc__(self):
        if self._c_fragment_context is not NULL:
            cfragment_context.fragment_classifier_free(
                    self._c_fragment_context)

    def classify(self, pBuf):
        if self._c_fragment_context is NULL:
            raise MemoryError()
        return cfragment_context.fragment_classifier_classify(
                self._c_fragment_context,
                pBuf,
                len(pBuf))

