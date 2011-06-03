#ifndef __FRAGMENT_CLASSIFIER_H__
#define __FRAGMENT_CLASSIFIER_H__ 1

typedef struct _FragmentClassifier FragmentClassifier;

/* FragmentClassifier* fragment_classifier_new(const char* pFilename); */
extern FragmentClassifier* fragment_classifier_new(void);
extern void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

/*
int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const uint8_t* pBuf, int pBufLength);
*/
extern int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        int pBufLength);

#endif /* __FRAGMENT_CLASSIFIER_H__ */

