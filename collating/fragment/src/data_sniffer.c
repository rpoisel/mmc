#include <stdlib.h>
#include <limits.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <stdio.h>

#include "os_def.h"
#include "const_def.h"
#include "logging.h"
#include "fragment_classifier.h"
#include "block_collection.h"

#define PROG_NAME "data_sniffer"
#define USAGE "Invocation: %s <block-size> <number-of-threads> <path-to-image> \n"

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
    exit(1);
}

int main(int argc, char* argv[])
{
    FragmentClassifier* lHandle = NULL;
    ClassifyOptions lOptions[1];
    thread_data lData = { OS_MUTEX_INIT_VALUE, NULL, -1 };
    long int lNumThreads = NUM_THREADS_DEFAULT;
    long int lBlockSize = 4096;
    struct stat lStat;
    off_t lImageSize;
    off_t lImageNumBlocks = 0;
    char lFilename[MAX_STR_LEN] = {'\0'};

	if (argc != 4)
	{
		return_error();
	}

	lBlockSize = strtol(argv[1], NULL, 10);
	lNumThreads = strtol(argv[2], NULL, 10);
	strncpy(lFilename, argv[3], MAX_STR_LEN);
    if (stat(lFilename, &lStat) != 0)
    {
        LOGGING_ERROR("Cannot stat(2) given file: %s. \n", 
                lFilename);
        return EXIT_FAILURE;
    }
    lImageSize = lStat.st_size;

    OS_MUTEX_INIT(lData.mMutex);

    lData.mBlockSize = lBlockSize;
    lImageNumBlocks = lImageSize / lBlockSize;
    if (lImageSize % lBlockSize != 0)
    {
        ++lImageNumBlocks;
    }

    lHandle = fragment_classifier_new(lOptions, 0, lBlockSize);
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
