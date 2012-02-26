cdef extern from *:
    ctypedef char * const_char_ptr "const char*"

cdef extern from "include/fragment_classifier.h":
    ctypedef struct FragmentClassifier:
        pass

    void fragment_classifier_free(FragmentClassifier * pFragmentClassifier)
    int fragment_classifier_classify(
            FragmentClassifier * pFragmentClassifier,
            unsigned char * pBuf,
            int pLen)

cdef extern from "include/fragment_classifier_mmc.h":
    FragmentClassifier * fragment_classifier_mmc(char * pFragsRefDir,
                    unsigned int pFragmentSize)
