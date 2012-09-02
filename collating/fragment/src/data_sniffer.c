#include <stdlib.h>
#include <limits.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

#include "os_def.h"
#include "const_def.h"
#include "logging.h"
#include "fragment_classifier.h"
#include "block_collection.h"

#define NUM_OPTIONS 0
#define PROG_NAME "data_sniffer"
#define USAGE "Invocation: %s [-b <= 131072] [-t <= 2048] <path-to-image> \n" \
    "-b ... block size  \n" \
    "-t ... thread number \n" 

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo);

typedef struct
{
    OS_MUTEX_TYPE mMutex;
    block_collection_t* mStorage;
    long int mBlockSize;
} thread_data;

void return_error() 
{
    LOGGING_ERROR(USAGE, PROG_NAME);
    abort();
}

int main(int argc, char* argv[])
{
    FragmentClassifier* lHandle = NULL;
    ClassifyOptions lOptions[NUM_OPTIONS];
    thread_data lData = { OS_MUTEX_INIT_VALUE, NULL };
    long int lNumThreads = NUM_THREADS_DEFAULT;
    long int lBlockSize = 4096;
    struct stat lStat;
    off_t lImageSize;
    off_t lImageNumBlocks = 0;
    int lOption = -1;
    char lFilename[MAX_STR_LEN] = {'\0'};

    while ((lOption = getopt(argc, argv, "ht:b:")) != -1)
    {
        switch(lOption)
        {
            case 'h':
                LOGGING_ERROR(USAGE, PROG_NAME);
                return EXIT_SUCCESS;
            case 't':
                lNumThreads = strtol(optarg, NULL, 10);
                if (errno == ERANGE || lNumThreads < 1 || lNumThreads > 2048)
                {
                    LOGGING_ERROR("Illegal number of threads. Needs to be between 1 and 2048 (inclusive). \n");
                    return EXIT_FAILURE;
                }
                break;
            case 'b':
                lBlockSize = strtol(optarg, NULL, 10);
                if (errno == ERANGE || lBlockSize < 1 || lBlockSize > 131072)
                {
                    LOGGING_ERROR("Illegal block size given. Needs to be between 1 and 131072 (inclusive). \n");
                    return EXIT_FAILURE;
                }
                break;
            default:
                return_error();
        }
    }

    if (optind == argc)
    {
        LOGGING_ERROR("Missing image file. \n");
        return_error();
    }

    strncpy(lFilename, argv[optind], MAX_STR_LEN);
    if (stat(lFilename, &lStat) != 0)
    {
        LOGGING_ERROR("Cannot stat(2) given file: %s. \n", 
                lFilename);
        return EXIT_FAILURE;
    }
    lImageSize = lStat.st_size;

    /* see this for porting pthreads-code to windows */
    /* http://msdn.microsoft.com/en-us/library/windows/desktop/ms686908(v=vs.85).aspx */
    OS_MUTEX_INIT(lData.mMutex);

    lData.mBlockSize = lBlockSize;
    lImageNumBlocks = lImageSize / lBlockSize;
    if (lImageSize % lBlockSize != 0)
    {
        ++lImageNumBlocks;
    }

    lHandle = fragment_classifier_new(lOptions, NUM_OPTIONS, lBlockSize);
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    lData.mStorage = block_collection_new(lImageNumBlocks, lBlockSize);

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_print, 
            (void *)&lData, lFilename, 
            0 /* filesystem offset */, 
            lImageNumBlocks,
            PATH_MAGIC_DB,
            lNumThreads);

    OS_MUTEX_DESTROY(lData.mMutex);

    block_collection_free(lData.mStorage);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo)
{
    char* lType = NULL;
    thread_data* lData = (thread_data* )pData;

    OS_MUTEX_LOCK(lData->mMutex);

    switch (pType)
    {
        case FT_HIGH_ENTROPY:
            lType = "high";
            break;
        case FT_LOW_ENTROPY:
            lType = "low";
            break;
        case FT_JPG:
            lType = "jpeg";
            break;
        case FT_PNG:
            lType = "png";
            break;
        case FT_VIDEO:
            lType = "video";
            break;
        case FT_IMAGE:
            lType = "image";
            break;
        case FT_H264:
            lType = "h264";
            break;
        case FT_TXT:
            lType = "text";
            break;
        default:
            lType = "unknown";
    }
    if (strlen(pInfo) > 0)
    {
        LOGGING_INFO("%lld %s %s%s\n", 
                pOffset * lData->mBlockSize,
                lType, pInfo,
                pIsHeader ?  " (Header)" : "");
    }
    else
    {
        LOGGING_INFO("%lld %s %s\n", 
                pOffset * lData->mBlockSize,
                lType, 
                pIsHeader ?  " (Header)" : "");
    }

    OS_MUTEX_UNLOCK(lData->mMutex);
    return 0;
}
