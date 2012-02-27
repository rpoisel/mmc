#include <math.h>
#include <stdint.h>

#include "entropy.h"

#define MAX_FRAG_SIZE 4096

float calc_entropy(const unsigned char* pFragment, int pLen)
{
    /* http://stackoverflow.com/questions/990477/how-to-calculate-the-entropy-of-a-file */
    /* (float) entropy = 0
     * for i in the array[256]:Counts do 
     *   (float)p = Counts[i] / filesize
     *     if (p > 0) entropy = entropy - p*lg(p) // lgN is the logarithm with base 2
     */

    float entropy = 0;
    float p = 0;
    int lCnt = 0;
    int16_t lCounts[256];

    /* calculate binary distribution */
    for (lCnt = 0; lCnt < pLen; lCnt++)
    {
        lCounts[pFragment[lCnt]]++;
    }

    /* calculate information entropy */
    /* TODO correct this formula */
    for (lCnt = 0; lCnt < 256; lCnt++)
    {
        p = lCounts[lCnt] / pLen;
        if (p > 0)
        {
            entropy -= p * log(p) / log(2);
        }
    }

    entropy /= 8;

    return entropy;
}
