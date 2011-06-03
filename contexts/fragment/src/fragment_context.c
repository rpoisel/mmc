#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "fragment_context.h"

struct _FragmentContext
{
};

/* FragmentContext* fragment_classifier_new(const char* pFilename) */
FragmentContext* fragment_classifier_new()
{
    return NULL;
}

void fragment_classifier_free(FragmentContext* pFragmentContext)
{
}

/* int fragment_classifier_classify(FragmentContext* pFragmentContext, const uint8_t* pBuf, int pBufLength) */
int fragment_classifier_classify(FragmentContext* pFragmentContext, int pBufLength)
{
    int lCnt = 0;
#if 0
    printf("Length: %d\n", pBufLength);
    for (lCnt = 0; lCnt < pBufLength; lCnt++)
    {
        printf("%02X ", pBuf[lCnt]);
        if ((lCnt % 16) == 15)
        {
            printf("\n");
        }
    }
#endif

    /* success */
    return 1;
}
