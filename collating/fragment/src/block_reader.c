#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fragment_classifier.h"
#include "block_collection.h"

#define NUM_OPTIONS 0

int callback_collect(unsigned long long pOffset, FileType pType, int pStrength);

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
    fragment_classifier_classify_mt(lHandle, callback_collect, argv[1]);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_collect(unsigned long long pOffset, FileType pType, int pStrength)
{
    /* store classified block */
    return 0;
}
