#ifndef __BLOCK_COLLECTION_H__
#define __BLOCK_COLLECTION_H__ 1

#ifndef _MSC_VER
#define __declspec(dllexport) 
#endif

/* returns only if this is a relevant block */
#define BLOCK(x) ((x) & 0x01)
/* returns the offset with header bit set */
#define HEADER(x) ((x) & 0x02)

#define BITS_PER_BLOCK 2
#define BLOCKS_PER_STORAGE (sizeof(unsigned long long) * 8/ BITS_PER_BLOCK)

typedef unsigned long long storage_t;
typedef struct _block_collection_t block_collection_t;

__declspec(dllexport) block_collection_t* block_collection_new(unsigned long long pMaxBlocks, 
        unsigned pBlockSize);
__declspec(dllexport) int block_collection_set(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader);
__declspec(dllexport) int block_collection_set_range(block_collection_t* pCollection, 
        unsigned long long pOffset, int pIsHeader, unsigned pSizeRange);
__declspec(dllexport) unsigned long long block_collection_get(block_collection_t* pCollection, 
        unsigned long long pOffset);
__declspec(dllexport) unsigned long long block_collection_len(block_collection_t* pCollection);
__declspec(dllexport) unsigned block_collection_get_bs(block_collection_t* pCollection);
__declspec(dllexport) void block_collection_free(block_collection_t* pCollection);

#endif /* __BLOCK_COLLECTION_H__ */
