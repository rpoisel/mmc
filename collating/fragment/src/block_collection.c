#include <stdlib.h>

#include "block_collection.h"

struct _block_collection_t
{
    unsigned long long* mBlockArray;
    unsigned long long mMaxBlocks;
    unsigned long long mNumBlocks;
    unsigned long long mNumHeaders;
};

block_collection_t* block_collection_new(unsigned long long pMaxBlocks)
{
    block_collection_t* lHandle = (block_collection_t*)malloc(sizeof(block_collection_t));

    lHandle->mBlockArray = (unsigned long long*)malloc(sizeof(unsigned long long) * pMaxBlocks);
    lHandle->mMaxBlocks = pMaxBlocks;
    lHandle->mNumBlocks = 0;
    lHandle->mNumHeaders = 0;

    return lHandle;
}

int block_collection_add(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader)
{
    if (pIsHeader)
    {
        pCollection->mBlockArray[pCollection->mNumBlocks] = HEADER(pOffset);
        pCollection->mNumHeaders++;
    }
    else
    {
        pCollection->mBlockArray[pCollection->mNumBlocks] = pOffset;
    }
    pCollection->mNumBlocks++;

    return 0;
}

static int compare_blocks(const void* pBlock1, const void* pBlock2)
{
    return OFFSET((**(unsigned long long** )pBlock1)) - \
        OFFSET((**(unsigned long long** )pBlock2));
}

void block_collection_sort(block_collection_t* pCollection)
{
    /* do an in-place sort of all elements */
    qsort((void* )pCollection, pCollection->mNumBlocks, 
            sizeof(block_collection_t), compare_blocks);
}

unsigned long long block_collection_get(block_collection_t* pCollection, 
        unsigned long long pIndex)
{
    return OFFSET(pCollection->mBlockArray[pIndex]);
}

unsigned long long block_collection_len(block_collection_t* pCollection)
{
    return pCollection->mNumBlocks;
}

void block_collection_free(block_collection_t* pCollection)
{
    free(pCollection->mBlockArray);
    free(pCollection);
}

int isHeader(unsigned long long pOffset)
{
    if (pOffset & BITMASK_HEADER)
    {
        return 1;
    }
    return 0;
}

