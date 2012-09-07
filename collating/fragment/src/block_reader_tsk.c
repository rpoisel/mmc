#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <tsk3/libtsk.h>

#ifndef _MSC_VER
#include <magic.h>
#else
/* for the windows port see the following URL: */
/* http://msdn.microsoft.com/en-us/library/windows/desktop/ms682516(v=vs.85).aspx */
/* http://msdn.microsoft.com/en-us/library/kdzttdcb(v=vs.71).aspx */
#include "magic.h"
#endif

#include "pipe.h"

#include "os_def.h"
#include "logging.h"
#include "block_classifier.h"
#include "block_reader_tsk.h"
#include "classify_tsk_collect.h"

/* number a FIFO queue can take */
#define SIZE_FIFO 2048

/* maximum size of a block read from an image */
#define MAX_BLOCK_SIZE 32768

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
    pipe_t* mPipeClassify;
    pipe_t* mPipeClassifyFree;
    unsigned mNumThreads;
} thread_data;

/* data structure for data passed between threads through FIFOs */
typedef struct
{
    unsigned char* mBuf;
    unsigned mLen;
} classify_data;

THREAD_FUNC(tsk_read_thread, pData);
THREAD_FUNC(tsk_classify_thread, pData);

int block_classify_tsk_mt(
        BlockClassifier* pBlockClassifier,
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, /* ignored */
        unsigned long long pSizeReal, /* ignored */
        const char* pPathMagic, 
        unsigned pNumThreads
        )
{
    unsigned lCnt = 0;
    OS_THREAD_TYPE* lThreadRead = NULL;
    OS_THREAD_TYPE* lThreadsClassify = NULL;
    thread_data* lDataClassify = NULL;
    thread_data* lDataRead = NULL;
    pipe_t* lPipeClassify = NULL; 
    pipe_t* lPipeClassifyFree = NULL; 

    lThreadRead = (OS_THREAD_TYPE* )malloc(sizeof(OS_THREAD_TYPE));
    lDataRead = (thread_data* )malloc(sizeof(thread_data));
    lThreadsClassify = (OS_THREAD_TYPE* )malloc(sizeof(OS_THREAD_TYPE) * pNumThreads);
    lDataClassify = (thread_data* )malloc(sizeof(thread_data) * pNumThreads);

    if (lThreadRead == NULL || lThreadsClassify == NULL ||
            lDataClassify == NULL)
    {
        /* TODO react on error */
    }

    /* create one FIFO pipe for passing the read data to classifiers */
    lPipeClassify = pipe_new(sizeof(classify_data* ), SIZE_FIFO);

    /* create one FIFO pipe for passing back empty buffers to the reader */
    /* pipe size is unlimited on purpose */
    lPipeClassifyFree = pipe_new(sizeof(classify_data* ), 0);

    /* create classification threads */
    for (lCnt = 0; lCnt < pNumThreads; lCnt++)
    {
        /* initialize thread data */
        (lDataClassify + lCnt)->handle_fc = pBlockClassifier;
        (lDataClassify + lCnt)->mPathMagic = pPathMagic;
        (lDataClassify + lCnt)->mPipeClassify = lPipeClassify;
        (lDataClassify + lCnt)->mPipeClassifyFree = lPipeClassifyFree;

        OS_THREAD_CREATE((lThreadsClassify + lCnt), (lDataClassify + lCnt), tsk_classify_thread);
    }

    /* initialize reader data */
    lDataRead->mPipeClassify = lPipeClassify;
    lDataRead->mPipeClassifyFree = lPipeClassifyFree;
    lDataRead->mNumThreads = pNumThreads;

    /* create reader thread */
    OS_THREAD_CREATE(lThreadRead, lDataRead, tsk_read_thread);

    /* join classification threads */
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        OS_THREAD_JOIN(*(lThreadsClassify + lCnt));
    }
    LOGGING_INFO("Classification threads joined.\n");

    /* join reader thread */
    OS_THREAD_JOIN(*lThreadRead);
    LOGGING_INFO("Reading thread joined.\n")

    pipe_free(lPipeClassify);
    pipe_free(lPipeClassifyFree);

    free(lDataClassify);
    free(lThreadsClassify);
    free(lDataRead);
    free(lThreadRead);
            
    return EXIT_SUCCESS;
}

