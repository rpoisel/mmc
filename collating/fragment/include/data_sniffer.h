#ifndef __DATA_SNIFFER_H__
#define __DATA_SNIFFER_H__ 1

#include "fragment_classifier.h"

typedef struct 
{
    FragmentClassifier* handle_fc;
    fc_classify_ptr fc_classify;
    fc_new_ptr fc_new;
    fc_free_ptr fc_free;
} thread_data;

#endif /* __DATA_SNIFFER_H__ */
