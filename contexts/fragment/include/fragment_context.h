#ifndef __FRAGMENT_CONTEXT_H__
#define __FRAGMENT_CONTEXT_H__ 1

typedef struct _FragmentContext FragmentContext;

/* FragmentContext* fragment_classifier_new(const char* pFilename); */
FragmentContext* fragment_classifier_new();
void fragment_classifier_free(FragmentContext* pFragmentContext);

/*
int fragment_classifier_classify(FragmentContext* pFragmentContext, 
        const uint8_t* pBuf, int pBufLength);
*/
int fragment_classifier_classify(FragmentContext* pFragmentContext, 
        int pBufLength);

#endif /* __FRAGMENT_CONTEXT_H__ */

