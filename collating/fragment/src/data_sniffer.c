#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fragment_classifier.h"

#define NUM_OPTIONS 0

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader);

int main(int argc, char* argv[])
{
    FragmentClassifier* lHandle = NULL;
    ClassifyOptions lOptions[NUM_OPTIONS];

    if (argc != 3)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size>\n", argv[0]);
        return EXIT_FAILURE;
    }

    lHandle = fragment_classifier_new(lOptions, NUM_OPTIONS, atoi(argv[2]));
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_print, NULL, argv[1]);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_print(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader)
{
    printf("Offset: %lld, Type: ", pOffset);
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
        case FT_H264:
            printf("H264");
            break;
        default:
            printf("Unknown");
    }
    printf(", Strength: %d\n", pStrength);
    return 0;
}
