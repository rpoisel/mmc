#include "classify_tsk_collect.h"

#include <stdlib.h>

#include "block_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"
#include "callback_collect.h"

/* TODO check if it makes more sense to pass the actual function to call 
 * as parameter (e. g. as c-string) instead of having complete independent 
 * functions 
 */
fragment_collection_t* classify_tsk(int pBlockSize, 
        int pNumBlocks, /* ignored */
        const char* pImage, 
        unsigned long long pOffset,  /* ignored */
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize,
        int pNumThreads)
{
    BlockClassifier* lHandle = NULL;
    block_collection_t* lBlocks = NULL;
    fragment_collection_t* lFragments = NULL;

    lHandle = block_classifier_new_ct(NULL, 0, pBlockSize, pTypes, pNumTypes);
    if (!lHandle)
    {
        return NULL;
    }

    lBlocks = block_collection_new(pNumBlocks, pBlockSize); 

    /* start multithreaded classification process */
    block_classify_tsk_mt(lHandle, classify_collect, 
            lBlocks /* callback data */,
            pImage,
            pOffset,
            pNumBlocks, 
            PATH_MAGIC, /* colons do not work in windows; thus one file is used only */
            pNumThreads);

    /* factor 1/4 is just an empirical value */
    /* TODO perform this step on several CPU cores */
    lFragments = fragment_collection_new(lBlocks, 4, pOffset, 
            pBlockGap, pMinFragSize);

    /* destruct fragment classifier */
    block_collection_free(lBlocks);
    block_classifier_free(lHandle);

    return lFragments;
}

void classify_tsk_free(fragment_collection_t* pCollection)
{
    fragment_collection_free(pCollection);
}

