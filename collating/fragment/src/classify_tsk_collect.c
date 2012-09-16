#include <stdlib.h>

#include "classify_collect.h"
#include "block_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"
#include "callback_collect.h"
#include "block_reader_tsk.h"

#define SECTOR_SIZE 512

/* TODO check if it makes more sense to pass the actual function to call 
 * as parameter (e. g. as c-string) instead of having complete independent 
 * functions 
 */
fragment_collection_t* classify_tsk(
        unsigned long long pImageSize, 
        unsigned pBlockSize, 
        unsigned pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset,  /* ignored */
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize,
        const char* pPathMagic,
        int pNumThreads)
{
    BlockClassifier* lHandle = NULL;
    block_collection_t* lBlocks = NULL;
    fragment_collection_t* lFragments = NULL;

    lHandle = block_classifier_new_ct(NULL, 0, pTypes, pNumTypes);
    if (!lHandle)
    {
        return NULL;
    }

    /* initialize block_collection with default sector size */
    /* block size fixed for tsk */
    /* TODO use sector size from image here */
    lBlocks = block_collection_new(
            pImageSize / SECTOR_SIZE + (pImageSize % SECTOR_SIZE != 0 ? 1 : 0),
            SECTOR_SIZE
            ); 

    /* start multithreaded classification process */
    block_classify_tsk_mt(lHandle,
            classify_collect, 
            lBlocks /* callback data */,
            pImage,
            pOffset,
            pBlockSize,
            pNumBlocks, 
            pPathMagic, /* colons do not work in windows; thus one file is used only */
            pNumThreads);

    /* factor 1/4 is just an empirical value */
    /* TODO perform this step on several CPU cores */
    /* NOTE: pOffset should only be used in case there is a real offset 
     *       used for the invocation of TSK itself
     */
#if 0
    lFragments = fragment_collection_new(lBlocks, 4, pOffset, 
            pBlockGap, pMinFragSize);
#else
    lFragments = fragment_collection_new(lBlocks, 4, 0,
            pBlockGap, pMinFragSize);
#endif

    /* destruct fragment classifier */
    block_collection_free(lBlocks);
    block_classifier_free(lHandle);

    return lFragments;
}

void classify_tsk_free(fragment_collection_t* pCollection)
{
    fragment_collection_free(pCollection);
}

