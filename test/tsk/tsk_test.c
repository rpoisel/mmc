#include <stdlib.h>

#include <tsk3/libtsk.h>

static TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pData);

int main(int argc, char* argv[])
{
    char* lImages[] = { "../../data/usbkey.dd" };
    TSK_VS_INFO* lVsInfo = NULL;
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
            tsk_vs_part_walk(lVsInfo,
                    0, /* start */
                    lVsInfo->part_count - 1, /* end */
                    0, /* all partitions */
                    part_act, /* callback */
                    NULL /* data passed to the callback */
                    );
        }
    }
    else
    {
        fprintf(stderr, "Problem opening the image. \n");
    }
    return EXIT_SUCCESS;
}

TSK_WALK_RET_ENUM part_act(
        TSK_VS_INFO* pVsInfo,
        const TSK_VS_PART_INFO* pPartInfo,
        void* pData)
{
    printf("Partition!\n");
    return TSK_WALK_CONT;
}
