#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>

#include "fragment_classifier.h"

#define NUM_OPTIONS 0

typedef struct 
{
    FragmentClassifier* handle_fc;
    int result;
    const char* path_image;
    int frag_size;
    /* not used at the moment */
    int offset_img;
} thread_data;

void* classify_thread(void* pData);

int main(int argc, char* argv[])
{
    pthread_t lThread1;
    thread_data lData;
    ClassifyOptions lOptions[NUM_OPTIONS];

    if (argc != 3)
    {
        fprintf(stderr, "Wrong number of command-line arguments.\n");
        fprintf(stderr, "Invocation: %s <path-to-image> <block-size>\n", argv[0]);
        return EXIT_FAILURE;
    }

    lData.path_image = argv[1];
    lData.frag_size = atoi(argv[2]);
    lData.handle_fc = fragment_classifier_new(lOptions, NUM_OPTIONS, lData.frag_size);
    if (!lData.handle_fc)
    {
        return EXIT_FAILURE;
    }

    /* start classification process */
    /* TODO check return value */
    pthread_create(&lThread1, NULL, classify_thread, (void*)&lData);

    /* join threads */
    pthread_join(lThread1, NULL);

    /* destruct fragment classifier */
    fragment_classifier_free(lData.handle_fc);

    return EXIT_SUCCESS;
}

void* classify_thread(void* pData)
{
    thread_data* lData = (thread_data*)pData; 
    FILE* lImage = NULL;
    unsigned char* lBuf = NULL;
    int lResult = lData->frag_size;

    lBuf = (unsigned char*)malloc(lData->frag_size);
    lImage = fopen(lData->path_image, "r");

    /* classify fragments */
    while (lResult == lData->frag_size)
    {
        lResult = fread(lBuf, 1, lData->frag_size, lImage);
        lData->result = fragment_classifier_classify(lData->handle_fc, 
                lBuf, lResult);
        /* do something with the result */
        printf("Result: %d\n", lData->result);
    }


    fclose(lImage);
    free(lBuf);

    return NULL;
}

