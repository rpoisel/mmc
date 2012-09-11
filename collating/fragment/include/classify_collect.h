#ifndef __CLASSIFY_COLLECT_H__
#define __CLASSIFY_COLLECT_H__ 1

#include "block_classifier.h"
#include "fragment_collection.h"

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

__declspec(dllexport) fragment_collection_t* classify_nofs(
        unsigned long long pImageSize, 
        unsigned pBlockSize, 
        unsigned pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize, 
        const char* pPathMagic,
        int pNumThreads); 

__declspec(dllexport) fragment_collection_t* classify_tsk(
        unsigned long long pImageSize, 
        unsigned pBlockSize, 
        unsigned pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize, 
        const char* pPathMagic,
        int pNumThreads); 

__declspec(dllexport) void classify_free(fragment_collection_t* pCollection);

#endif /* __CLASSIFY_COLLECT_H__ */
