cdef extern from "include/fragment_classifier.h":
    ctypedef struct FragmentClassifier:
        pass

    #FragmentClassifier* fragment_classifier_new(const char* pFilename)
    FragmentClassifier* fragment_classifier_new()
    void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
    #int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, const uint8_t* pBuf, int pBufLength);
    int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
            int pBufLength)
