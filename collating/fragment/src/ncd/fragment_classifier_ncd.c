#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <time.h>
#include <math.h>

#ifdef _MSC_VER
#include "inttypes.h"
#include "dirent_ms.h"
#define INFINITY 0xFFFFFFFF
void initlibfragment_classifier(void) {};
#else
#include <stdint.h>
#include <dirent.h>
#endif

#include "fragment_classifier.h"

/* turn to 1 for verbose messages */
#define VERBOSE 0
/* set to 0 to turn off ncd testing */

#define STRLEN_PATH 1024

#include "ncd.h"
#define MAX_NUM_FILE_TYPES 16
#define NUM_FRAGS_PER_FILE_TYPE 5
/* #define FRAGS_REF_DIR "./data/frags_ref" */
#define MAX_DIR_ENT 256

struct _FragmentClassifier
{
    unsigned int mFragmentSize;
    unsigned char* mReferenceFrags[MAX_NUM_FILE_TYPES][NUM_FRAGS_PER_FILE_TYPE];
};

static const char *sTypes[] = { ".html", ".txt", ".svg", ".h264", "" };
struct SNearest
{
    int mIdxTypeNearest;
    double mValNearest;
};

static int check_ncd(FragmentClassifier* pFragmentClassifier, 
    const unsigned char* pFragment,
    int pLen);
int readRandFrag(unsigned char*, int, const char*, const char*);

FragmentClassifier* fragment_classifier_new(const char* pRefDir, 
        unsigned int pFragmentSize)
{
    int lCntX = 0, lCntY = 0;

    /* initialize handle structure */
    struct _FragmentClassifier* lHandle = 
        (struct _FragmentClassifier*)malloc(sizeof(struct _FragmentClassifier));

    lHandle->mFragmentSize = pFragmentSize;

#ifdef _MSC_VER
    srand((unsigned)time(NULL));
#else
    srandom(time(NULL));
#endif
    for (lCntX = 0; lCntX < MAX_NUM_FILE_TYPES && strlen(sTypes[lCntX]) > 0 ; lCntX++)
    {
        for (lCntY = 0; lCntY < NUM_FRAGS_PER_FILE_TYPE; lCntY++)
        {
            lHandle->mReferenceFrags[lCntX][lCntY] = 
                (unsigned char*)malloc(sizeof(unsigned char) * pFragmentSize);
            /* randomly open file, random seek, read reference fragment */
            readRandFrag(lHandle->mReferenceFrags[lCntX][lCntY], pFragmentSize, pRefDir, sTypes[lCntX]); 
        }
    }

    return lHandle;
}

void fragment_classifier_free(FragmentClassifier* pFragmentClassifier)
{
    int lCntX = 0, lCntY = 0;

    /* free resources from the structure */
    for (lCntX = 0; lCntX < MAX_NUM_FILE_TYPES && strlen(sTypes[lCntX]) > 0; lCntX++)
    {
        for (lCntY = 0; lCntY < NUM_FRAGS_PER_FILE_TYPE; lCntY++)
        {
            free(pFragmentClassifier->mReferenceFrags[lCntX][lCntY]);
        }
    }
    free(pFragmentClassifier);
}

int fragment_classifier_classify(FragmentClassifier* pFragmentClassifier, 
        const unsigned char* pFragment,
        int pLen)
{
    int lReturn = 0;

    lReturn = check_ncd(pFragmentClassifier, pFragment, pLen);
    if (lReturn < 0)
    {
        /* non-relevant fragment */
        return lReturn;
    }

    /* relevant fragment */
    return lReturn;
}

