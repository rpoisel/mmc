#ifndef __BLOCK_COLLECTION_H__
#define __BLOCK_COLLECTION_H__ 1

typedef struct
{
    unsigned long long* mBlockArray;
    unsigned long long mMaxBlocks;
    unsigned long long mNumBlocks;
} block_array;

block_array* block_array_new(unsigned long long pMaxBlocks);
int block_array_add(block_array* pArray, unsigned long long pOffset, int pIsHeader);
int block_array_sort(block_array* pArray);
unsigned long long block_array_get(block_array* pArray, unsigned long long pIndex);
int block_array_free(block_array* pArray);

#endif /* __BLOCK_COLLECTION_H__ */
