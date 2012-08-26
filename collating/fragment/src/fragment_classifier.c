#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#ifdef __linux__
#include <pthread.h>
#elif defined _WIN32 || defined _WIN64
#include <Windows.h>
#else
#error "unknown platform"
#endif

/* for the windows port see the following URL: */
/* http://msdn.microsoft.com/en-us/library/windows/desktop/ms682516(v=vs.85).aspx */
/* http://msdn.microsoft.com/en-us/library/kdzttdcb(v=vs.71).aspx */
#include "magic.h"

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
    const char* mPathMagic;
} thread_data;

#ifdef __linux__
void* classify_thread(void* pData);
#else
DWORD classify_thread(LPVOID pData);
#endif

FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize)
{
    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

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
#ifdef __linux__
              snprintf(pResult->mInfo, MAX_STR_LEN, "%s", lMagicResult);
#else
              _snprintf(pResult->mInfo, MAX_STR_LEN, "%s", lMagicResult);
#endif
            
            
#if DEBUG == 1
            printf("%s | ", lMagicResult);
#endif
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
#if DEBUG == 1
                        printf("FALSE - Wrong Marker\n");
#endif
                        break;
                    }
                }
            }

            if (lCntJpeg > 0)
            {
                pResult->mType = FT_JPG;
#ifdef __linux__
                snprintf(pResult->mInfo, MAX_STR_LEN, "no header");
#else
                _snprintf(pResult->mInfo, MAX_STR_LEN, "no header");
#endif
                
                pResult->mStrength = 1;
#if DEBUG == 1
                printf("TRUE - Marker: %d\n",lCntJpeg);
#endif
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
#ifdef __linux__
      pthread_t* lThreads = NULL;
#else
      HANDLE* lThreads = NULL;
#endif
            
    int lCnt = 0;
    thread_data* lData = NULL;
    unsigned long long lSize = pSizeReal * pFragmentClassifier->mFragmentSize - pOffset;
    unsigned long long lFragsTotal = lSize / pFragmentClassifier->mFragmentSize;
    unsigned long long lFragsPerCpu = lFragsTotal / pNumThreads;
    unsigned long long lFragsPerCpuR = 0;
    unsigned long long lOffsetImg = 0;
    if (lFragsPerCpu > 0)
    {
        lFragsPerCpuR = lFragsTotal % lFragsPerCpu;
    }
       
    /* TODO check return value */
#ifdef __linux__
    lThreads = (pthread_t* )malloc(sizeof(pthread_t) * pNumThreads);
#else
    lThreads = (HANDLE* )malloc(sizeof(HANDLE) * pNumThreads);
#endif

    
    lData = (thread_data* )malloc(sizeof(thread_data) * pNumThreads);

#if DEBUG == 1
    printf("Fragments range: %lld\n", lFragsTotal);
    printf("Filesystem offset: %lld\n", pOffset);
#endif

    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        strncpy((lData + lCnt)->path_image, pImage, MAX_STR_LEN);
        (lData + lCnt)->handle_fc = pFragmentClassifier;
        (lData + lCnt)->callback = pCallback;
        (lData + lCnt)->callback_data = pCallbackData; 
        (lData + lCnt)->mPathMagic = pPathMagic;

        (lData + lCnt)->num_frags = lFragsPerCpu + (lFragsPerCpuR > 0 ? 1 : 0);
        (lData + lCnt)->offset_img = lOffsetImg;
        (lData + lCnt)->offset_fs = pOffset;
        lOffsetImg += (lData + lCnt)->num_frags;
        lFragsPerCpuR--;

#if DEBUG == 1
        printf("Starting thread %d with block range %lld to %lld.\n",
                lCnt, (lData + lCnt)->offset_img, (lData + lCnt)->offset_img + (lData + lCnt)->num_frags);
#endif
        
       
#ifdef __linux__
        pthread_create((lThreads + lCnt), NULL, 
                classify_thread, (void*)(lData + lCnt));
#elif defined _WIN32 || defined _WIN64
          *(lThreads + lCnt) = CreateThread(NULL,0,classify_thread,(void*)(lData + lCnt),0,NULL);
#else
#error "unknown platform"
#endif           
                
    }

    /* join threads */
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
#ifdef __linux__
          pthread_join(*(lThreads + lCnt), NULL);
#elif defined _WIN32 || defined _WIN64
          WaitForSingleObject(*(lThreads + lCnt),INFINITE);
