#ifndef __BLOCK_READER_H__
#define __BLOCK_READER_H__ 1

#include "fragment_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"

fragment_collection_t* classify(int pBlockSize, 
        int pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize, 
        int pNumThreads); 

void classify_free(fragment_collection_t* pCollection);

#endif /* __BLOCK_READER_H__ */
