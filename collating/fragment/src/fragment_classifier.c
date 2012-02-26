#include "fragment_classifier.h"

__declspec(dllexport) FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned int pFragmentSize);

__declspec(dllexport) void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

__declspec(dllexport) int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

