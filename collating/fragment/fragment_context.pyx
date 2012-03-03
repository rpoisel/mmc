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

    def __cinit__(self, pFragsRefDir, pFragmentSize):
        self._c_fragment_context = cfragment_context.fragment_classifier_mmc(
                pFragsRefDir, pFragmentSize)
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

    def example(self):
        if self._c_fragment_context is NULL:
            raise MemoryError()
        return cfragment_context.example()
