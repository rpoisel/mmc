#ifndef __FRAGMENT_COLLECTION__H_
#define __FRAGMENT_COLLECTION__H_ 1

#include "block_collection.h"

typedef struct
{
    unsigned long long mOffset;
    unsigned long long mSize;
    long long mNextIdx;
    int mIsHeader;
    char* mPicBegin;
    char* mPicEnd;
    int mIsSmall;
} fragment_t;

typedef struct
{
    unsigned long long mNumFrags;
    unsigned long long mMaxFrags;
    fragment_t* mFrags;
} fragment_collection_t;

fragment_collection_t* fragment_collection_new(
        block_collection_t* pBlocks, 
        int pFactor,
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize);

void fragment_collection_free(
        fragment_collection_t* pCollection);

#endif
