#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fragment_classifier.h"

#define NUM_OPTIONS 0


typedef struct
{
    unsigned long long* mBlockArray;
    unsigned long long mMaxBlocks;
    unsigned long long mNumBlocks;
} block_array;

block_array* block_array_new(unsigned long long pMaxBlocks);
int block_array_add(block_array* pArray, unsigned long long pOffset, int pIsHeader);
int block_array_sort(block_array* pArray);
unsigned long long block_array_get(block_array* pArray, unsigned long long pIndex);
int block_array_free(block_array* pArray);

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
    fragment_classifier_classify_mt(lHandle, callback_print, argv[1]);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

block_array* block_array_new(unsigned long long pMaxBlocks)
{
    return NULL;
}

int callback_collect(unsigned long long pOffset, FileType pType, int pStrength)
{
    /* store classified block */
    return 0;
}