THREAD_FUNC(tsk_read_thread, pData)
{
    thread_data* lData = (thread_data* )pData;
    pipe_producer_t* lPipeClassifyProducer = NULL;
    pipe_consumer_t* lPipeClassifyFreeConsumer = NULL;
    unsigned lCnt = 0;
    unsigned lCntCirculating = 0;
    classify_data* lDataCurrent = NULL;
    size_t lReturnPop = -1;

    /* KillPill is a NULL pointer */
    classify_data* lKillPill = NULL;
    LOGGING_INFO("Reading thread started. \n");

    lPipeClassifyProducer = pipe_producer_new(lData->mPipeClassify);
    lPipeClassifyFreeConsumer = pipe_consumer_new(lData->mPipeClassifyFree);

    /* read blocks from image */
    for (lCnt = 0; lCnt < 10 /*placeholder */; lCnt++)
    {
        /* more elements can be allocated */
        if (lCntCirculating < SIZE_FIFO)
        {
            lDataCurrent = 
                (classify_data* )malloc(sizeof(classify_data));
            lDataCurrent->mBuf = 
                (unsigned char* )malloc(sizeof(unsigned char) * MAX_BLOCK_SIZE);
                
            ++lCntCirculating;
        }
        /* wait for free FIFO to receive elements for re-use */
        else
        {
            lReturnPop = pipe_pop(lPipeClassifyFreeConsumer, &lDataCurrent, 1);
            if (lReturnPop == 0)
            {
                /* problem with FIFO */
                break;
            }
        }

        /* read data into buffer */
        lDataCurrent->mLen = 0; /* placeholder */

        /* enqueue lDataCurrent */
        pipe_push(lPipeClassifyProducer, &lDataCurrent, 1);
    }

    /* read from FIFO to free memory until all read elements have been classified */
    /* reduce lCntCirculating to determine the end */
    for(; lCntCirculating > 0; --lCntCirculating)
    {
        lReturnPop = pipe_pop(lPipeClassifyFreeConsumer, &lDataCurrent, 1);
        if (lReturnPop == 0)
        {
            /* problem with FIFO */
            break;
        }
        free(lDataCurrent->mBuf);
        free(lDataCurrent);
    }

    for (lCnt = 0; lCnt < lData->mNumThreads; ++lCnt)
    {
        pipe_push(lPipeClassifyProducer, &lKillPill, 1);
    }

    /* free allocated memory */

    /* free other resources */
    pipe_producer_free(lPipeClassifyProducer);
    pipe_consumer_free(lPipeClassifyFreeConsumer);

    LOGGING_INFO("Exiting reading thread. \n");

    return OS_THREAD_RETURN;
}

THREAD_FUNC(tsk_classify_thread, pData)
{
    thread_data* lData = (thread_data* )pData;
    ClassifyT lResult = { FT_UNKNOWN, 0, 0, { '\0' } };
    magic_t lMagic;
    pipe_consumer_t* lPipeClassifyConsumer = NULL;
    pipe_producer_t* lPipeClassifyFreeProducer = NULL;
    classify_data* lClassifyData = NULL;
    size_t lReturnPop = -1;

    LOGGING_INFO("Classification thread started. \n");

    lPipeClassifyConsumer = pipe_consumer_new(lData->mPipeClassify);
    lPipeClassifyFreeProducer = pipe_producer_new(lData->mPipeClassifyFree);

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

    for(;;) 
    {
        /* read from FIFO */
        lReturnPop = pipe_pop(lPipeClassifyConsumer, &lClassifyData, 1);

        /* check for kill-pill => break out of loop and shutdown thread */
        if (lClassifyData == NULL || lReturnPop == 0)
        {
            break;
        }

#if 0
        /* classify data of block */
        block_classifier_classify_result(
                lData->handle_fc, lMagic,
                lClassifyData->mBuf, lClassifyData->mLen,
                &lResult);

        /* call this for each block read */
        callback_selective(lData->handle_fc,
                lData->callback,
                lData->callback_data,
                0 /* lCntBlock */ /* offset in blocks */,
                lData->handle_fc->mBlockSize,
                lResult);
#endif

        pipe_push(lPipeClassifyFreeProducer, &lClassifyData, 1);
    }

    pipe_producer_free(lPipeClassifyFreeProducer);
    pipe_consumer_free(lPipeClassifyConsumer);

    LOGGING_INFO("Exiting classification thread. \n");

    return OS_THREAD_RETURN;
}
