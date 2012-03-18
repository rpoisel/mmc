#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define BITMASK_HEADER ((unsigned long long)0x01 << ((sizeof(unsigned long long) * 8) - 1))

struct struct_handle
{
    void* mData; 
};

int main(void)
{
    unsigned long long lOffset = 1439;
    printf("0x%llX\n", ULLONG_MAX);
    lOffset |= BITMASK_HEADER;
    printf("0x%llX\n", lOffset & (~BITMASK_HEADER));
    struct struct_handle lHandle;
    lHandle.mData = malloc(1000000000L * sizeof(char));
    if (lHandle.mData == NULL)
    {
        perror("Could not allocate memory: ");
        return EXIT_FAILURE;
    }

    free(lHandle.mData);

    return EXIT_SUCCESS;
}
