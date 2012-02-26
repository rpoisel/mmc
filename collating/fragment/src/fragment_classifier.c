#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

#include "fragment_classifier.h"
#include "fragment_classifier_p.h"

FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned pFragmentSize)
{
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*) malloc(sizeof(struct _FragmentClassifier));
    if (!lHandle)
    {
        perror("Could not allocate memory for handle: ");
        return NULL;
    }
    lHandle->mNumClassifiers = 0;

    /* load ncd classifier START */
    if (load_classifier(lHandle->mClassifiers + lHandle->mNumClassifiers,
                pFilename, 
                pFragmentSize, 
                "./collating/fragment/libfragment_classifier_ncd.so",
                1) < 0)
    {
        return NULL;
    }
    /* load ncd classifier END */

    lHandle->mNumClassifiers++;

    return lHandle;
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
        fprintf(stderr, "Could not load shared object: %s\n", dlerror());
        return -1;
    }
    pHandle->mWeight = pWeight;

    pHandle->mFcNew = dlsym(pHandle->mSoHandler, "fragment_classifier_new");
    pHandle->mFcClassify = dlsym(pHandle->mSoHandler, "fragment_classifier_classify");
    pHandle->mFcFree = dlsym(pHandle->mSoHandler, "fragment_classifier_free");

    pHandle->mFcHandler = (*pHandle->mFcNew)(pFilename, pFragmentSize);
    return 0;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    int lCnt = 0;

    /* free loaded shared libraries */
    for (lCnt = 0; lCnt < pFragmentClassifier->mNumClassifiers; lCnt++)
    {
        (*pFragmentClassifier->mClassifiers[lCnt].mFcFree)(pFragmentClassifier->mClassifiers[lCnt].mFcHandler);
        dlclose(pFragmentClassifier->mClassifiers[lCnt].mSoHandler);
    }

    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    int lCnt = 0;
    int lReturn = 0;

    /* invoke loaded classifiers */
    for (lCnt = 0; lCnt < pFragmentClassifier->mNumClassifiers; lCnt++)
    {
        lReturn += (pFragmentClassifier->mClassifiers[lCnt].mWeight * (*pFragmentClassifier->mClassifiers[lCnt].mFcClassify)(
                pFragmentClassifier->mClassifiers[lCnt].mFcHandler, 
                pFragment, 
                pLen));
    }

    return lReturn;
}

