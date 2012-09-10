#include "callback_collect.h"

#include "block_collection.h"
#include "logging.h"
#include "os_def.h"

int classify_collect(
        void* pData, unsigned long long pOffset, unsigned pSizeRange, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo
        )
{
    UNUSED(pType);
    UNUSED(pStrength);
    UNUSED(pInfo);

    block_collection_t* pBlocks = (block_collection_t* )pData;
    /* store classified block */
    return block_collection_set_range(pBlocks, pOffset,
            pIsHeader, pSizeRange);
}
