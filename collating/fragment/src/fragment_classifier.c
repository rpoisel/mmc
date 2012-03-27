#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <math.h>

#ifndef _MSC_VER
#include <magic.h>
#endif

#include "fragment_classifier.h"
#include "entropy/entropy.h"

#define DEBUG 0
/* turn to 1 for verbose messages */
#define VERBOSE 0
#define MAX_FILETYPES 24

struct _FragmentClassifier
{
    unsigned mFragmentSize;
    ClassifyT mFileTypes[MAX_FILETYPES];
    unsigned mNumFileTypes;
};

typedef struct 
{
    FragmentClassifier* handle_fc;
    fragment_cb callback;
    void* callback_data;
    int result;
    char path_image[MAX_STR_LEN];
    unsigned long long offset_img;
    unsigned long long offset_fs;
    unsigned long long num_frags;
#ifndef _MSC_VER
    const char* mPathMagic;
#endif
} thread_data;

void* classify_thread(void* pData);

FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize)
{
    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;

    /* initialize fields that are not used regularely with
     * illegal values */
    lHandle->mNumFileTypes = 0;

    return lHandle;
}

FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize,
        ClassifyT* pTypes,
        unsigned pNumTypes)
{
    struct _FragmentClassifier* lHandle = fragment_classifier_new(
            pOptions,
            pNumSo,
            pFragmentSize);

    /* initialize additional fields */
    memcpy(lHandle->mFileTypes, pTypes, sizeof(ClassifyT) * pNumTypes);
    lHandle->mNumFileTypes = pNumTypes;

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    /* free handle resources */
    free(pFragmentClassifier);
}

int fragment_classifier_classify_result(FragmentClassifier* pFragmentClassifier, 
#ifndef _MSC_VER
        magic_t pMagic, 
#endif
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult)

{
#ifndef _MSC_VER
    const char* lMagicResult = NULL;
#endif
    float lEntropy = 0;
    /* non-relevant fragment <= 0 > relevant fragment */

    pResult->mType = FT_UNKNOWN;
    pResult->mStrength = 0;
    pResult->mIsHeader = 0;

    if (pLen == 0)
    {
        return 0;
    }

#ifndef _MSC_VER
    /* signature checking */
    if (pMagic != NULL)
    {
        lMagicResult = magic_buffer(pMagic, pFragment, pLen);
        if (strcmp(lMagicResult, "data") != 0)
        {
            if (strstr(lMagicResult, "text") != NULL)
            {
                /* do not do anything yet */
            }
            else if (strstr(lMagicResult, "video") != NULL)
            {
                pResult->mType = FT_VIDEO;
                pResult->mStrength = 1;
                pResult->mIsHeader = 1;
            }
            else if (strstr(lMagicResult, "image") != NULL)
            {
                pResult->mType = FT_IMAGE;
                pResult->mStrength = 1;
                pResult->mIsHeader = 1;
            }
        }
    }
    if (pResult->mType == FT_UNKNOWN)
#endif

    /* statistical examination */
    {
        lEntropy = calc_entropy(pFragment, pLen);
        if (lEntropy > 0.625) /* empiric value ;-) */
        {
            pResult->mType = FT_HIGH_ENTROPY;
            pResult->mStrength = 1;
        }
    }

    return pResult->mStrength;
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    ClassifyT lResult;
    int lCnt = 0;

    fragment_classifier_classify_result(pFragmentClassifier,
#ifndef _MSC_VER
            NULL, 
#endif
            pFragment, 
            pLen, 
            &lResult);

    if (lResult.mStrength)
    {
        if (pFragmentClassifier->mNumFileTypes > 0)
        {
            for (lCnt = 0; lCnt < pFragmentClassifier->mNumFileTypes; ++lCnt)
            {
                if (pFragmentClassifier->mFileTypes[lCnt].mType == lResult.mType)
                {
                    /* relevant fragment */
                    return 1;
                }
            }
        }
        else
        {
            return 1;
        }
    }

    /* irrelevant fragment */
    return 0;
}

