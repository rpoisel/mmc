#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

#include "data_sniffer.h"

void* classify_thread(void* pData);

int main(int argc, char* argv[])
{
    void* lHandleSO = NULL;
    fc_new_ptr fc_new;
    fc_free_ptr fc_free;
    int lResult = 0;
    pthread_t lThread1;
    int lThread1Ret;
    struct ThreadData lData;

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
    lData.mFcClassify = dlsym(lHandleSO, "fragment_classifier_classify");
    fc_free = dlsym(lHandleSO, "fragment_classifier_free");

    /* initialize fragment classifier */
    lData.mHandleFC = (*fc_new)("/tmp", atoi(argv[2]));

    /* start classification process */
    lThread1Ret = pthread_create(&lThread1, NULL, classify_thread, (void*)&lData);

    /* join threads */
    pthread_join(lThread1, NULL);

    /* destruct fragment classifier */
    (*fc_free)(lData.mHandleFC);

    /* close shared object */
    dlclose(lHandleSO);

    return lResult;
}

void* classify_thread(void* pData)
{
    int lResult = 0;
    /* classify fragments */
    /* lResult = (*fc_classify)(lHandleFC, (const unsigned char*)"abc", 3); */
    lResult = (*((struct ThreadData*)pData)->mFcClassify)(((struct ThreadData*)pData)->mHandleFC, (const unsigned char*)"abc", 3);

    return NULL;
}

