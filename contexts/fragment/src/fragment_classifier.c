#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "fragment_classifier.h"

struct _FragmentClassifier
{
    int mSomething;
};

FragmentClassifier* fragment_classifier_new(const char* pFilename)
{
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));
    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pBuf, int pBufLength)
{
#if 1
    int lCnt = 0;
    printf("Length: %d\n", pBufLength);
    for (lCnt = 0; lCnt < pBufLength; lCnt++)
    {
        printf("%02X ", pBuf[lCnt]);
        if ((lCnt % 16) == 15)
        {
            printf("\n");
        }
    }
    printf("\n");
#endif

    /* success */
    return 1;
}
