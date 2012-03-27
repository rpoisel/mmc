#include <stdlib.h>
#include <stdio.h>

#include "fragment_collection.h"

#define DEBUG 0

static int fragment_collection_add(fragment_collection_t* , 
        fragment_t* , unsigned long long);

fragment_collection_t* fragment_collection_new(
        block_collection_t* pBlocks, 
        int pFactor,
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize)
{
    unsigned long long lCntBlock = 0;
    storage_t lBlockTmp = 0;
    unsigned long long lBlockGap = 0;
    int lFlagExisting = 0;
    unsigned lBlockSize = block_collection_get_bs(pBlocks);
    fragment_t lFragTmp = { 0, 0, -1, 0, "", "", 0 };

    fragment_collection_t* lFragments = 
        (fragment_collection_t* )malloc(sizeof(fragment_collection_t));

    lFragments->mNumFrags = 0;
    lFragments->mMaxFrags = block_collection_len(pBlocks) / pFactor;
#if DEBUG == 1
    printf("Max Frags: %lld\n", lFragments->mMaxFrags);
#endif
    lFragments->mFrags = (fragment_t* )malloc(sizeof(fragment_t) * \
            lFragments->mMaxFrags);

    for(lCntBlock = 0; 
            lCntBlock < block_collection_len(pBlocks); 
            ++lCntBlock)
    {
        lBlockTmp = block_collection_get(pBlocks, lCntBlock);

        if (BLOCK(lBlockTmp))
        {
            if (HEADER(lBlockTmp))
            {
                /* reset lFragTmp to start a new fragment */
                lFragTmp = (fragment_t){ lBlockSize * lCntBlock, lBlockSize, -1, 1, "", "", 0 };
                lBlockGap = 0;
            }
            else /* non-header fragment */
            {
                /* start new fragment or update current fragment depending on
                 * block gap being reached */
                if (lBlockGap <= pBlockGap && lFlagExisting)
                {
                    lFragTmp.mSize = lBlockSize * lCntBlock - lFragTmp.mOffset;
                }
                else
                {
                    lFragTmp = (fragment_t){ lBlockSize * lCntBlock, lBlockSize, -1, 0, "", "", 0 };
                }
                lBlockGap = 0;
            }
            lFlagExisting = 1;
        }
        else
        {
            /* determine if block gap has been reached */
            /* if yes, add the fragment and set conditions to start a new one */
            if (lBlockGap > pBlockGap)
            {
                if (fragment_collection_add(lFragments, &lFragTmp, pMinFragSize * lBlockSize) != 0)
                {
                    /* fragments buffer full => quit */
                    break;
                }
                lBlockGap = 0;
                lFlagExisting = 0;
            }
            else if (lFlagExisting)
            {
                lBlockGap += lBlockSize;
            }
        }
    }

    return lFragments;
}

static int fragment_collection_add(fragment_collection_t* pFragments, 
        fragment_t* pFragment, 
        unsigned long long pMinFragSize)
{
    /* buffer full condition */
    if (pFragments->mNumFrags >= pFragments->mMaxFrags)
    {
        return -1;
    }
    else if (pFragment->mSize <= pMinFragSize)
    {
        return 0;
    }

    /* add fragment to buffer */
    *(pFragments->mFrags + pFragments->mNumFrags) = *pFragment;
    (pFragments->mNumFrags)++;

    return 0;
}

void fragment_collection_free(
        fragment_collection_t* pCollection)
{
    free(pCollection->mFrags);
    free(pCollection);
}
