#include <stdlib.h>
#include <stdio.h>

#include "fragment_collection.h"

#define DEBUG 0

static int sort_callback(const void* pFrag1, const void* pFrag2);
static int fragment_collection_add(fragment_collection_t* , 
        fragment_t* , unsigned long long, unsigned long long);

fragment_collection_t* fragment_collection_new(
        block_collection_t* pBlocks, 
        int pFactor,
        unsigned long long pOffset, 
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

        /* deterine if it is a relevant block */
        if (BLOCK(lBlockTmp))
        {
            /* determine if current block is a header block */
            if (HEADER(lBlockTmp))
            {
                /* temporary fragment is already existing */
                if (lFlagExisting)
                {
                    if (fragment_collection_add(lFragments, &lFragTmp, pOffset, pMinFragSize * lBlockSize) != 0)
                    {
                        /* fragments buffer full => quit */
                        break;
                    }
                }
                /* reset lFragTmp to start a new fragment */
                lFragTmp = (fragment_t){ lBlockSize * lCntBlock, lBlockSize, -1, 1, "", "", 0 };
                lBlockGap = 0;
            }
            else /* non-header fragment */
            {
                /* start new fragment or update current fragment depending on
                 * block gap being reached */
                if (lFlagExisting)
                {
                    if (lBlockGap <= pBlockGap)
                    {
                        lFragTmp.mSize = (lBlockSize + 1) * lCntBlock - lFragTmp.mOffset;
#if DEBUG == 1
                        printf("Fragment offset: %llu, size: %llu\n", 
                                lFragTmp.mOffset,
                                lFragTmp.mSize);
#endif
                    }
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
                if (fragment_collection_add(lFragments, &lFragTmp, pOffset, pMinFragSize * lBlockSize) != 0)
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

    if (lFlagExisting && lFragTmp.mSize > 0)
    {
        /* TODO check if buffer full */
        fragment_collection_add(lFragments, &lFragTmp, pOffset, pMinFragSize * lBlockSize);
    }


    /* sort fragments */
    qsort(lFragments->mFrags, lFragments->mNumFrags, sizeof(fragment_t),
            sort_callback);

    return lFragments;
}

static int sort_callback(const void* pFrag1, const void* pFrag2)
{
    if (((const fragment_t* )pFrag1)->mIsHeader &&
            !((const fragment_t* )pFrag2)->mIsHeader)
    {
        return -1;
    }
    else if (!((const fragment_t* )pFrag1)->mIsHeader &&
            ((const fragment_t* )pFrag2)->mIsHeader)
    {
        return 1;
    }

    return 0;
}

static int fragment_collection_add(fragment_collection_t* pFragments, 
        fragment_t* pFragment, 
        unsigned long long pOffset, 
        unsigned long long pMinFragSize)
{
#if DEBUG == 1
    printf("Offset: %lld, Size: %lld%s\n",
            pFragment->mOffset,
            pFragment->mSize,
            pFragment->mIsHeader ? ", Header" : "");
#endif
    /* buffer full condition */
    if (pFragments->mNumFrags >= pFragments->mMaxFrags)
    {
        return -1;
    }
    /* fragment is too small */
    else if (pFragment->mSize <= pMinFragSize && !pFragment->mIsHeader)
    {
        return 0; /* this is not an error case */
    }

    /* add fragment to buffer */
    *(pFragments->mFrags + pFragments->mNumFrags) = *pFragment;
    (pFragments->mFrags + pFragments->mNumFrags)->mOffset += pOffset;
    (pFragments->mNumFrags)++;

    return 0;
}

void fragment_collection_free(
        fragment_collection_t* pCollection)
{
    free(pCollection->mFrags);
    free(pCollection);
}
