#ifndef __BLOCK_CLASSIFIER_H__
#define __BLOCK_CLASSIFIER_H__ 1

#define MAX_STR_LEN 256
#define NUM_THREADS_DEFAULT 1
#define MAX_FILETYPES 24

#include <magic.h>
#if defined __linux__
#define PATH_MAGIC "collating/fragment/data/magic/media.mgc"
#elif defined _WIN32 || defined _WIN64
#define PATH_MAGIC "collating\\fragment\\data\\magic\\media.mgc"
#endif

/* data types */
typedef enum _FileType
{
    FT_JPG = 0, 
    FT_PNG,
    FT_DOC,
    FT_XLS,
    FT_PDF, 
    FT_H264, 
    FT_MP3, 
    FT_ZIP,
    FT_RAR,
    FT_TXT,
    FT_HTML,
    FT_XML, 
    FT_UNKNOWN,
    FT_HIGH_ENTROPY,
    FT_LOW_ENTROPY,
    FT_VIDEO,
    FT_IMAGE,
} FileType;

typedef struct _ClassifyT
{
    FileType mType;
    int mStrength;
    int mIsHeader;
    char mInfo[MAX_STR_LEN];
} ClassifyT;

struct _BlockClassifier
{
    unsigned mFragmentSize;
    ClassifyT mFileTypes[MAX_FILETYPES];
    unsigned mNumFileTypes;
};

typedef struct _BlockClassifier BlockClassifier;

typedef struct _ClassifyOptions
{
    char mOption1[MAX_STR_LEN];
    char mOption2[MAX_STR_LEN];
    char mOption3[MAX_STR_LEN];
    char mOption4[MAX_STR_LEN];
    char mOption5[MAX_STR_LEN];
    struct _ClassifyOptions* mSubOptions;
} ClassifyOptions;

typedef int (*fragment_cb)(
        void* pCallbackData, unsigned long long pOffset, unsigned pSizeRange,
        FileType pType, int pStrength, int pIsHeader, char* pInfo
        );

void callback_selective(BlockClassifier* pBlockClassifier,
    fragment_cb pCallback,
    void* pCallbackData,
    unsigned long long pCntBlock,
    unsigned pSizeRange, 
    ClassifyT pResult);

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

/* function declarations */
__declspec(dllexport) BlockClassifier* block_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumOptions, 
        unsigned pFragmentSize);

__declspec(dllexport) BlockClassifier* block_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned pNumOptions, 
        unsigned pFragmentSize,
        ClassifyT* pTypes,
        unsigned pNumTypes);

__declspec(dllexport) void block_classifier_free(BlockClassifier* pBlockClassifier);

__declspec(dllexport) int block_classifier_classify_result(BlockClassifier* pBlockClassifier, 
        magic_t pMagic, 
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult);

__declspec(dllexport) int block_classifier_classify(BlockClassifier* pBlockClassifier, 
        const unsigned char* pFragment,
        int pLen);

__declspec(dllexport) int block_classify_nofs_mt(BlockClassifier* pBlockClassifier, 
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, 
        unsigned long long pSizeReal, 
        const char* pPathMagic, 
        unsigned int pNumThreads);

#endif /* __BLOCK_CLASSIFIER_H__ */
