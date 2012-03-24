#ifndef __BLOCK_READER_H__
#define __BLOCK_READER_H__ 1

#include "fragment_classifier.h"
#include "block_collection.h"

typedef struct
{
    unsigned long long mOffset;
    unsigned long long mSize;
    unsigned long long mNextIdx;
    int mIsHeader;
} fragment_t;

typedef struct
{
    unsigned long long mNumFrags;
    fragment_t* mFrags;
} fragment_collection_t;

fragment_collection_t* classify(int pBlockSize, 
        int pNumBlocks, 
        const char* pImage, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        int pNumThreads); 

void classify_free(fragment_collection_t* pCollection);

#endif /* __BLOCK_READER_H__ */
