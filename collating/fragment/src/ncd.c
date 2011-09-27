#include "ncd.h"

#include <string.h>
#include <assert.h>
#include <stdio.h>

#ifdef _MSC_VER
#include "zlib.h"
#define ZLIB_WINAPI
#else
#include <zlib.h>
#endif

#define LEVEL 9
#define MIN(a,b) ((a)>(b)?(b):(a))
#define MAX(a,b) ((a)<(b)?(b):(a))

static int deflate_zlib(unsigned const char* bufInput, unsigned const char* bufOutput, 
        unsigned int pSizeInput, unsigned int pSizeOutput);

double ncd(unsigned const char* pFragment1, unsigned const char* pFragment2, unsigned int pFragmentSize)
{
    
    unsigned char lBufFrags[MAX_FRAG_SIZE];
    unsigned char lBufFragsCompr[MAX_FRAG_SIZE];
    int lCxy = 0;
    int lCx = 0;
    int lCy = 0;

#if 0
    for (lCx = 0; lCx < pFragmentSize; lCx++)
    {
        fprintf(stderr, "0x%02X ", pFragment2[lCx]);
        if ((lCx + 1) % 16 == 0)
        {
            fprintf(stderr, "\n");
        }
    }
#endif

    memcpy(lBufFrags, pFragment1, pFragmentSize);
    memcpy(lBufFrags + pFragmentSize, pFragment2, pFragmentSize);

    lCxy = deflate_zlib(lBufFrags, lBufFragsCompr, 
            2 * pFragmentSize, MAX_FRAG_SIZE);
    lCx = deflate_zlib(pFragment1, lBufFragsCompr, 
            pFragmentSize, MAX_FRAG_SIZE);
    lCy = deflate_zlib(pFragment2, lBufFragsCompr, 
            pFragmentSize, MAX_FRAG_SIZE);

#if 0
    fprintf(stderr, "lCxy: %d, lCx: %d, lCy: %d\n", lCxy, lCx, lCy);
#endif

    return ((double)(lCxy - MIN(lCx, lCy))) / (double)(MAX(lCx, lCy));
}

static int deflate_zlib(unsigned const char* bufInput, unsigned const char* bufOutput, 
        unsigned int pSizeInput, unsigned int pSizeOutput)
{
    int lRet;
    unsigned lNumBytesCompressed;
    z_stream strm;

    /* allocate deflate state */
    strm.zalloc = Z_NULL;
    strm.zfree = Z_NULL;
    strm.opaque = Z_NULL;
    lRet = deflateInit(&strm, LEVEL);
    if (lRet != Z_OK)
        return lRet;

    strm.avail_in = pSizeInput;
    strm.next_in = bufInput;

    /* run deflate() on input until output buffer not full, finish
       compression if all of source has been read in */
    strm.avail_out = pSizeOutput;
    strm.next_out = bufOutput;
    lRet = deflate(&strm, Z_FINISH);    /* no bad return value */
    assert(lRet != Z_STREAM_ERROR);  /* state not clobbered */
    assert(strm.avail_out != 0);
    lNumBytesCompressed = pSizeOutput - strm.avail_out;
    assert(strm.avail_in == 0);     /* all input will be used */

    /* clean up and return */
    (void)deflateEnd(&strm);
    return lNumBytesCompressed;
}

