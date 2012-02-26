#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <string.h>

#include "fragment_classifier.h"
#include "fragment_classifier_p.h"

/* parameters */
#define PATH_LEN 256

/* features */
#define LOAD_SKEL 0

int load_classifier(ClassifyHandler* pHandle, 
        const char* pFilename, 
        unsigned pFragmentSize, 
        const char* pPath, 
        int pWeight);
void unload_classifier(ClassifyHandler* pHandle);

FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned pFragmentSize)
{
    char lPath[PATH_LEN] = { '\0' };

    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*) malloc(sizeof(struct _FragmentClassifier));
    if (!lHandle)
    {
        perror("Could not allocate memory for handle: ");
        return NULL;
    }
    lHandle->mNumClassifiers = 0;

    /* load ncd classifier START */
    strncpy(lPath, pFilename, PATH_LEN);
    strncat(lPath, "libfragment_classifier_ncd.so", PATH_LEN - strlen(lPath) - 1);
    if (load_classifier(lHandle->mClassifiers + lHandle->mNumClassifiers,
                "data/frags_ref", 
                pFragmentSize, 
                lPath, 
                1) < 0)
    {
        return NULL;
    }
    lHandle->mNumClassifiers++;
    /* load ncd classifier END */

#if LOAD_SKEL==1
    /* load skel classifier START */
    strncpy(lPath, pFilename, PATH_LEN);
    strncat(lPath, "libfragment_classifier_skel.so", PATH_LEN - strlen(lPath) - 1);
    if (load_classifier(lHandle->mClassifiers + lHandle->mNumClassifiers,
                "", 
                pFragmentSize, 
                lPath, 
                1) < 0)
    {
        return NULL;
    }
    lHandle->mNumClassifiers++;
    /* load skel classifier END */
#endif

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
        const char* pFilename, 
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

    pHandle->mFcHandler = (*pHandle->mFcNew)(pFilename, 
            pFragmentSize);
    return 0;
}

void unload_classifier(ClassifyHandler* pHandle)
{
    (*pHandle->mFcFree)(pHandle->mFcHandler);
    dlclose(pHandle->mSoHandler);
}
