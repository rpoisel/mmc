#ifndef __FRAGMENT_CLASSIFIER_H__
#define __FRAGMENT_CLASSIFIER_H__ 1

#define MAX_STR_LEN 256

/* data types */
typedef enum _FileType
{
    FT_UNKNOWN = 0, 
    FT_HIGH_ENTROPY, 
    FT_LOW_ENTROPY, 
    FT_TXT, 
    FT_HTML, 
    FT_XML, 
    FT_JPG, 
    FT_PNG,
    FT_DOC, 
    FT_PDF, 
    FT_H264, 
} FileType;

typedef struct _ClassifyT
{
    FileType mType;
    int mStrength;
} ClassifyT;

typedef struct _FragmentClassifier FragmentClassifier;

typedef struct _ClassifyOptions
{
    char mOption1[MAX_STR_LEN];
    char mOption2[MAX_STR_LEN];
    char mOption3[MAX_STR_LEN];
    char mOption4[MAX_STR_LEN];
    char mOption5[MAX_STR_LEN];
    struct _ClassifyOptions* mSubOptions;
} ClassifyOptions;

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

/* function declarations */
__declspec(dllexport) FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumOptions, 
        unsigned pFragmentSize);

__declspec(dllexport) FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned pNumOptions, 
        unsigned pFragmentSize,
        ClassifyT* pTypes,
        unsigned pNumTypes);

__declspec(dllexport) void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

__declspec(dllexport) int fragment_classifier_classify_result(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult);

__declspec(dllexport) int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);
#endif /* __FRAGMENT_CLASSIFIER_H__ */
