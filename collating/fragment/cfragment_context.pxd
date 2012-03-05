cdef extern from *:
    ctypedef char * const_char_ptr "const char*"

cdef extern from "include/fragment_classifier.h":
    ctypedef enum FileType:
        pass

cdef extern from "include/fragment_classifier.h":
    cdef struct _ClassifyT:
        FileType mType
        int mStrength

ctypedef _ClassifyT ClassifyT

cdef extern from "include/fragment_classifier.h":
    ctypedef struct ClassifyOptions:
        char * mOption1
        char * mOption2
        char * mOption3
        char * mOption4
        char * mOption5
        ClassifyOptions * mSubOptions

cdef extern from "include/fragment_classifier.h":
    ctypedef struct FragmentClassifier:
        pass

cdef extern from "include/fragment_classifier.h":
    void fragment_classifier_free(FragmentClassifier * pFragmentClassifier)

cdef extern from "include/fragment_classifier.h":
    int fragment_classifier_classify(
            FragmentClassifier * pFragmentClassifier,
            unsigned char * pBuf,
            int pLen)

cdef extern from "include/fragment_classifier.h":
    FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned int pNumOptions, 
        unsigned int pFragmentSize,
        ClassifyT* pTypes,
        unsigned int pNumTypes)

