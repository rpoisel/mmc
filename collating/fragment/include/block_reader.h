#ifndef __BLOCK_READER_H__
#define __BLOCK_READER_H__ 1

#include "fragment_classifier.h"
#include "block_collection.h"
#include "fragment_collection.h"

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

#if defined __linux__
#define PATH_MAGIC "collating/fragment/data/magic/media.mgc"
#elif defined _WIN32 || defined _WIN64
#define PATH_MAGIC "collating\\fragment\\data\\magic\\media.mgc"
#endif

__declspec(dllexport) fragment_collection_t* classify(int pBlockSize, 
        int pNumBlocks, 
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize, 
        int pNumThreads); 

__declspec(dllexport) void classify_free(fragment_collection_t* pCollection);

#endif /* __BLOCK_READER_H__ */
