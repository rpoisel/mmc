#ifndef __DATA_SNIFFER_H__
#define __DATA_SNIFFER_H__ 1

#include "fragment_classifier.h"

struct ThreadData
{
    FragmentClassifier* mHandleFC;
    fc_classify_ptr mFcClassify;
};

#endif /* __DATA_SNIFFER_H__ */
