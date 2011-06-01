#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "fragment_context.h"

int classify(const uint8_t* pBuf, int pBufLength)
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
