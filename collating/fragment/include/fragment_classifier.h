#ifndef __FRAGMENT_CLASSIFIER_H__
#define __FRAGMENT_CLASSIFIER_H__ 1

#define MAX_STR_LEN 256

typedef enum _FileType
{
    FT_NONE = 0, 
    FT_TXT, 
    FT_HTML, 
    FT_XML, 
    FT_JPG, 
    FT_DOC, 
    FT_PDF, 
    FT_H264, 
} FileType;

typedef struct _ResultClassify
{
    FileType mType;
    int mStrength;
} ResultClassify;

ResultClassify example(void);

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

__declspec(dllexport) FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned int pNumOptions, 
        unsigned int pFragmentSize);

__declspec(dllexport) void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

__declspec(dllexport) int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

typedef FragmentClassifier* (*fc_new_ptr)(ClassifyOptions* pOptions, 
        unsigned int pNumSo, 
        unsigned int pFragmentSize);
typedef void (*fc_free_ptr)(FragmentClassifier* pFragmentClassifier);
typedef int (*fc_classify_ptr)(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

#endif /* __FRAGMENT_CLASSIFIER_H__ */
