#include <stdlib.h>
#include <stdio.h>

#include "block_collection.h"

#define STORAGE_SIZE(x) (x * BITS_PER_BLOCK / (sizeof(unsigned long long) * 8))

struct _block_collection_t
{
    unsigned long long* mBlockArray;
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
    lHandle->mBlockArray = (unsigned long long*)malloc(STORAGE_SIZE(pMaxBlocks) > sizeof(unsigned long long) ? STORAGE_SIZE(pMaxBlocks) : sizeof(unsigned long long));
    lHandle->mBlockSize = pBlockSize;
    lHandle->mMaxBlocks = pMaxBlocks;
    lHandle->mNumBlocks = 0;
    lHandle->mNumHeaders = 0;

    for (lCnt = 0; 
            lCnt <= STORAGE_SIZE(pMaxBlocks) / sizeof(unsigned long long); 
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
    unsigned long long* lStorage = pCollection->mBlockArray + lOffsetStorage;
    unsigned lShifts = (BLOCKS_PER_STORAGE - 1 - (pOffset / pCollection->mBlockSize) % BLOCKS_PER_STORAGE) * BITS_PER_BLOCK;

    unsigned long long lBitmask = (((unsigned long long)0x01 | (pIsHeader ? 0x02 : 0x00)) << lShifts);
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

