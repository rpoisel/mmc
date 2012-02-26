#ifndef __FRAGMENT_CLASSIFIER_PY_H__
#define __FRAGMENT_CLASSIFIER_PY_H__ 1

#include "fragment_classifier.h"

/* this is just a facade */
__declspec(dllexport) FragmentClassifier* fragment_classifier_py(const char* pFragsRefDir,
        unsigned int pFragmentSize);

#endif /* __FRAGMENT_CLASSIFIER_PY_H__ */
