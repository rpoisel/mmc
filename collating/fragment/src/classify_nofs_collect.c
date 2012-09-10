#include <stdlib.h>

#include "classify_collect.h"
#include "block_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"
#include "callback_collect.h"
#include "block_reader_nofs.h"

/* TODO pNumBlocks is not relevant for fs based classifiers */
fragment_collection_t* classify_nofs(
        unsigned long long pImageSize, 
        int pBlockSize, 
        int pNumBlocks, /* TODO only non-fs relevant */
        const char* pImage, 
        unsigned long long pOffset, 
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
    block_classify_nofs_mt(lHandle, classify_collect, 
            lBlocks /* callback data */, pImage, pOffset, pNumBlocks, 
            /* colons do not work in windows; thus one file is used only */
            PATH_MAGIC,
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

void classify_nofs_free(fragment_collection_t* pCollection)
{
    fragment_collection_free(pCollection);
}
