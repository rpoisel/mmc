#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include "os_def.h"

/* for the windows port see the following URL: */
/* http://msdn.microsoft.com/en-us/library/windows/desktop/ms682516(v=vs.85).aspx */
/* http://msdn.microsoft.com/en-us/library/kdzttdcb(v=vs.71).aspx */
#include "magic.h"

#include "logging.h"
#include "block_classifier.h"
#include "entropy/entropy.h"

BlockClassifier* block_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize)
{
    /* initialize handle structure */
    struct _BlockClassifier* lHandle = 
        (struct _BlockClassifier*)malloc(sizeof(struct _BlockClassifier));

    lHandle->mFragmentSize = pFragmentSize;

    /* initialize function pointers to the following functions (windows) */
    /* magic_open, magic_close, magic_load, magic_buffer, magic_error */
    /* see the following URL to learn how to do that: */
    /* http://msdn.microsoft.com/en-us/library/ms686944.aspx */

    /* initialize fields that are not used regularely with
     * illegal values */
    lHandle->mNumFileTypes = 0;

    return lHandle;
}

BlockClassifier* block_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize,
        ClassifyT* pTypes,
        unsigned pNumTypes)
{
    struct _BlockClassifier* lHandle = block_classifier_new(
            pOptions,
            pNumSo,
            pFragmentSize);

    /* initialize additional fields */
    memcpy(lHandle->mFileTypes, pTypes, sizeof(ClassifyT) * pNumTypes);
    lHandle->mNumFileTypes = pNumTypes;

    return lHandle;
}

void block_classifier_free(BlockClassifier* pBlockClassifier)
{
    /* free handle resources */
    free(pBlockClassifier);
}

int block_classifier_classify_result(BlockClassifier* pBlockClassifier, 
        magic_t pMagic, 
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult)
{
        
    const char* lMagicResult = NULL;
    float lEntropy = 0;
    int lCnt = 0;
    int lCntJpeg = 0;
    /* non-relevant fragment <= 0 > relevant fragment */

    pResult->mType = FT_UNKNOWN;
    pResult->mStrength = 0;
    pResult->mIsHeader = 0;
    pResult->mInfo[0] = '\0';
    if (pLen == 0)
    {
        return 0;
    }

    /* signature checking */
    if (pMagic != NULL)
    {
        lMagicResult = magic_buffer(pMagic, pFragment, pLen);

        if (strcmp(lMagicResult, "data") != 0)
        {
            if (strstr(lMagicResult, "text") != NULL)
            {
                pResult->mType = FT_TXT;
                pResult->mStrength = 1;
            }
            /* further distinguish between different text formats */
            /* check for specific video headers */
            else if (strstr(lMagicResult, "H.264") != NULL)
            {
                pResult->mType = FT_H264;
                pResult->mStrength = 1;
                if (strstr(lMagicResult, "MPEG") == NULL ||
                        strstr(lMagicResult, "sequence") == NULL)
                {
                    pResult->mIsHeader = 1;
                }
            }
            else if (strstr(lMagicResult, "MPEG") != NULL)
            {
                pResult->mType = FT_VIDEO;
                pResult->mStrength = 1;
                if (strstr(lMagicResult, "sequence") == NULL &&
                        strstr(lMagicResult, "LOAS") == NULL && 
#if 1
                        (strstr(lMagicResult, "ADTS") != NULL && 
                         strstr(lMagicResult, "layer II,") == NULL && 
                         strstr(lMagicResult, "AAC") == NULL &&
                         strstr(lMagicResult, "v1") == NULL &&
                         strstr(lMagicResult, "v2,") == NULL))
#else
                        strstr(lMagicResult, "ADTS") == NULL)
#endif
                {
                    pResult->mIsHeader = 1;
                }
            }
            else if (strstr(lMagicResult, "video") != NULL)
            {
                /* check for specific video headers */
                pResult->mType = FT_VIDEO;
                pResult->mStrength = 1;
                pResult->mIsHeader = 1;
            }
            else if (strstr(lMagicResult, "image") != NULL)
            {
                if (strstr(lMagicResult, "JPEG") != NULL)
                {
                    pResult->mType = FT_JPG;
                    pResult->mStrength = 1;
                    pResult->mIsHeader = 1;
                }
                else
                {
                    pResult->mType = FT_IMAGE;
                    pResult->mStrength = 1;
                    pResult->mIsHeader = 1;
                }
            }
            OS_SNPRINTF(pResult->mInfo, MAX_STR_LEN, "%s", lMagicResult);
            
            LOGGING_DEBUG("%s \n", lMagicResult);
            return pResult->mStrength;
        }
    }

    if (pResult->mType >= FT_UNKNOWN &&
            pResult->mIsHeader != 1)
    /* statistical examination */
    {
        lEntropy = calc_entropy(pFragment, pLen);

        if (lEntropy > 0.9)
        {
            pResult->mType = FT_HIGH_ENTROPY;
            pResult->mStrength = 1;

            /* comparably cheap check for JPEG file fragments */
            for (lCnt = 0; lCnt < pLen - 1; lCnt++)
            {
                if (pFragment[lCnt] == 0xFF)
                {
                    /* these usually occur in JPEG file fragments */
                    if (pFragment[lCnt + 1] == 0x00)
                    {
                        lCntJpeg++;
                    }
                    /* illegal sequence in JPEG files */
                    else if (pFragment[lCnt + 1] < 0xC0 || pFragment[lCnt + 1] > 0xFE)
                    {
                        lCntJpeg = 0;
                        LOGGING_DEBUG("FALSE - Wrong Marker\n");
                        break;
                    }
                }
            }

            if (lCntJpeg > 0)
            {
                pResult->mType = FT_JPG;
                OS_SNPRINTF(pResult->mInfo, MAX_STR_LEN, "no header");
                
                pResult->mStrength = 1;
                LOGGING_DEBUG("TRUE - Marker: %d\n",lCntJpeg);
                return pResult->mStrength;
            }

            /* perform SVM classification */
        }
        else
        {
            pResult->mType = FT_LOW_ENTROPY;
            pResult->mStrength = 1;
        }
    }

    return pResult->mStrength;
}

void callback_selective(BlockClassifier* pBlockClassifier,
    fragment_cb pCallback,
    void* pCallbackData,
    unsigned long long pCntBlock,
    unsigned pSizeRange, 
    ClassifyT pResult)
{
    unsigned lCnt;
    /* do something with the classification result */
    if (pBlockClassifier->mNumFileTypes == 0)
    {
        pCallback(pCallbackData, pCntBlock, pSizeRange, 
                pResult.mType, pResult.mStrength, pResult.mIsHeader, pResult.mInfo);
    }
    else
    {
        for (lCnt = 0; lCnt < pBlockClassifier->mNumFileTypes; ++lCnt)
        {
            if (pBlockClassifier->mFileTypes[lCnt].mType == pResult.mType)
            {
                /* relevant fragment */
                if (pResult.mIsHeader)
                {
                    LOGGING_INFO("ClassifyThread: Block(%lld), Typ(%d), Strength(%d), Header(%d), Info (%s) \n",
                            pCntBlock,
                            pResult.mType,
                            pResult.mStrength,
                            pResult.mIsHeader,
                            pResult.mInfo);
                }
                pCallback(pCallbackData, pCntBlock, pSizeRange, 
                        pResult.mType, pResult.mStrength, pResult.mIsHeader, pResult.mInfo);
                break;
            }
        }
    }
}
