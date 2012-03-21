#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/stat.h>

#include "fragment_classifier.h"
#include "block_collection.h"

#define NUM_OPTIONS 0

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader);

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
    int lNumThreads = NUM_THREADS_DEFAULT;
    struct stat lStat;
    off_t lImageSize;

    if (argc != 3 && argc != 4)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size> [num-threads]\n", argv[0]);
        return EXIT_FAILURE;
    }

    if (argc == 4)
    {
        lNumThreads = atoi(argv[3]);
    }

    pthread_mutex_init(&lData.mMutex, NULL);
    stat(argv[1], &lStat);
    lImageSize = lStat.st_size;

    lHandle = fragment_classifier_new(lOptions, NUM_OPTIONS, atoi(argv[2]));
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    lData.mStorage = block_collection_new(lImageSize / atoi(argv[2]), atoi(argv[2]));

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_print, 
            (void *)&lData, argv[1], 
            lImageSize / atoi(argv[2]),
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
        FileType pType, int pStrength, int pIsHeader)
{
    thread_data* lData = (thread_data* )pData;
    pthread_mutex_lock(&lData->mMutex);
    block_collection_set(lData->mStorage, pOffset, pIsHeader);
    /*
    pIsHeader ? printf("Header, ") : printf("        ");
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
        default:
            printf("Unknown");
    }
    printf("\n");
    */
    pthread_mutex_unlock(&lData->mMutex);
    return 0;
}
