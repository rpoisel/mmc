/* TODO this file should be called block_reader_nofs.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef _MSC_VER
#include <magic.h>
#else
/* for the windows port see the following URL: */
/* http://msdn.microsoft.com/en-us/library/windows/desktop/ms682516(v=vs.85).aspx */
/* http://msdn.microsoft.com/en-us/library/kdzttdcb(v=vs.71).aspx */
#include "magic.h"
#endif

#include "os_def.h"
#include "block_reader.h"

/* TODO put in separate c-file; definition in separate h-file */
int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo);

/* TODO this is part of the non-fs based classifier */
/* TODO pNumBlocks is not relevant for fs based classifiers */
fragment_collection_t* classify(int pBlockSize, 
        int pNumBlocks, /* TODO only non-fs relevant */
        const char* pImage, 
        unsigned long long pOffset, 
        ClassifyT* pTypes, 
        int pNumTypes, 
        unsigned long long pBlockGap,
        unsigned long long pMinFragSize,
        int pNumThreads)
{
    FragmentClassifier* lHandle = NULL;
    block_collection_t* lBlocks = NULL;
    fragment_collection_t* lFragments = NULL;

    lHandle = fragment_classifier_new_ct(NULL, 0, pBlockSize, pTypes, pNumTypes);
    if (!lHandle)
    {
        return NULL;
    }

    lBlocks = block_collection_new(pNumBlocks, pBlockSize); 

    /* start multithreaded classification process */
    fragment_classifier_classify_mt(lHandle, callback_collect, 
            lBlocks /* callback data */, pImage, pOffset, pNumBlocks, 
            /* colons do not work in windows; thus one file is used only */
            PATH_MAGIC,
            pNumThreads);

    /* factor 1/4 is just an empirical value */
    /* TODO perform this step on several CPU cores */
    lFragments = fragment_collection_new(lBlocks, 4, pOffset, 
            pBlockGap, pMinFragSize);

    /* destruct fragment classifier */
    block_collection_free(lBlocks);
    fragment_classifier_free(lHandle);

    return lFragments;
}

/* TODO this is part of the non-fs based classifier */
void classify_free(fragment_collection_t* pCollection)
{
    fragment_collection_free(pCollection);
}

/* generally valid call-back */
/* TODO put in separate c-file; definition in separate h-file */
int callback_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo)
{
    block_collection_t* pBlocks = (block_collection_t* )pData;
    /* store classified block */
    return block_collection_set(pBlocks, pOffset, pIsHeader);
}
