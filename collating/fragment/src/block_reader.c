#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "block_reader.h"

int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader);

int classify(block_collection_t* pBlocks, 
        int pBlockSize, 
        int pNumBlocks, 
        const char* pImage, 
        ClassifyT* pTypes, 
        int pNumTypes)
{
    FragmentClassifier* lHandle = NULL;

    lHandle = fragment_classifier_new_ct(NULL, 0, pBlockSize, pTypes, pNumTypes);
    if (!lHandle)
    {
        return EXIT_FAILURE;
    }

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_collect, pBlocks, pImage);

    /* destruct fragment classifier */
    fragment_classifier_free(lHandle);

    return EXIT_SUCCESS;
}

int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader)
{
    block_collection_t* pBlocks = (block_collection_t* )pData;
    /* store classified block */
    return block_collection_add(pBlocks, pOffset, pIsHeader);
}
