#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

#include "fragment_classifier.h"

#define NUM_OPTIONS 0

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader);

int main(int argc, char* argv[])
{
    FragmentClassifier* lHandle = NULL;
    ClassifyOptions lOptions[NUM_OPTIONS];
    pthread_mutex_t lMutex = PTHREAD_MUTEX_INITIALIZER;
    int lNumThreads = NUM_THREADS_DEFAULT;

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

    lHandle = fragment_classifier_new(lOptions, NUM_OPTIONS, atoi(argv[2]));
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    pthread_mutex_init(&lMutex, NULL);

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_print, (void *)&lMutex, argv[1], lNumThreads);

    pthread_mutex_destroy(&lMutex);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader)
{
    pthread_mutex_t* lMutex = (pthread_mutex_t* )pData;
    pthread_mutex_lock(lMutex);
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
    pthread_mutex_unlock(lMutex);
    return 0;
}
