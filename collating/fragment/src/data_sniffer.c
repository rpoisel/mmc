#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>

#include "data_sniffer.h"

void* classify_thread(void* pData);

int main(int argc, char* argv[])
{
    void* lHandleSO = NULL;
    int lResult = 0;
    pthread_t lThread1;
    int lThread1Ret;
    thread_data lData;

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
    lData.fc_new = dlsym(lHandleSO, "fragment_classifier_new");
    lData.fc_classify = dlsym(lHandleSO, "fragment_classifier_classify");
    lData.fc_free = dlsym(lHandleSO, "fragment_classifier_free");

    /* initialize fragment classifier */
    lData.handle_fc = (*lData.fc_new)("/tmp", atoi(argv[2]));

    /* start classification process */
    lThread1Ret = pthread_create(&lThread1, NULL, classify_thread, (void*)&lData);

    /* join threads */
    pthread_join(lThread1, NULL);

    /* destruct fragment classifier */
    (*lData.fc_free)(lData.handle_fc);

    /* close shared object */
    dlclose(lHandleSO);

    return lResult;
}

void* classify_thread(void* pData)
{
    int lResult = 0;
    /* classify fragments */
    /* lResult = (*fc_classify)(lHandleFC, (const unsigned char*)"abc", 3); */
    lResult = (*((thread_data*)pData)->fc_classify)(((thread_data*)pData)->handle_fc, (const unsigned char*)"abc", 3);

    return NULL;
}

