#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef _MSC_VER
#include <magic.h>
#else
/* for the windows port see the following URL: */
/* http://msdn.microsoft.com/en-us/library/windows/desktop/ms682516(v=vs.85).aspx */
/* http://msdn.microsoft.com/en-us/library/kdzttdcb(v=vs.71).aspx */
#include "magic.h"
#endif

#include "os_def.h"
#include "logging.h"
#include "block_classifier.h"
#include "block_reader_nofs.h"
#include "classify_nofs_collect.h"

typedef struct 
{
    BlockClassifier* handle_fc;
    fragment_cb callback;
    void* callback_data;
    int result;
    char path_image[MAX_STR_LEN];
    unsigned long long offset_img;
    unsigned long long offset_fs;
    unsigned long long num_frags;
    const char* mPathMagic;
} thread_data;

THREAD_FUNC(classify_thread, pData);

int block_classify_nofs_mt(BlockClassifier* pBlockClassifier,
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, 
        unsigned long long pSizeReal,
        const char* pPathMagic, 
        unsigned int pNumThreads
        )
{
    OS_THREAD_TYPE* lThreads = NULL;
            
    unsigned lCnt = 0;
    thread_data* lData = NULL;
    unsigned long long lSize = pSizeReal * pBlockClassifier->mBlockSize - pOffset;
    unsigned long long lFragsTotal = lSize / pBlockClassifier->mBlockSize;
    unsigned long long lFragsPerCpu = lFragsTotal / pNumThreads;
    unsigned long long lFragsPerCpuR = 0;
    unsigned long long lOffsetImg = 0;
    if (lFragsPerCpu > 0)
    {
        lFragsPerCpuR = lFragsTotal % lFragsPerCpu;
    }
       
    /* TODO check return values */
    lThreads = (OS_THREAD_TYPE* )malloc(sizeof(OS_THREAD_TYPE) * pNumThreads);
    lData = (thread_data* )malloc(sizeof(thread_data) * pNumThreads);

    LOGGING_DEBUG("Fragments range: %lld\n", lFragsTotal);
    LOGGING_DEBUG("Filesystem offset: %lld\n", pOffset);

    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        strncpy((lData + lCnt)->path_image, pImage, MAX_STR_LEN);
        (lData + lCnt)->handle_fc = pBlockClassifier;
        (lData + lCnt)->callback = pCallback;
        (lData + lCnt)->callback_data = pCallbackData; 
        (lData + lCnt)->mPathMagic = pPathMagic;

        (lData + lCnt)->num_frags = lFragsPerCpu + (lFragsPerCpuR > 0 ? 1 : 0);
        (lData + lCnt)->offset_img = lOffsetImg;
        (lData + lCnt)->offset_fs = pOffset;
        lOffsetImg += (lData + lCnt)->num_frags;
        lFragsPerCpuR--;

        LOGGING_DEBUG("Starting thread %d with block range %lld to %lld.\n",
                lCnt, (lData + lCnt)->offset_img, (lData + lCnt)->offset_img + (lData + lCnt)->num_frags);
        
    OS_THREAD_CREATE((lThreads + lCnt), (lData + lCnt), classify_thread);
    }

    /* join threads */
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        OS_THREAD_JOIN(*(lThreads + lCnt));
    }

    free(lData);
    free(lThreads);
    
    return EXIT_SUCCESS;
}

THREAD_FUNC(classify_thread, pData)
{
    thread_data* lData = (thread_data*)pData; 
    unsigned lLen = lData->handle_fc->mBlockSize;
    unsigned long long lCntBlock = lData->offset_img;
    OS_FH_TYPE lImage = NULL;
    unsigned char* lBuf = NULL;
    ClassifyT lResult = { FT_UNKNOWN, 0, 0, { '\0' } };
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


    LOGGING_DEBUG(
            "Offset: %lld\n", lData->offset_img * lData->handle_fc->mBlockSize + lData->offset_fs);

    lBuf = (unsigned char*)malloc(lData->handle_fc->mBlockSize);
    lImage = OS_FOPEN_READ(lData->path_image);

    if (lImage == OS_FH_INVALID)
    {
        /* TODO return error back to GUI */
        perror("Could not open image file");
        return OS_THREAD_RETURN;
    }
    OS_FSEEK_SET(lImage,
        lData->offset_img * lData->handle_fc->mBlockSize + lData->offset_fs);
            
    /* classify fragments */
    while (lLen == lData->handle_fc->mBlockSize && 
            (lCntBlock - lData->offset_img) < lData->num_frags)
    {
        OS_FREAD(lBuf, lData->handle_fc->mBlockSize, lLen, lImage); 
        block_classifier_classify_result(lData->handle_fc, lMagic, lBuf, lLen,
                &lResult);

        callback_selective(lData->handle_fc,
                lData->callback,
                lData->callback_data,
                lCntBlock,
                lData->handle_fc->mBlockSize,
                lResult);

        lCntBlock++;
    }
    
    OS_FCLOSE(lImage);
    free(lBuf);

    magic_close(lMagic);  
    
    return OS_THREAD_RETURN;
}