#ifndef _MSC_VER
int fragment_classifier_classify_mt(FragmentClassifier* pFragmentClassifier, 
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, 
        unsigned long long pSizeReal,
        const char* pPathMagic, 
        unsigned int pNumThreads
        )
{
    pthread_t* lThreads = NULL;
    int lCnt = 0;
    thread_data* lData = NULL;
    unsigned long long lSize = pSizeReal * pFragmentClassifier->mFragmentSize - pOffset;
    unsigned long long lFragsTotal = lSize / pFragmentClassifier->mFragmentSize;
    unsigned long long lFragsPerCpu = ceill(((long double)lFragsTotal)/pNumThreads);
    unsigned long long lFragsPerCpuR = lFragsTotal % lFragsPerCpu;

    /* TODO check return value */
    lThreads = (pthread_t* )malloc(sizeof(pthread_t) * pNumThreads);
    lData = (thread_data* )malloc(sizeof(thread_data) * pNumThreads);
    
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        strncpy((lData + lCnt)->path_image, pImage, MAX_STR_LEN);
        (lData + lCnt)->handle_fc = pFragmentClassifier;
        (lData + lCnt)->callback = pCallback;
        (lData + lCnt)->callback_data = pCallbackData; 
        (lData + lCnt)->mPathMagic = pPathMagic;
        if (lCnt == pNumThreads - 1 && lFragsPerCpuR > 0)
        {
            (lData + lCnt)->num_frags = lFragsPerCpuR;
        }
        else
        {
            (lData + lCnt)->num_frags = lFragsPerCpu;
        }
#if 0
        (lData + lCnt)->offset_img = 
            lCnt * lFragsPerCpu * pFragmentClassifier->mFragmentSize + pOffset;
#else
        (lData + lCnt)->offset_img = lCnt * lFragsPerCpu;
        (lData + lCnt)->offset_fs = pOffset;
#endif

        pthread_create((lThreads + lCnt), NULL, 
                classify_thread, (void*)(lData + lCnt));
    }

    /* join threads */
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        pthread_join(*(lThreads + lCnt), NULL);
    }

    free(lData);
    free(lThreads);

    return EXIT_SUCCESS;
}

void* classify_thread(void* pData)
{
    thread_data* lData = (thread_data*)pData; 
    int lLen = lData->handle_fc->mFragmentSize;
    unsigned long long lCntBlock = lData->offset_img;
    FILE* lImage = NULL;
    unsigned char* lBuf = NULL;
    ClassifyT lResult = { 0, 0, 0 };
    int lCnt = 0;

#ifndef _MSC_VER
    magic_t lMagic = magic_open(MAGIC_NONE);
    if (!lMagic)
    {
        printf("Could not load library\n");
    }
    /* TODO load proper file */
    if (magic_load(lMagic, lData->mPathMagic))
    {
        printf("%s\n", magic_error(lMagic));
    }
#endif

#if DEBUG == 1
    printf("Offset: %lld\n", lData->offset_img * lData->handle_fc->mFragmentSize + lData->offset_fs);
#endif

    lBuf = (unsigned char*)malloc(lData->handle_fc->mFragmentSize);
    lImage = fopen(lData->path_image, "r");
    fseek(lImage, lData->offset_img * lData->handle_fc->mFragmentSize + lData->offset_fs, SEEK_SET);

    /* classify fragments */
    while (lLen == lData->handle_fc->mFragmentSize && 
            (lCntBlock - lData->offset_img) < lData->num_frags)
    {
        lLen = fread(lBuf, 1, lData->handle_fc->mFragmentSize, lImage);
        fragment_classifier_classify_result(lData->handle_fc, lMagic, lBuf, lLen,
                &lResult);
        /* do something with the classification result */
        if (lData->handle_fc->mNumFileTypes == 0)
        {
            lData->callback(lData->callback_data, lCntBlock, 
                    lResult.mType, lResult.mStrength, lResult.mIsHeader);
        }
        else
        {
            for (lCnt = 0; lCnt < lData->handle_fc->mNumFileTypes; ++lCnt)
            {
                if (lData->handle_fc->mFileTypes[lCnt].mType == lResult.mType)
                {
                    /* relevant fragment */
                    lData->callback(lData->callback_data, lCntBlock, 
                            lResult.mType, lResult.mStrength, lResult.mIsHeader);
                    break;
                }
            }
        }
        lCntBlock++;
    }

    fclose(lImage);
    free(lBuf);
#ifndef _MSC_VER
    magic_close(lMagic);
#endif

    return NULL;
}
#endif
