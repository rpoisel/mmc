#include <stdlib.h>
#include <stdio.h>

#include "fragment_collection.h"

fragment_collection_t* fragment_collection_new(
        block_collection_t* pBlocks, 
        int pFactor)
{
    unsigned long long lCntFrag = 0;
    unsigned long long lCntBlock = 0;

    fragment_collection_t* lFragments = 
        (fragment_collection_t* )malloc(sizeof(fragment_collection_t));

    lFragments->mNumFrags = 0;
    lFragments->mFrags = (fragment_t* )malloc(sizeof(fragment_t) * \
            block_collection_len(pBlocks) / pFactor);

    for(lCntBlock = 0; 
            lCntFrag < block_collection_len(pBlocks) / pFactor &&
            lCntBlock < block_collection_len(pBlocks); 
            ++lCntBlock)
    {
        if (BLOCK(block_collection_get(pBlocks, lCntBlock)))
        {
            printf("Block %lld%s\n", 
                    lCntBlock, 
                    HEADER(block_collection_get(pBlocks, lCntBlock)) ? ", Header" : "");
        }
#if 0
        (lFragments->mFrags + lCntFrag)->mOffset = 0;
        (lFragments->mFrags + lCntFrag)->mSize = 512;
        (lFragments->mFrags + lCntFrag)->mNextIdx = -1;
        (lFragments->mFrags + lCntFrag)->mIsHeader = 1;
        (lFragments->mFrags + lCntFrag)->mPicBegin = "";
        (lFragments->mFrags + lCntFrag)->mPicEnd = "";
        (lFragments->mFrags + lCntFrag)->mIsSmall = 0;
#endif
    }

    return lFragments;
}

void fragment_collection_free(
        fragment_collection_t* pCollection)
{
    free(pCollection->mFrags);
    free(pCollection);
}
