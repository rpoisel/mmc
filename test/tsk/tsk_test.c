#include <stdlib.h>
#include <stdio.h>

#include <tsk3/libtsk.h>

static TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pData);

static TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void *a_ptr);

int main(int argc, char* argv[])
{
    char* lImages[] = { "../../data/usbkey.dd" };
    TSK_VS_INFO* lVsInfo = NULL;
    FILE* lOut = fopen("/tmp/out.dd", "wb");
    TSK_IMG_INFO* lImgInfo = tsk_img_open(
            1, /* number of images */
            (const TSK_TCHAR * const*)lImages, /* path to images */
            TSK_IMG_TYPE_DETECT, /* disk image type */
            0); /* size of device sector in bytes */
    if (lImgInfo != NULL)
    {
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

    /* open file system */
    if ((lFsInfo = tsk_fs_open_vol(
            pPartInfo, /* partition to open */
            TSK_FS_TYPE_DETECT /* auto-detect mode on */
            )) != NULL)
    {
        /* known file-system */

#if 0
        fprintf(
                stdout,
                "Block Size: %u\n",
                lFsInfo->block_size
                );
#endif
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
#if 0
        fprintf(stdout, "Start: %llu, Block Size: %u, Len: %llu\n",
                pPartInfo->start,
                pPartInfo->vs->block_size,
                pPartInfo->len);
#endif
        for (lCnt = 0; lCnt < pPartInfo->len; lCnt++)
        {
            /* use the following function so that forensic images are supported */
            /* HINT: this is not the case with fopen/fseek/fread/fclose functions */
            tsk_vs_part_read_block(
                    pPartInfo,
                    pPartInfo->start + lCnt * pPartInfo->vs->block_size, /* start address */
                    lBuf, /* buffer to store data in */
                    pPartInfo->vs->block_size /* amount of data to read */
                    );
            fwrite(lBuf, pPartInfo->vs->block_size, 1, lOut);
        }
    }

    return TSK_WALK_CONT;
}

TSK_WALK_RET_ENUM block_act(
        const TSK_FS_BLOCK *a_block,
        void* a_ptr)
{
    FILE* lOut = (FILE* )a_ptr;
    fwrite(
            a_block->buf, /* block data */
            a_block->fs_info->block_size, /* size in bytes */
            1, /* number of blocks */
            lOut); /* file-handle */
    return TSK_WALK_CONT;
}
