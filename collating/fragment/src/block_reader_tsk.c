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

THREAD_FUNC(tsk_read_thread, pData);
THREAD_FUNC(tsk_classify_thread, pData);

int block_classify_tsk_mt(BlockClassifier* pBlockClassifier,
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, /* ignored */
        unsigned long long pSizeReal, /* ignored */
        const char* pPathMagic, 
        unsigned int pNumThreads
        )
{
    OS_THREAD_TYPE* lThreads = NULL;

    /* create one FIFO pipe for passing the read data to classifiers */
    /* create one FIFO pipe for passing back empty buffers to the reader */

    /* create classification threads */
    /* create reader thread */

    /* send kill-pills to classification threads */
            
    return EXIT_SUCCESS;
}

THREAD_FUNC(tsk_read_thread, pData)
{
    return OS_THREAD_RETURN;
}

THREAD_FUNC(tsk_classify_thread, pData)
{
    return OS_THREAD_RETURN;
}
