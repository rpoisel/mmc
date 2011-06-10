#include "ncd.h"

#include <assert.h>
#include <zlib.h>

#define LEVEL 9

int ncd(unsigned char* pFragment1, unsigned char* pFragment2, 
        unsigned int pSizeInput, unsigned int pSizeOutput)
{
    /* TODO change the return value */
    return -1;
}

static int def(unsigned char* bufInput, unsigned char* bufOutput, 
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

