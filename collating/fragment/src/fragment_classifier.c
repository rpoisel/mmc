#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "fragment_classifier.h"
#include "ncd.h"

#define NUM_FILE_TYPES 3
#define NUM_FRAGS_PER_FILE_TYPE 10

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
    unsigned char* mReferenceFrags[NUM_FILE_TYPES][NUM_FRAGS_PER_FILE_TYPE];
};

static int check_ncd(FragmentClassifier* pFragmentClassifier, 
    const unsigned char* pFragment);

FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned int pFragmentSize)
{
    int lCntX = 0, lCntY = 0;

    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;
    for (lCntX = 0; lCntX < NUM_FILE_TYPES; lCntX++)
    {
        for (lCntY = 0; lCntY < NUM_FRAGS_PER_FILE_TYPE; lCntY++)
        {
            lHandle->mReferenceFrags[lCntX][lCntY] = 
                (unsigned char*)malloc(sizeof(unsigned char) * pFragmentSize);
        }
    }

    /* randomly read reference fragments */
    /* TODO check that the reference fragments do not contain 
     * header or footer material */

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    int lCntX = 0, lCntY = 0;

    /* free resources from the structure */
    for (lCntX = 0; lCntX < NUM_FILE_TYPES; lCntX++)
    {
        for (lCntY = 0; lCntY < NUM_FRAGS_PER_FILE_TYPE; lCntY++)
        {
            free(pFragmentClassifier->mReferenceFrags[lCntX][lCntY]);
        }
    }
    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment)
{
    if (1)
    {
        /* check for signatures */
    }
    else if (check_ncd(pFragmentClassifier, pFragment) == 0)
    {
        /* not relevant fragment */
        return 0;
    }
    else
    {
        /* check statistics */
    }
    /* do further tests here */

    /* relevant fragment */
    return 1;
}

static int check_ncd(FragmentClassifier* pFragmentClassifier, 
    const unsigned char* pFragment)
{
    /* FileType counter */
    int lCntFT = 0;

    for (lCntFT = 0; lCntFT < NUM_FILE_TYPES; lCntFT++)
    {
    }

    /* keep on processing this fragment */
    return 1;
}

