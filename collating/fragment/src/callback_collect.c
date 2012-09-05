#include "callback_collect.h"

#include "block_collection.h"

int classify_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo)
{
    block_collection_t* pBlocks = (block_collection_t* )pData;
    /* store classified block */
    return block_collection_set(pBlocks, pOffset, pIsHeader);
}

