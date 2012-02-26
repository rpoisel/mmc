#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <string.h>

#include "fragment_classifier.h"
#include "fragment_classifier_p.h"
#include "fragment_classifier_py.h"

/* parameters */
#define PATH_LEN 256
#define NUM_OPTIONS 2

/* features */
#define LOAD_SKEL 0

int load_classifier(ClassifyHandler* pHandle, 
        ClassifyOptions* pOptions, 
        unsigned pFragmentSize, 
        const char* pPath, 
        int pWeight);
void unload_classifier(ClassifyHandler* pHandle);

FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned int pNumSo, 
        unsigned int pFragmentSize)
{
    char lPath[PATH_LEN] = { '\0' };
    int lCnt = 0;

    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*) malloc(sizeof(struct _FragmentClassifier));
    if (!lHandle)
    {
        perror("Could not allocate memory for handle: ");
        return NULL;
    }
    lHandle->mNumClassifiers = pNumSo;

    for (lCnt = 0; lCnt < lHandle->mNumClassifiers; lCnt++)
    {
        if (load_classifier(lHandle->mClassifiers + lCnt,
                (pOptions + lCnt), 
                pFragmentSize, 
                (pOptions + lCnt)->mSoName, 
                (pOptions + lCnt)->mWeight) < 0)
        {
            return NULL;
        }
    }

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    int lCnt = 0;

    /* free loaded shared libraries */
    for (lCnt = 0; lCnt < pFragmentClassifier->mNumClassifiers; lCnt++)
    {
        unload_classifier(pFragmentClassifier->mClassifiers + lCnt);
    }

    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    int lCnt = 0;
    int lReturn = 0;
    ClassifyHandler* lHandler = NULL;

    /* invoke loaded classifiers */
    for (lCnt = 0; lCnt < pFragmentClassifier->mNumClassifiers; lCnt++)
    {
        lHandler = pFragmentClassifier->mClassifiers + lCnt;
        lReturn += (lHandler->mWeight * (*lHandler->mFcClassify)(
                lHandler->mFcHandler, 
                pFragment, 
                pLen));
    }

    return lReturn;
}

int load_classifier(ClassifyHandler* pHandle, 
        ClassifyOptions* pOptions, 
        unsigned pFragmentSize, 
        const char* pPath, 
        int pWeight)
{
    pHandle->mSoHandler = dlopen(pPath, RTLD_LAZY);

    if (!pHandle->mSoHandler)
    {
        fprintf(stderr, "Could not load shared object: %s\n", 
                dlerror());
        return -1;
    }
    pHandle->mWeight = pWeight;

    pHandle->mFcNew = dlsym(pHandle->mSoHandler, 
            "fragment_classifier_new");
    pHandle->mFcClassify = dlsym(pHandle->mSoHandler, 
            "fragment_classifier_classify");
    pHandle->mFcFree = dlsym(pHandle->mSoHandler, 
            "fragment_classifier_free");

    pHandle->mFcHandler = (*pHandle->mFcNew)(pOptions, 
            0, 
            pFragmentSize);
    return 0;
}

void unload_classifier(ClassifyHandler* pHandle)
{
    (*pHandle->mFcFree)(pHandle->mFcHandler);
    dlclose(pHandle->mSoHandler);
}

FragmentClassifier* fragment_classifier_py(const char* pFragsRefDir,
        unsigned int pFragmentSize)
{
    ClassifyOptions lOptions[NUM_OPTIONS];

    /* ncd */
    strncpy(lOptions[0].mSoName, "collating/fragment/libfragment_classifier_ncd.so", MAX_STR_LEN);
    lOptions[0].mWeight = 1;
    strncpy(lOptions[0].mOption1, pFragsRefDir, MAX_STR_LEN);
    /* skel */
    strncpy(lOptions[1].mSoName, "collating/fragment//libfragment_classifier_skel.so", MAX_STR_LEN);
    lOptions[1].mWeight = 0;

    return fragment_classifier_new(lOptions, NUM_OPTIONS, pFragmentSize);
}

