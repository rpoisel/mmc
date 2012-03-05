#include <stdlib.h>

#include "fragment_classifier.h"
#include "entropy/entropy.h"

/* turn to 1 for verbose messages */
#define VERBOSE 0
/* set to 0 to turn off ncd testing */

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
};

FragmentClassifier* fragment_classifier_new(ClassifyOptions* pOptions, 
        unsigned int pNumSo, 
        unsigned int pFragmentSize)
{
    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;

    /* initialize fields that are not used regularely with
     * illegal values */

    return lHandle;
}

FragmentClassifier* fragment_classifier_new_ct(ClassifyOptions* pOptions, 
        unsigned int pNumSo, 
        unsigned int pFragmentSize,
        ClassifyT* pTypes,
        unsigned int pNumTypes)
{
    struct _FragmentClassifier* lHandle = fragment_classifier_new(
            pOptions,
            pNumSo,
            pFragmentSize);

    /* initialize additional fields */

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    /* free handle resources */
    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    float lReturn = 0;

    if (pLen == 0)
    {
        return 0;
    }

    lReturn = calc_entropy(pFragment, pLen);
    /* empiric value ;-) */
    if (lReturn > 0.625)
    {
        return 1;
    }

    /* non-relevant fragment <= 0 > relevant fragment */
    return 0;
}