static int check_ncd(FragmentClassifier* pFragmentClassifier, 
    const unsigned char* pFragment,
    int pLen)
{
    /* FileType counter */
    int lCntFT = 0;
    int lCntFrag = 0;
    struct SNearest lNearest = { -1, INFINITY };
    double lNCDResult = INFINITY;

    for (lCntFT = 0; lCntFT < MAX_NUM_FILE_TYPES && strlen(sTypes[lCntFT]) > 0; lCntFT++)
    {
        /* determine first nearest neighbor */
        for (lCntFrag = 0; lCntFrag < NUM_FRAGS_PER_FILE_TYPE; lCntFrag++)
        {
            lNCDResult = ncd(pFragment, 
                    pFragmentClassifier->mReferenceFrags[lCntFT][lCntFrag], 
                    pLen);

            if (lNCDResult < lNearest.mValNearest)
            {
                lNearest.mIdxTypeNearest = lCntFT;
                lNearest.mValNearest = lNCDResult;
            }
        }
    }
    /* TODO 
     * determine biggest distance if filetype is correct
     * determine nearest distance if filetype is incorrect
     */
#if VERBOSE == 1
    fprintf(stdout, "NCD Nearest Neighbor %f | Type: %s\n",
            lNearest.mValNearest, 
            sTypes[lNearest.mIdxTypeNearest]);
#endif

    if (lNearest.mIdxTypeNearest < 3)
    {
        /* text-based fragment */
        return -1;
    }

    /* keep on processing this fragment */
    return 1;
}

int readRandFrag(unsigned char* pBuf, int pFragmentSize, 
        const char* pDir, const char* pFileExt)
{
    DIR* lDH = NULL;
    FILE* lRandomFH = NULL;
    struct dirent* lCurDir = NULL;
    struct dirent lDirEnts[MAX_DIR_ENT];
    int lCnt = 0;
    struct stat lInfo;
    char lFullPath[STRLEN_PATH];
    long lFileSize = 0;
    long lNumFrags = 0;
    long int lRandIdx = 0;

    lDH = opendir(pDir);
    if (lDH == NULL)
    {
        closedir(lDH);
        return -1;
    }

    for(; lCnt < MAX_DIR_ENT;)
    {
        lCurDir = readdir(lDH);
        if (lCurDir == NULL)
        {
            break;
        }
        else
        {
            strcpy(lFullPath, pDir);
#ifdef _MSC_VER
            strcat(lFullPath, "\\");
#else
            strcat(lFullPath, "/");
#endif
            strcat(lFullPath, lCurDir->d_name);

            if (stat(lFullPath, &lInfo) == -1)
            {
                fprintf(stderr, "stat() error.\n");
            }

            if (S_ISREG(lInfo.st_mode))
            {
                /* check file extension */
                if (strstr((lFullPath + strlen(lFullPath) - strlen(pFileExt) - 1), 
                            pFileExt) != NULL)
                {
                    lDirEnts[lCnt] = *lCurDir;
                    lCnt++;
                }
            }
        }
    }

    if (lCnt > 0)
    {
#ifdef _MSC_VER
        lRandIdx = rand() % lCnt;
#else
        lRandIdx = random() % lCnt;
#endif

        strcpy(lFullPath, pDir);
#ifdef _MSC_VER
        strcat(lFullPath, "\\");
#else
        strcat(lFullPath, "/");
#endif
        strcat(lFullPath, lDirEnts[lRandIdx].d_name);
        lRandomFH = fopen(lFullPath, "rb");

        fseek(lRandomFH, 0, SEEK_END);
        lFileSize = ftell(lRandomFH);
        lNumFrags = lFileSize / pFragmentSize;
        if (lFileSize % pFragmentSize != 0)
        {
            lNumFrags++;
        }
#ifdef _MSC_VER
        fseek(lRandomFH, (rand() % (lNumFrags - 2) + 1) * pFragmentSize, SEEK_SET);
#else
        fseek(lRandomFH, (random() % (lNumFrags - 2) + 1) * pFragmentSize, SEEK_SET);
#endif
        fread(pBuf, 1, pFragmentSize, lRandomFH);
        
        fclose(lRandomFH);
    }

    return (lCnt > 0 ? 1 : 0);
}

