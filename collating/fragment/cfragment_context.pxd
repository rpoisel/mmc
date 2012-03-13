cdef extern from *:
    ctypedef char * const_char_ptr "const char*"

cdef extern from "include/fragment_classifier.h":
    ctypedef enum FileType:
        pass

    cdef struct _ClassifyT:
        FileType mType
        int mStrength

    ctypedef _ClassifyT ClassifyT

    ctypedef struct ClassifyOptions:
        char * mOption1
        char * mOption2
        char * mOption3
        char * mOption4
        char * mOption5
        ClassifyOptions * mSubOptions

    ctypedef struct FragmentClassifier:
        pass

    void fragment_classifier_free(FragmentClassifier * pFragmentClassifier)

    int fragment_classifier_classify(
            FragmentClassifier * pFragmentClassifier,
            unsigned char * pBuf,
            int pLen)

    FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned int pNumOptions, 
        unsigned int pFragmentSize,
        ClassifyT* pTypes,
        unsigned int pNumTypes)

