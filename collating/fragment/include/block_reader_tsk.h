#ifndef __BLOCK_READER_TSK_H__
#define __BLOCK_READER_TSK_H__ 1

#include "block_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"

int block_classify_tsk_mt(
        BlockClassifier* pBlockClassifier,
        fragment_cb pCallback, 
        void* pCallbackData, 
        const char* pImage, 
        unsigned long long pOffset, /* ignored */
        unsigned long long pSizeReal, /* ignored */
        const char* pPathMagic, 
        unsigned int pNumThreads
        );

#endif /* __BLOCK_READER_TSK_H__ */
