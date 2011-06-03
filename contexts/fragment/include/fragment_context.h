#ifndef __FRAGMENT_CONTEXT_H__
#define __FRAGMENT_CONTEXT_H__ 1

typedef struct _FragmentContext FragmentContext;

FragmentContext* fragment_classify_new(const char* pFilename);
void fragment_classify_free(FragmentContext* pFragmentContext);

int fragment_classify(FragmentContext* pFragmentContext, const uint8_t* pBuf, int pBufLength);

#endif /* __FRAGMENT_CONTEXT_H__ */

