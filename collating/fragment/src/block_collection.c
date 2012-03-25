#include <stdlib.h>
#include <stdio.h>

#include "block_collection.h"

#define DEBUG 0

typedef unsigned long long storage_t;

/* no ceiling performed */
#define STORAGE_SIZE(x) (x * BITS_PER_BLOCK / (sizeof(storage_t) * 8) + 1)

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

#if DEBUG == 1
    printf("Storage size: %llu, Max Blocks: %lld\n", STORAGE_SIZE(pMaxBlocks), pMaxBlocks);
#endif
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
    unsigned long long lOffsetStorage = pOffset / BLOCKS_PER_STORAGE;
    storage_t* lStorage = pCollection->mBlockArray + lOffsetStorage;
    unsigned lShifts = (BLOCKS_PER_STORAGE - 1 - pOffset % BLOCKS_PER_STORAGE) * BITS_PER_BLOCK;

    storage_t lBitmask = (((storage_t)0x01 | (pIsHeader ? 0x02 : 0x00)) << lShifts);
    (*lStorage) |= lBitmask;

    ++pCollection->mNumBlocks;
    pCollection->mNumHeaders += (pIsHeader ? 1 : 0);

#if DEBUG == 1
    printf("Offset: %9llu, Bitmask: 0x%016llX, Storage: 0x%016llX, Offset Storage: %05llu, Shifts: %02u\n", 
            pOffset, lBitmask, *lStorage, lOffsetStorage, lShifts);
#endif

    return 0;
}

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

