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
    const char* mPathImage;
    unsigned long long offset_img;
    unsigned long long offset_fs;
    unsigned long long num_frags;
    const char* mPathMagic;
    pipe_t* mPipeClassify;
    pipe_t* mPipeClassifyFree;
    unsigned mNumThreads;
} thread_data;

typedef struct
{
    const char* mPathImage;
    unsigned mCntCirculating;
    unsigned mSectorSize;
    pipe_producer_t* mPipeClassifyProducer;
    pipe_consumer_t* mPipeClassifyFreeConsumer;
} tsk_cb_data;

/* data structure for data passed between threads through FIFOs */
typedef struct
{
    char* mBuf;
    unsigned mLen;
    unsigned long long mOffset;
} classify_data;

/* function definitions */
THREAD_FUNC(tsk_read_thread, pData);
THREAD_FUNC(tsk_classify_thread, pData);

static void blocks_read_tsk(
        tsk_cb_data* pTskCbData
        );

static TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pTskCbData);

static TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void* pTskCbData);

static void data_act(
        char* pBuf,
        const unsigned pLen,
        const unsigned long long pOffset,
        void* pTskCbData
        );

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
        (lDataClassify + lCnt)->callback = pCallback;
        (lDataClassify + lCnt)->callback_data = pCallbackData;

        OS_THREAD_CREATE((lThreadsClassify + lCnt), (lDataClassify + lCnt), tsk_classify_thread);
    }

    /* initialize reader data */
    lDataRead->mPathImage = pImage;
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
    classify_data* lDataCurrent = NULL;
    unsigned lCnt = 0;
    size_t lReturnPop = -1;
    tsk_cb_data lTskCbData;

    /* KillPill is a NULL pointer */
    classify_data* lKillPill = NULL;
    LOGGING_INFO("Reading thread started. \n");

    lPipeClassifyProducer = pipe_producer_new(lData->mPipeClassify);
    lPipeClassifyFreeConsumer = pipe_consumer_new(lData->mPipeClassifyFree);

    /* call iterating functions */
    lTskCbData.mPathImage = lData->mPathImage;
    lTskCbData.mCntCirculating = 0;
    lTskCbData.mPipeClassifyProducer = lPipeClassifyProducer;
    lTskCbData.mPipeClassifyFreeConsumer = lPipeClassifyFreeConsumer;

    LOGGING_DEBUG("Path image: %s\n", lData->mPathImage)

    blocks_read_tsk(&lTskCbData);

    /* read from FIFO to free memory until all read elements have been classified */
    /* reduce lCntCirculating to determine the end */
    /* TODO consider problem with pipe (return value of pop) in data_act() */
    for(; lTskCbData.mCntCirculating > 0; --lTskCbData.mCntCirculating)
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

        /* classify data of block */
        block_classifier_classify_result(
                lData->handle_fc, lMagic,
                lClassifyData->mBuf, lClassifyData->mLen,
                &lResult);

        /* call this for each block read */
        callback_selective(lData->handle_fc,
                lData->callback,
                lData->callback_data,
                lClassifyData->mOffset, /* lCntBlock */ /* offset in blocks */
                lData->handle_fc->mBlockSize,
                lResult);

        pipe_push(lPipeClassifyFreeProducer, &lClassifyData, 1);
    }

    pipe_producer_free(lPipeClassifyFreeProducer);
    pipe_consumer_free(lPipeClassifyConsumer);

    LOGGING_INFO("Exiting classification thread. \n");

    return OS_THREAD_RETURN;
}

void blocks_read_tsk(
        tsk_cb_data* pTskCbData
        )
{
    TSK_VS_INFO* lVsInfo = NULL;
    TSK_IMG_INFO* lImgInfo = OS_FH_INVALID;
    TSK_OFF_T lCnt = 0;
    const char* lPathImageChar[1] = { pTskCbData->mPathImage };
    const TSK_TCHAR *const *lPathImage;
    /* TODO replace the following with buffer to be put into classification queue */
    char lBuf[MAX_BLOCK_SIZE] = { 0 };
    unsigned lCntRead = 0;

    lPathImage = (const TSK_TCHAR *const *) lPathImageChar;

    lImgInfo = tsk_img_open(
            1, /* number of images */
            lPathImage, /* path to images */
            TSK_IMG_TYPE_DETECT, /* disk image type */
            0); /* size of device sector in bytes */
    if (lImgInfo != NULL)
    {
        TSK_OFF_T lSizeSectors = lImgInfo->size / lImgInfo->sector_size + \
                                 (lImgInfo->size % lImgInfo->sector_size ? 1 : 0);
        LOGGING_INFO("Image size (Bytes): %lu, Image size (sectors): %lu\n",
                lImgInfo->size,
                lSizeSectors);

        pTskCbData->mSectorSize = lImgInfo->sector_size;

        lVsInfo = tsk_vs_open(lImgInfo, 0, TSK_VS_TYPE_DETECT);
        if (lVsInfo != NULL)
        {
            if (tsk_vs_part_walk(lVsInfo,
                    0, /* start */
                    lVsInfo->part_count - 1, /* end */
                    TSK_VS_PART_FLAG_ALL, /* all partitions */
                    part_act, /* callback */
                    (void*) pTskCbData /* data passed to the callback */
                    ) != 0)
            {
                fprintf(stderr, "Problem when walking partitions. \n");
            }
        }
        else
        {
            LOGGING_DEBUG("Volume system cannot be opened.\n");
            for (lCnt = 0; lCnt < lSizeSectors; lCnt++)
            {
                lCntRead = lCnt == lSizeSectors - 1 ? 
                                lImgInfo->size % lImgInfo->sector_size :
                                lImgInfo->sector_size;

				LOGGING_DEBUG("Reading %u bytes\n", lCntRead);

				tsk_img_read(
                        lImgInfo, /* handler */
                        lCnt * lImgInfo->sector_size, /* start address */
                        lBuf, /* buffer to store data in */
                        lCntRead /* amount of data to read */
                        );
                data_act(lBuf, lCntRead, lCnt * lImgInfo->sector_size, pTskCbData);
            }
        }
    }
    else
    {
        LOGGING_ERROR("Problem opening the image. \n");
		tsk_error_print(stderr);
		exit(1);
    }
}

TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pTskCbData)
{
    TSK_FS_INFO* lFsInfo = NULL;
    tsk_cb_data* lTskCbData = (tsk_cb_data* )pTskCbData;
    unsigned long long lCnt = 0;
    char lBuf[32768] = { 0 };
    unsigned long long lOffsetBlock = 0;

    /* open file system */
    if ((lFsInfo = tsk_fs_open_vol(
            pPartInfo, /* partition to open */
            TSK_FS_TYPE_DETECT /* auto-detect mode on */
            )) != NULL)
    {
        /* known file-system */

        /* iterate over unallocated blocks of fs */
        tsk_fs_block_walk(
                lFsInfo, /* file-system info */
                0, /* start */
                lFsInfo->block_count - 1, /* end */
                TSK_FS_BLOCK_WALK_FLAG_UNALLOC, /* only unallocated blocks */
                block_act, /* callback */
                pTskCbData /* file-handle */
                );
        /* close fs */
        tsk_fs_close(lFsInfo);
    }
    else
    {
        /* unknown file-system */

        /* iterate through all blocks of this volume regardless of their state */
        for (lCnt = 0; lCnt < pPartInfo->len; lCnt++)
        {
            lOffsetBlock = (pPartInfo->start + lCnt) * pPartInfo->vs->block_size;

            LOGGING_DEBUG(
                    "Block in unknown partition (Len: %lu blocks). " 
                    "Size: %u, Absolute address (Bytes): %lld\n",
                    pPartInfo->len,
                    pPartInfo->vs->block_size,
                    lOffsetBlock);

            /* use the following function so that forensic images are supported */
            /* HINT: this is not the case with fopen/fseek/fread/fclose functions */
            tsk_vs_part_read_block(
                    pPartInfo,
                    lCnt, /* start address (blocks) relative to start of volume */
                    lBuf, /* buffer to store data in */
                    pPartInfo->vs->block_size /* amount of data to read */
                    );
            data_act(lBuf,
                    pPartInfo->vs->block_size, 
                    lOffsetBlock,
                    lTskCbData);
        }
    }

    return TSK_WALK_CONT;
}

TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void* pTskCbData)
{
    tsk_cb_data* lTskCbData = (tsk_cb_data* )pTskCbData;

    LOGGING_DEBUG(
            "FS-Offset (Bytes): %lu, Size: %u, "
            "Block: %lu, Absolute address: %ld\n",
            a_block->fs_info->offset,
            a_block->fs_info->block_size,
            a_block->addr, 
            a_block->fs_info->offset + a_block->addr * a_block->fs_info->block_size);

    data_act(
            a_block->buf, /* block data */
            a_block->fs_info->block_size, /* size in bytes */
            a_block->fs_info->offset + a_block->addr * a_block->fs_info->block_size,
            lTskCbData); /* file-handle */
    return TSK_WALK_CONT;
}

static void data_act(
        char* pBuf,
        const unsigned pLen,
        const unsigned long long pOffset,
        void* pTskCbData
        )
{
    tsk_cb_data* lTskCbData = (tsk_cb_data* )pTskCbData;
    classify_data* lDataCurrent = NULL;
    size_t lReturnPop = -1;

    /* more elements can be allocated */
    if (lTskCbData->mCntCirculating < SIZE_FIFO)
    {
        lDataCurrent = 
            (classify_data* )malloc(sizeof(classify_data));
        lDataCurrent->mBuf = 
            (char* )malloc(sizeof(char) * MAX_BLOCK_SIZE);
            
        ++lTskCbData->mCntCirculating;
    }
    /* wait for free FIFO to receive elements for re-use */
    else
    {
        lReturnPop = pipe_pop(lTskCbData->mPipeClassifyFreeConsumer,
                &lDataCurrent, 1);
        if (lReturnPop == 0)
        {
            /* problem with FIFO */
            return;
        }
    }
    
    /* copy data to buffer */
    memcpy(lDataCurrent->mBuf, pBuf, pLen);
    lDataCurrent->mLen = pLen;
    lDataCurrent->mOffset = pOffset / lTskCbData->mSectorSize;

    /* enqueue lDataCurrent */
    pipe_push(lTskCbData->mPipeClassifyProducer,
            &lDataCurrent, 1);
}
