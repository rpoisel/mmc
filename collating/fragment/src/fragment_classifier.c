#include <stdlib.h>

#include "fragment_classifier.h"

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
};

FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned int pFragmentSize)
{
    struct _FragmentClassifier* lHandle = (struct _FragmentClassifier*) malloc(sizeof(struct _FragmentClassifier));

    /* load shared libraries */

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    /* free loaded shared libraries */

    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    /* invoke loaded classifiers */

    /* weight results */

    return -1;
}

