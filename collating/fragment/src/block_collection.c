#include <stdlib.h>
#include <stdio.h>

#include "logging.h"
#include "block_collection.h"

/* no ceiling performed */
#define STORAGE_SIZE(x) (x * BITS_PER_BLOCK / (sizeof(storage_t) * 8) + 1)

struct _block_collection_t
{
    storage_t* mBlockArray;
    unsigned mBlockSize;
    unsigned long long mMaxBlocks;
    unsigned long long mNumHeaders;
};

block_collection_t* block_collection_new(unsigned long long pMaxBlocks, unsigned pBlockSize)
{
    unsigned lCnt = 0;

    block_collection_t* lHandle = (block_collection_t*)malloc(sizeof(block_collection_t));

    LOGGING_INFO("Storage size: %llu, Max Blocks: %lld\n", STORAGE_SIZE(pMaxBlocks), pMaxBlocks);

    if (STORAGE_SIZE(pMaxBlocks) * sizeof(storage_t) > sizeof(storage_t))
    {
        LOGGING_INFO("Allocating %llu bytes of memory. \n",
                STORAGE_SIZE(pMaxBlocks) * sizeof(storage_t))
        lHandle->mBlockArray = (storage_t*)malloc(STORAGE_SIZE(pMaxBlocks) * sizeof(storage_t));
    }
    else
    {
        lHandle->mBlockArray = (storage_t*)malloc(sizeof(storage_t));
        LOGGING_INFO("Allocating %lu bytes of memory. \n",
                sizeof(storage_t))
    }
    lHandle->mBlockSize = pBlockSize;
    lHandle->mMaxBlocks = pMaxBlocks;
    lHandle->mNumHeaders = 0;

    for (lCnt = 0; 
            lCnt < STORAGE_SIZE(pMaxBlocks);
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

    storage_t lBitmask = ((pIsHeader ? (storage_t)0x03 : (storage_t)0x01) << lShifts);
    (*lStorage) |= lBitmask;

    pCollection->mNumHeaders += (pIsHeader ? 1 : 0);

    LOGGING_DEBUG("Block %9llu, Bitmask: 0x%016llX, Storage: 0x%016llX, " \
            "Offset Storage: %05llu, Shifts: %02u\n", 
            pOffset, lBitmask, *lStorage, lOffsetStorage, lShifts);

    return 0;
}

int block_collection_set_range(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader, unsigned pRangeSize)
{
    unsigned lCnt = 0;

    for (lCnt = 0;
            lCnt < (pRangeSize / pCollection->mBlockSize + (pRangeSize % pCollection->mBlockSize != 0 ? 1 : 0));
            lCnt++)
    {
        block_collection_set(pCollection,
                pOffset + lCnt,
                pIsHeader);
    }

    LOGGING_DEBUG("Block size: %lld, Range size: %lld, Offset: %lld, Max Count size: %u\n",
            pCollection->mBlockSize,
            pRangeSize,
            pOffset,
            (pRangeSize / pCollection->mBlockSize + (pRangeSize % pCollection->mBlockSize != 0 ? 1 : 0))
            );
    return 0;
}

storage_t block_collection_get(block_collection_t* pCollection, 
        unsigned long long pOffset)
{
    unsigned long long lOffsetStorage = pOffset / BLOCKS_PER_STORAGE;
    storage_t* lStorage = pCollection->mBlockArray + lOffsetStorage;
    unsigned lShifts = (BLOCKS_PER_STORAGE - 1 - pOffset % BLOCKS_PER_STORAGE) * BITS_PER_BLOCK;

    /* printf("Storage: 0x%llx, Shifts: %u\n", *lStorage, lShifts); */
    return ((*lStorage) & ((storage_t)0x03 << lShifts)) >> lShifts;
}

unsigned long long block_collection_len(block_collection_t* pCollection)
{
    return pCollection->mMaxBlocks;
}

unsigned block_collection_get_bs(block_collection_t* pCollection)
{
    return pCollection->mBlockSize;
}

void block_collection_free(block_collection_t* pCollection)
{
    LOGGING_INFO("Freeing block collection memory. \n")

    free(pCollection->mBlockArray);
    free(pCollection);
}

