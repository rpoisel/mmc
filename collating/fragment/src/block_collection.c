#include <stdlib.h>
#include <stdio.h>

#include "block_collection.h"

typedef unsigned long long storage_t;

#define STORAGE_SIZE(x) (x * BITS_PER_BLOCK / (sizeof(storage_t) * 8))

struct _block_collection_t
{
    storage_t* mBlockArray;
    unsigned mBlockSize;
    unsigned long long mMaxBlocks;
    unsigned long long mNumBlocks;
    unsigned long long mNumHeaders;
};

block_collection_t* block_collection_new(unsigned long long pMaxBlocks, unsigned pBlockSize)
{
    int lCnt = 0;

    block_collection_t* lHandle = (block_collection_t*)malloc(sizeof(block_collection_t));

    printf("Storage size: %llu\n", STORAGE_SIZE(pMaxBlocks));
    if (STORAGE_SIZE(pMaxBlocks) * sizeof(storage_t) > sizeof(storage_t))
    {
        lHandle->mBlockArray = (storage_t*)malloc(STORAGE_SIZE(pMaxBlocks) * sizeof(storage_t));
    }
    else
    {
        lHandle->mBlockArray = (storage_t*)malloc(sizeof(storage_t));
    }
    lHandle->mBlockSize = pBlockSize;
    lHandle->mMaxBlocks = pMaxBlocks;
    lHandle->mNumBlocks = 0;
    lHandle->mNumHeaders = 0;

    for (lCnt = 0; 
            lCnt < STORAGE_SIZE(pMaxBlocks); /* / sizeof(unsigned long long);  */
            ++lCnt)
    {
        lHandle->mBlockArray[lCnt] = 0;
    }

    return lHandle;
}

int block_collection_set(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader)
{
    unsigned long long lOffsetStorage = pOffset / (pCollection->mBlockSize * BLOCKS_PER_STORAGE);
    storage_t* lStorage = pCollection->mBlockArray + lOffsetStorage;
    unsigned lShifts = (BLOCKS_PER_STORAGE - 1 - (pOffset / pCollection->mBlockSize) % BLOCKS_PER_STORAGE) * BITS_PER_BLOCK;

    storage_t lBitmask = (((storage_t)0x01 | (pIsHeader ? 0x02 : 0x00)) << lShifts);
    (*lStorage) |= lBitmask;

    printf("Offset: %9llu, Bitmask: 0x%016llX, Storage: 0x%016llX, Offset Storage: %llu, Shifts: %u\n", 
            pOffset, lBitmask, *lStorage, lOffsetStorage, lShifts);

    /*
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
    */

    return 0;
}

#if 0
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
#endif

storage_t block_collection_get(block_collection_t* pCollection, 
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

