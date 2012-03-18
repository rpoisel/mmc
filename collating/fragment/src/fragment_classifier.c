#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#include "fragment_classifier.h"
#include "entropy/entropy.h"

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
    int result;
    char path_image[MAX_STR_LEN];
    /* not used at the moment */
    int offset_img;
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
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult)

{
    float lEntropy = 0;
    /* non-relevant fragment <= 0 > relevant fragment */

    pResult->mType = FT_UNKNOWN;
    pResult->mStrength = 0;

    if (pLen == 0)
    {
        return 0;
    }

    lEntropy = calc_entropy(pFragment, pLen);
    if (lEntropy > 0.625) /* empiric value ;-) */
    {
        pResult->mType = FT_HIGH_ENTROPY;
        pResult->mStrength = 1;
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
            pFragment, 
            pLen, 
            &lResult);

    if (lResult.mStrength)
    {
        if (pFragmentClassifier->mNumFileTypes > 0)
        {
            for (lCnt = 0; lCnt < pFragmentClassifier->mNumFileTypes; lCnt++)
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

int fragment_classifier_classify_mt(FragmentClassifier* pFragmentClassifier, 
        fragment_cb pCallback, 
        const char* pPath)
{
    pthread_t lThread1;
    thread_data lData;
    strncpy(lData.path_image, pPath, MAX_STR_LEN);
    lData.handle_fc = pFragmentClassifier;
    lData.callback = pCallback;

    /* TODO check return value */
    pthread_create(&lThread1, NULL, classify_thread, (void*)&lData);

    /* join threads */
    pthread_join(lThread1, NULL);

    return EXIT_SUCCESS;
}

void* classify_thread(void* pData)
{
    unsigned long long lOffset = 0;
    thread_data* lData = (thread_data*)pData; 
    FILE* lImage = NULL;
    unsigned char* lBuf = NULL;
    int lResult = lData->handle_fc->mFragmentSize;

    lBuf = (unsigned char*)malloc(lData->handle_fc->mFragmentSize);
    lImage = fopen(lData->path_image, "r");

    /* classify fragments */
    while (lResult == lData->handle_fc->mFragmentSize)
    {
        lResult = fread(lBuf, 1, lData->handle_fc->mFragmentSize, lImage);
        lData->result = fragment_classifier_classify(lData->handle_fc, 
                lBuf, lResult);
        /* do something with the result */
        lData->callback(lOffset, lData->result, 0);
        lOffset += lResult;
    }

    fclose(lImage);
    free(lBuf);

    return NULL;
}

