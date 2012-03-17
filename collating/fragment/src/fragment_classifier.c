#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#include "fragment_classifier.h"
#include "entropy/entropy.h"

/* turn to 1 for verbose messages */
#define VERBOSE 0
#define MAX_FILETYPES 24

struct _FragmentClassifier
{
    unsigned mFragmentSize;
    ClassifyT mFileTypes[MAX_FILETYPES];
    unsigned mNumFileTypes;
};

FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize)
{
    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;

    /* initialize fields that are not used regularely with
     * illegal values */
    lHandle->mNumFileTypes = 0;

    return lHandle;
}

FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned pNumSo, 
        unsigned pFragmentSize,
        ClassifyT* pTypes,
        unsigned pNumTypes)
{
    struct _FragmentClassifier* lHandle = fragment_classifier_new(
            pOptions,
            pNumSo,
            pFragmentSize);

    /* initialize additional fields */
    memcpy(lHandle->mFileTypes, pTypes, sizeof(ClassifyT) * pNumTypes);
    lHandle->mNumFileTypes = pNumTypes;

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    /* free handle resources */
    free(pFragmentClassifier);
}

int fragment_classifier_classify_result(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen,
        ClassifyT* pResult)

{
    float lEntropy = 0;
    /* non-relevant fragment <= 0 > relevant fragment */

    pResult->mType = FT_UNKNOWN;
    pResult->mStrength = 0;

    if (pLen == 0)
    {
        return 0;
    }

    lEntropy = calc_entropy(pFragment, pLen);
    if (lEntropy > 0.625) /* empiric value ;-) */
    {
        pResult->mType = FT_HIGH_ENTROPY;
        pResult->mStrength = 1;
    }

    return pResult->mStrength;
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    ClassifyT lResult;
    int lCnt = 0;
    fragment_classifier_classify_result(pFragmentClassifier,
            pFragment, 
            pLen, 
            &lResult);

    if (lResult.mStrength)
    {
        if (pFragmentClassifier->mNumFileTypes > 0)
        {
            for (lCnt = 0; lCnt < pFragmentClassifier->mNumFileTypes; lCnt++)
            {
                if (pFragmentClassifier->mFileTypes[lCnt].mType == lResult.mType)
                {
                    /* relevant fragment */
                    return 1;
                }
            }
        }
        else
        {
            return 1;
        }
    }

    /* irrelevant fragment */
    return 0;
}

