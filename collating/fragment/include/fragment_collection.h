#ifndef __FRAGMENT_COLLECTION__H_
#define __FRAGMENT_COLLECTION__H_ 1

#include "block_collection.h"

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

typedef struct
{
    unsigned long long mOffset;
    unsigned long long mSize;
    int mIsHeader;
    int mIsFooter;
    char* mPicBegin;
    char* mPicEnd;
    int mIsSmall;
    int mIdxDecode;
    int mIdxFile;
} fragment_t;

typedef struct
{
    unsigned long long mNumFrags;
    unsigned long long mMaxFrags;
    fragment_t* mFrags;
} fragment_collection_t;

__declspec(dllexport) fragment_collection_t* fragment_collection_new(
        block_collection_t* pBlocks, 
        int pFactor,
        unsigned long long pOffset, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize);

__declspec(dllexport) void fragment_collection_free(
        fragment_collection_t* pCollection);

#endif
