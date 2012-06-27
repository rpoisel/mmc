#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>
#include <string.h>
#include <pthread.h>
#include <sys/stat.h>

#include "fragment_classifier.h"
#include "block_collection.h"

#define NUM_OPTIONS 0

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo);

typedef struct
{
    pthread_mutex_t mMutex;
    block_collection_t* mStorage;
} thread_data;

int main(int argc, char* argv[])
{
    FragmentClassifier* lHandle = NULL;
    ClassifyOptions lOptions[NUM_OPTIONS];
    thread_data lData = { PTHREAD_MUTEX_INITIALIZER, NULL };
    long int lNumThreads = NUM_THREADS_DEFAULT;
    long int lBlockSize = -1;
    struct stat lStat;
    off_t lImageSize;
    off_t lImageBlockSize = 0;

    if (argc != 3 && argc != 4)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size <= 131072> [num-threads <= 2048]\n", argv[0]);
        return EXIT_FAILURE;
    }

    if (argc == 4)
    {
        lNumThreads = strtol(argv[3], NULL, 10);
        if (errno == ERANGE || lNumThreads < 1 || lNumThreads > 2048)
        {
            fprintf(stderr, "Illegal number of threads. Needs to be between 1 and 2048 (inclusive). \n");
            return EXIT_FAILURE;
        }
    }

    pthread_mutex_init(&lData.mMutex, NULL);
    if (stat(argv[1], &lStat) != 0)
    {
        fprintf(stderr, "File does not exist. \n");
        return EXIT_FAILURE;
    }
    lImageSize = lStat.st_size;

    lBlockSize = strtol(argv[2], NULL, 10);
    if (errno == ERANGE || lBlockSize < 1 || lBlockSize > 131072)
    {
        fprintf(stderr, "Illegal block size given. Needs to be between 1 and 131072 (inclusive). \n");
        return EXIT_FAILURE;
    }
    lImageBlockSize = lImageSize / lBlockSize;
    if (lImageSize % lBlockSize != 0)
    {
        ++lImageBlockSize;
    }

    lHandle = fragment_classifier_new(lOptions, NUM_OPTIONS, lBlockSize);
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    lData.mStorage = block_collection_new(lImageBlockSize, lBlockSize);

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_print, 
            (void *)&lData, argv[1], 
            0 /* filesystem offset */, 
            lImageBlockSize,
            "../../data/magic/animation.mgc:" \
                "../../data/magic/jpeg.mgc:" \
                "../../data/magic/png.mgc", 
            lNumThreads);

    pthread_mutex_destroy(&lData.mMutex);

    block_collection_free(lData.mStorage);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo)
{
    thread_data* lData = (thread_data* )pData;
    pthread_mutex_lock(&lData->mMutex);

    pIsHeader ?  printf("Header, ") : printf("        ");
    printf("Offset: % 10lld, Strength: %d, Type: ", 
            pOffset, pStrength);
    switch (pType)
    {
        case FT_HIGH_ENTROPY:
            printf("High Entropy");
            break;
        case FT_LOW_ENTROPY:
            printf("Low Entropy");
            break;
        case FT_JPG:
            printf("JPEG");
            break;
        case FT_PNG:
            printf("PNG");
            break;
        case FT_VIDEO:
            printf("VIDEO");
            break;
        case FT_IMAGE:
            printf("IMAGE");
            break;
        case FT_H264:
            printf("H264");
            break;
        case FT_TXT:
            printf("TEXT");
            break;
        default:
            printf("Unknown");
    }
    if (strlen(pInfo) > 0)
    {
        printf(", Info: %s", pInfo);
    }
    printf("\n");

    pthread_mutex_unlock(&lData->mMutex);
    return 0;
}
