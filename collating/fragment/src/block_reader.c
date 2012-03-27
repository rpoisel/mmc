#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "block_reader.h"

int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader);

fragment_collection_t* classify(int pBlockSize, 
        int pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize,
        int pNumThreads)
{
    FragmentClassifier* lHandle = NULL;
    block_collection_t* lBlocks = NULL;

    lHandle = fragment_classifier_new_ct(NULL, 0, pBlockSize, pTypes, pNumTypes);
    if (!lHandle)
    {
        return NULL;
    }

    lBlocks = block_collection_new(pNumBlocks, pBlockSize); 

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_collect, 
            lBlocks /* callback data */, pImage, pOffset, pNumBlocks, 
            "data/magic/animation.mgc:" \
                "data/magic/jpeg.mgc:" \
                "data/magic/png.mgc", 
            pNumThreads);

    /* factor 1/4 is just an empirical value */
    /* TODO perform this step on several CPU cores */
    fragment_collection_t* lFragments = fragment_collection_new(lBlocks, 4, pOffset, 
            pBlockGap, pMinFragSize);

    /* destruct fragment classifier */
    block_collection_free(lBlocks);
    fragment_classifier_free(lHandle);

    return lFragments;
}

void classify_free(fragment_collection_t* pCollection)
{
    fragment_collection_free(pCollection);
}

int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader)
{
    block_collection_t* pBlocks = (block_collection_t* )pData;
    /* store classified block */
    return block_collection_set(pBlocks, pOffset, pIsHeader);
}
