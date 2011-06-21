#ifndef __FRAGMENT_CLASSIFIER_H__
#define __FRAGMENT_CLASSIFIER_H__ 1

typedef struct _FragmentClassifier FragmentClassifier;

FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned int pFragmentSize);
void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

#endif /* __FRAGMENT_CLASSIFIER_H__ */

