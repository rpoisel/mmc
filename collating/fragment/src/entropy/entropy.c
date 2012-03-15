#include <math.h>
#include <stdio.h>

#ifdef _MSC_VER
#include "stdint_ms.h"
#else 
#include <stdint.h>
#endif /* _MSC_VER */

#include "entropy.h"

#define MAX_FRAG_SIZE 4096

float calc_entropy(const unsigned char* pFragment, int pLen)
{
    /* http://stackoverflow.com/questions/990477/how-to-calculate-the-entropy-of-a-file */
    /* http://ezbitz.com/2009/05/08/calculate-a-file-shannon-entropy-in-c/ */
    /* (float) entropy = 0
     * for i in the array[256]:Counts do 
     *   (float)p = Counts[i] / filesize
     *     if (p > 0) entropy = entropy - p*lg(p) // lgN is the logarithm with base 2
     */

    float entropy = 0;
    float p = 0;
    int lCnt = 0;
    int16_t lCounts[256] = { 0 };
    float log2 = log(2);

    /* calculate binary distribution */
    for (lCnt = 0; lCnt < pLen; lCnt++)
    {
        lCounts[pFragment[lCnt]]++;
    }

    /* calculate information entropy */
    for (lCnt = 0; lCnt < 256; lCnt++)
    {
        p = (float)lCounts[lCnt] / (float)pLen;
        if (p > 0)
        {
            entropy -= p * log(p) / log2;
        }
    }

    entropy /= 8;

    return entropy;
}
