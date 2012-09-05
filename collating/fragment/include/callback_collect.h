#ifndef __CALLBACK_COLLECT_H__
#define __CALLBACK_COLLECT_H__ 1

#include "block_classifier.h"

int classify_collect(void* pData, unsigned long long pOffset, 
        FileType pType, int pStrength, int pIsHeader, char* pInfo);


#endif /* __CALLBACK_COLLECT_H__ */
