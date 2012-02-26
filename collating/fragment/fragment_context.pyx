cimport cfragment_context

cdef class CFragmentClassifier:
    cdef cfragment_context.FragmentClassifier * _c_fragment_context

    def __cinit__(self, pFragsRefDir, pFragmentSize):
        self._c_fragment_context = cfragment_context.fragment_classifier_py(
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
