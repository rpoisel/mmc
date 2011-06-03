cdef extern from *:
    ctypedef char* const_char_ptr "const char*"

cdef extern from "include/fragment_classifier.h":
    ctypedef struct FragmentClassifier:
        pass

    FragmentClassifier* fragment_classifier_new(char* pFilename)
    void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
    bint fragment_classifier_classify(
            FragmentClassifier* pFragmentClassifier, 
            unsigned char* pBuf, int pBufLength)
