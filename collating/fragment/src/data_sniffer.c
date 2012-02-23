#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

#include "data_sniffer.h"
#include "fragment_classifier.h"

int main(int argc, char* argv[])
{
    void* lHandleSO = NULL;
    FragmentClassifier* lHandleFC = NULL;
    fc_new_ptr fc_new;
    fc_classify_ptr fc_classify;
    fc_free_ptr fc_free;
    int lResult;

    if (argc != 3)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size>\n", argv[0]);
        return -1;
    }

    /* open shared object and extract functions */
    lHandleSO = dlopen("./libfragment_classifier.so", RTLD_LAZY);
    if (!lHandleSO)
    {
        fprintf(stderr, "Could not load shared object: %s\n", dlerror());
        return -2;
    }
    fc_new = dlsym(lHandleSO, "fragment_classifier_new");
    fc_classify = dlsym(lHandleSO, "fragment_classifier_classify");
    fc_free = dlsym(lHandleSO, "fragment_classifier_free");

    /* initialize fragment classifier */
    lHandleFC = (*fc_new)("/tmp", atoi(argv[2]));

    /* classify fragments */
    lResult = (*fc_classify)(lHandleFC, (const unsigned char*)"abc", 3);

    /* destruct fragment classifier */
    (*fc_free)(lHandleFC);

    /* close shared object */
    dlclose(lHandleSO);

    return lResult;
}
