#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include <tsk3/libtsk.h>

#define IMAGE_IN "../../data/usbkey.dd"
#define IMAGE_OUT "/tmp/out.dd"

#define DEBUG 0

static TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pData);

static TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void *a_ptr);

static void data_act(
        char* pBuf,
        const unsigned pLen,
        const unsigned long long pOffset,
        void* pData
        );

int main(int argc, char* argv[])
{
    char* lImages[] = { argv[1] };
    TSK_VS_INFO* lVsInfo = NULL;
    FILE* lOut = fopen(IMAGE_OUT, "wb");
    unsigned long long lCnt = 0;
    char lBuf[32768] = { 0 };
    unsigned lCntRead = 0;

    TSK_IMG_INFO* lImgInfo = tsk_img_open(
            1, /* number of images */
            (const TSK_TCHAR * const*)lImages, /* path to images */
            TSK_IMG_TYPE_DETECT, /* disk image type */
            0); /* size of device sector in bytes */
    if (lImgInfo != NULL)
    {
        TSK_OFF_T lSizeSectors = lImgInfo->size / lImgInfo->sector_size + \
                                 (lImgInfo->size % lImgInfo->sector_size ? 1 : 0);
#if DEBUG == 1
        fprintf(stdout, "Image size (Bytes): %lu, Image size (sectors): %lu\n",
                lImgInfo->size,
                lSizeSectors);
#endif
        lVsInfo = tsk_vs_open(lImgInfo, 0, TSK_VS_TYPE_DETECT);
        if (lVsInfo != NULL)
        {
            if (tsk_vs_part_walk(lVsInfo,
                    0, /* start */
                    lVsInfo->part_count - 1, /* end */
                    0, /* all partitions */
                    part_act, /* callback */
                    (void*) lOut /* data passed to the callback */
                    ) != 0)
            {
                fprintf(stderr, "Problem when walking partitions. \n");
            }
        }
        else
        {
#if DEBUG == 1
            fprintf(stderr, "Volume system cannot be opened.\n");
#endif
            for (lCnt = 0; lCnt < lSizeSectors; lCnt++)
            {
                lCntRead = lCnt == lSizeSectors - 1 ? 
                                lImgInfo->size % lImgInfo->sector_size :
                                lImgInfo->sector_size;
#if DEBUG == 1
                fprintf(stderr, "Reading %u bytes\n", 
                        lCntRead
                       );
#endif
                tsk_img_read(
                        lImgInfo, /* handler */
                        lCnt * lImgInfo->sector_size, /* start address */
                        lBuf, /* buffer to store data in */
                        lCntRead /* amount of data to read */
                        );
                data_act(lBuf, lCntRead, lCnt * lImgInfo->sector_size, lOut);
            }
        }
    }
    else
    {
        fprintf(stderr, "Problem opening the image. \n");
    }
    fclose(lOut);

    return EXIT_SUCCESS;
}

TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pData)
{
    TSK_FS_INFO* lFsInfo = NULL;
    FILE* lOut = (FILE *)pData;
    unsigned long long lCnt = 0;
    char lBuf[32768] = { 0 };
    unsigned long long lOffsetBlock = 0;

    /* open file system */
    if ((lFsInfo = tsk_fs_open_vol(
            pPartInfo, /* partition to open */
            TSK_FS_TYPE_DETECT /* auto-detect mode on */
            )) != NULL)
    {
        /* known file-system */

        /* iterate over unallocated blocks of fs */
        tsk_fs_block_walk(
                lFsInfo, /* file-system info */
                0, /* start */
                lFsInfo->block_count - 1, /* end */
                TSK_FS_BLOCK_WALK_FLAG_UNALLOC, /* only unallocated blocks */
                block_act, /* callback */
                pData /* file-handle */
                );
        /* close fs */
        tsk_fs_close(lFsInfo);
    }
    else
    {
        /* unknown file-system */

        /* iterate through all blocks of this volume regardless of their state */
        for (lCnt = 0; lCnt < pPartInfo->len; lCnt++)
        {
            lOffsetBlock = (pPartInfo->start + lCnt) * pPartInfo->vs->block_size;
#if DEBUG == 1
            fprintf(stdout,
                    "Block in unknown partition (Len: %lu blocks). " 
                    "Size: %u, Absolute address (Bytes): %lld\n",
                    pPartInfo->len,
                    pPartInfo->vs->block_size,
                    lOffsetBlock);
#endif
            /* use the following function so that forensic images are supported */
            /* HINT: this is not the case with fopen/fseek/fread/fclose functions */
            tsk_vs_part_read_block(
                    pPartInfo,
                    lCnt, /* start address (blocks) relative to start of volume */
                    lBuf, /* buffer to store data in */
                    pPartInfo->vs->block_size /* amount of data to read */
                    );
            data_act(lBuf,
                    pPartInfo->vs->block_size, 
                    lOffsetBlock,
                    lOut);
        }
    }

    return TSK_WALK_CONT;
}

TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void* a_ptr)
{
    FILE* lOut = (FILE* )a_ptr;
#if DEBUG == 1
    fprintf(stdout,
            "FS-Offset (Bytes): %lu, Size: %u, "
            "Block: %lu, Absolute address: %ld\n",
            a_block->fs_info->offset,
            a_block->fs_info->block_size,
            a_block->addr, 
            a_block->fs_info->offset + a_block->addr * a_block->fs_info->block_size);
#endif
    data_act(
            a_block->buf, /* block data */
            a_block->fs_info->block_size, /* size in bytes */
            a_block->fs_info->offset + a_block->addr * a_block->fs_info->block_size,
            lOut); /* file-handle */
    return TSK_WALK_CONT;
}

static void data_act(
        char* pBuf,
        const unsigned pLen,
        const unsigned long long pOffset,
        void* pData
        )
{
    FILE* lOut = (FILE*)pData;
    fseek(lOut, pOffset, SEEK_SET);
    fwrite(pBuf, pLen, 1, lOut);
}