#else
#error "unknown platform"
#endif
    }

    free(lData);
    free(lThreads);
    
    return EXIT_SUCCESS;
}

#ifdef __linux__
void* classify_thread(void* pData)
#elif defined _WIN32 || defined _WIN64
DWORD WINAPI classify_thread(LPVOID pData)
#endif
{
    thread_data* lData = (thread_data*)pData; 
    int lLen = lData->handle_fc->mFragmentSize;
    unsigned long long lCntBlock = lData->offset_img;
#ifdef __linux__
    FILE* lImage = NULL;
#elif defined _WIN32 || defined _WIN64
    HANDLE lImage = NULL;
#endif
    unsigned char* lBuf = NULL;
    ClassifyT lResult = { 0, 0, 0 };
    int lCnt = 0;
    magic_t lMagic;

    lMagic = magic_open(MAGIC_NONE);
    if (!lMagic)
    {
        printf("Could not load library\n");
    }
    
    /* TODO load proper file */
    if (magic_load(lMagic, lData->mPathMagic))
    {
        printf("%s\n", magic_error(lMagic));
    }


#if DEBUG == 1
    printf("Offset: %lld\n", lData->offset_img * lData->handle_fc->mFragmentSize + lData->offset_fs);
#endif

    lBuf = (unsigned char*)malloc(lData->handle_fc->mFragmentSize);
#ifdef __linux__
    lImage = fopen(lData->path_image, "r");
#elif defined _WIN32 || defined _WIN64
    lImage = CreateFile(lData->path_image, 
        GENERIC_READ, 
        FILE_SHARE_READ, 
        NULL, 
        OPEN_EXISTING, 
        0, 
        NULL);
#endif

#ifdef __linux__
    if (lImage == NULL)
#elif defined _WIN32 || defined _WIN64
    if (lImage == INVALID_HANDLE_VALUE)
#endif
    {
        /* TODO return error back to GUI */
        perror("Could not open image file");
#ifdef __linux__
        return NULL;
#else
        return 0;
#endif
    }
#ifdef __linux__
    fseek(lImage, 
            lData->offset_img * lData->handle_fc->mFragmentSize + lData->offset_fs, 
            SEEK_SET);
#elif defined _WIN32 || defined _WIN64
    SetFilePointer(lImage, 
        lData->offset_img * lData->handle_fc->mFragmentSize + lData->offset_fs, 
        0, /* TODO: danger for 64-bit systems */
        FILE_BEGIN);
#endif
            
    /* classify fragments */
    while (lLen == lData->handle_fc->mFragmentSize && 
            (lCntBlock - lData->offset_img) < lData->num_frags)
    {
#ifdef __linux__
        lLen = fread(lBuf, 1, lData->handle_fc->mFragmentSize, lImage);
#elif defined _WIN32 || defined _WIN64
        ReadFile(lImage, lBuf, lData->handle_fc->mFragmentSize, &lLen, NULL);
#endif
        
        fragment_classifier_classify_result(lData->handle_fc, lMagic, lBuf, lLen,
                &lResult);

        /* do something with the classification result */
        if (lData->handle_fc->mNumFileTypes == 0)
        {
            lData->callback(lData->callback_data, lCntBlock, 
                    lResult.mType, lResult.mStrength, lResult.mIsHeader, lResult.mInfo);
        }
        else
        {
            for (lCnt = 0; lCnt < lData->handle_fc->mNumFileTypes; ++lCnt)
            {
                if (lData->handle_fc->mFileTypes[lCnt].mType == lResult.mType)
                {
                	/* relevant fragment */
#if DEBUG == 0
                    if (lResult.mIsHeader)
                    {
                        printf("ClassifyThread: Block(%lld), Typ(%d), Strength(%d), Header(%d), Info (%s) \n",
                                lCntBlock,
                                lResult.mType,
                                lResult.mStrength,
                                lResult.mIsHeader,
                                lResult.mInfo);
                    }
#endif
                    lData->callback(lData->callback_data, lCntBlock, 
                            lResult.mType, lResult.mStrength, lResult.mIsHeader, lResult.mInfo);
                    break;
                }
            }
        }
        lCntBlock++;
    }
    
 #if defined __linux__
    fclose(lImage);
#elif defined _WIN32 || defined _WIN64
    CloseHandle(lImage);
#endif
    free(lBuf);

    magic_close(lMagic);  
    
#ifdef __linux__
    return NULL;
#else
    return 0;
#endif
    
}
