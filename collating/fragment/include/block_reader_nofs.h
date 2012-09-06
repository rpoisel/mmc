#ifndef __BLOCK_READER_NOFS_H__
#define __BLOCK_READER_NOFS_H__ 1

#include "block_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"

int block_classify_nofs_mt(
        BlockClassifier* pBlockClassifier, 
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, 
        unsigned long long pSizeReal, 
        const char* pPathMagic, 
        unsigned int pNumThreads);

#endif /* __BLOCK_READER_NOFS_H__ */
