#ifndef __BLOCK_COLLECTION_H__
#define __BLOCK_COLLECTION_H__ 1

/* returns only the offset portion */
#define BLOCK(x) ((x) & 0x01)
/* returns the offset with header bit set */
#define HEADER(x) ((x) & 0x02)

#define BITS_PER_BLOCK 2
#define BLOCKS_PER_STORAGE (sizeof(unsigned long) * 8/ BITS_PER_BLOCK)

typedef struct _block_collection_t block_collection_t;

block_collection_t* block_collection_new(unsigned long long pMaxBlocks, 
        unsigned pBlockSize);
int block_collection_set(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader);
unsigned long long block_collection_get(block_collection_t* pCollection, 
        unsigned long long pOffset);
unsigned long long block_collection_len(block_collection_t* pCollection);
unsigned block_collection_get_bs(block_collection_t* pCollection);
void block_collection_free(block_collection_t* pCollection);

#endif /* __BLOCK_COLLECTION_H__ */
