#ifndef __FRAGMENT_CLASSIFIER_H__
#define __FRAGMENT_CLASSIFIER_H__ 1

typedef struct _FragmentClassifier FragmentClassifier;

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

__declspec(dllexport) FragmentClassifier* fragment_classifier_new(const char* pFilename, 
        unsigned int pFragmentSize);

__declspec(dllexport) void fragment_classifier_free(FragmentClassifier* pFragmentClassifier);

__declspec(dllexport) int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

typedef FragmentClassifier* (*fc_new_ptr)(const char* pFilename, 
        unsigned int pFragmentSize);
typedef void (*fc_free_ptr)(FragmentClassifier* pFragmentClassifier);
typedef int (*fc_classify_ptr)(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen);

#endif /* __FRAGMENT_CLASSIFIER_H__ */
