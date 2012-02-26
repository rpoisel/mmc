#include <stdlib.h>

#include "fragment_classifier.h"

/* turn to 1 for verbose messages */
#define VERBOSE 0
/* set to 0 to turn off ncd testing */

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
};

FragmentClassifier* fragment_classifier_new(const char* pRefDir, 
        unsigned int pFragmentSize)
{
    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;

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
    int lReturn = 0;

    /* non-relevant fragment <= 0 > relevant fragment */
    return lReturn;
}

