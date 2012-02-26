#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#include "fragment_classifier.h"

typedef struct 
{
    FragmentClassifier* handle_fc;
    fc_classify_ptr fc_classify;
    fc_new_ptr fc_new;
    fc_free_ptr fc_free;
    int result;
    /* not used at the moment */
    int offset_img;
} thread_data;

void* classify_thread(void* pData);

int main(int argc, char* argv[])
{
    pthread_t lThread1;
    int lThread1Ret;
    thread_data lData;

    if (argc != 3)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size>\n", argv[0]);
        return EXIT_FAILURE;
    }

    lData.handle_fc = fragment_classifier_new("./", atoi(argv[2]));
    if (!lData.handle_fc)
    {
        return EXIT_FAILURE;
    }

    /* start classification process */
    lThread1Ret = pthread_create(&lThread1, NULL, classify_thread, (void*)&lData);

    /* join threads */
    pthread_join(lThread1, NULL);

    /* destruct fragment classifier */
    fragment_classifier_free(lData.handle_fc);

    return EXIT_SUCCESS;
}

void* classify_thread(void* pData)
{
    thread_data* lData = (thread_data*)pData; 

    /* classify fragments */
    lData->result = fragment_classifier_classify(lData->handle_fc, 
            (const unsigned char*)"abc", 3);

    /* do something with the result */

    return NULL;
}

