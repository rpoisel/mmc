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
#define SIZE_FIFO 100

/* maximum size of a fs-block */
#define MAX_BLOCK_SIZE 4096

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
} thread_data;

/* data structure for data passed between threads through FIFOs */
typedef struct
{
    char mBuf[MAX_BLOCK_SIZE];
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
        unsigned int pNumThreads
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
    lPipeClassify = pipe_new(sizeof(classify_data), SIZE_FIFO);

    /* create one FIFO pipe for passing back empty buffers to the reader */
    /* pipe size is unlimited on purpose */
    lPipeClassifyFree = pipe_new(sizeof(classify_data), 0);

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

    /* create reader thread */
    OS_THREAD_CREATE(lThreadRead, lDataRead, tsk_read_thread);

    /* join reader thread */
    OS_THREAD_JOIN(*lThreadRead);
    
    /* join classification threads */
    for (lCnt = 0; lCnt < pNumThreads; ++lCnt)
    {
        OS_THREAD_JOIN(*(lThreadsClassify + lCnt));
    }

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
    pipe_producer_t* pipe_classify_producer = NULL;
    pipe_consumer_t* pipe_classify_free_consumer = NULL;

    pipe_classify_producer = pipe_producer_new(lData->mPipeClassify);
    pipe_classify_free_consumer = pipe_consumer_new(lData->mPipeClassifyFree);

    /* read blocks from image */

    /* num of allocated blocks < intended memory space => allocate memory */
    /* place data into queue */

    /* after reading => send kill-pills to classification threads; push into FIFO */

    /* free allocated memory */

    /* free other resources */
    pipe_producer_free(pipe_classify_producer);
    pipe_consumer_free(pipe_classify_free_consumer);

    return OS_THREAD_RETURN;
}

THREAD_FUNC(tsk_classify_thread, pData)
{
    thread_data* lData = (thread_data* )pData;
    ClassifyT lResult = { FT_UNKNOWN, 0, 0, { '\0' } };
    magic_t lMagic;
    unsigned lLen = lData->handle_fc->mBlockSize;
    unsigned char* lBuf = NULL;
    pipe_consumer_t* pipe_classify_consumer = NULL;
    pipe_producer_t* pipe_classify_free_producer = NULL;

    pipe_classify_consumer = pipe_consumer_new(lData->mPipeClassify);
    pipe_classify_free_producer = pipe_producer_new(lData->mPipeClassifyFree);

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

        /* check for kill-pill => break out of loop and shutdown thread */
        break;

        /* classify data of block */
        block_classifier_classify_result(
                lData->handle_fc, lMagic, lBuf, lLen,
                &lResult);

        /* call this for each block read */
        callback_selective(lData->handle_fc,
                lData->callback,
                lData->callback_data,
                0 /* lCntBlock */ /* offset in blocks */,
                lData->handle_fc->mBlockSize,
                lResult);
    }

    pipe_producer_free(pipe_classify_free_producer);
    pipe_consumer_free(pipe_classify_consumer);

    return OS_THREAD_RETURN;
}
