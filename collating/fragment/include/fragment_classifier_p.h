#ifndef __FRAGMENT_CLASSIFIER_P_H__
#define __FRAGMENT_CLASSIFIER_P_H__ 1

/* maximum number of classifiers that can be loaded */
#define MAX_CLASSIFIERS 10

typedef struct 
{
    void* mSoHandler;
    struct _FragmentClassifier* mFcHandler;
    int mWeight;
    fc_new_ptr mFcNew;
    fc_classify_ptr mFcClassify;
    fc_free_ptr mFcFree;
} ClassifyHandler;

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
    unsigned int mNumClassifiers;
    ClassifyHandler mClassifiers[MAX_CLASSIFIERS];
};

#endif /* __FRAGMENT_CLASSIFIER_P_H__ */
