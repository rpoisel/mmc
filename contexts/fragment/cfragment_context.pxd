cdef extern from "include/fragment_context.h":
    ctypedef struct FragmentContext:
        pass

    #FragmentContext* fragment_classifier_new(const char* pFilename)
    FragmentContext* fragment_classifier_new()
    void fragment_classifier_free(FragmentContext* pFragmentContext)
    #int fragment_classifier_classify(FragmentContext* pFragmentContext, const uint8_t* pBuf, int pBufLength);
    int fragment_classifier_classify(FragmentContext* pFragmentContext, 
            int pBufLength)
