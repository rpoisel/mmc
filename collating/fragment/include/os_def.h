#ifndef __OS_DEF_H__
#define __OS_DEF_H__ 1

#if defined __linux__

/* includes */
#include <pthread.h>

/* data types */
#define OS_FH_TYPE FILE*
#define OS_THREAD_TYPE pthread_t

/* functions */
#define OS_FOPEN_READ(pPath)                            \
    fopen(pPath, "r")

#define OS_FOPEN_WRITE(pPath)                           \
    fopen(pPath, "w")

#define OS_FCLOSE(pHandle)                              \
    fclose(pHandle)

#define OS_FREAD(pBuf, pLen, pNumRead, pHandle)         \
    pNumRead = fread(pBuf, 1, pLen, pHandle)

/* TODO check return type */
#define OS_WRITE(pBuf, pLen, pNumWrite, pHandle)        \
    pNumWrite = fwrite(pBuf, 1, pLen, pHandle)

#define OS_FSEEK_SET(pHandle, pOffset)                  \
    fseek(pHandle, pOffset, SEEK_SET)

#define OS_SNPRINTF snprintf

#define OS_THREAD_CREATE(pHandle, pData, pFunc)         \
        pthread_create(pHandle, NULL,                   \
                pFunc, (void*)(pData))

#define OS_THREAD_JOIN(pHandle)                         \
    pthread_join(pHandle, NULL);

/* user-defined functions */
#define THREAD_FUNC(pFuncName, pData)                   \
    void* pFuncName(void* pData)

/* values */
#define OS_FH_INVALID NULL
#define OS_THREAD_RETURN NULL

#elif defined _WIN32 || defined _WIN64

/* includes */
#include <Windows.h>
#include <sys/types.h>
#include <sys/timeb.h>
#include <string.h>

/* data types */
#define OS_FH_TYPE HANDLE
#define OS_THREAD_TYPE HANDLE

/* functions */
#define OS_FOPEN_READ(pPath)                            \
    CreateFile(pPath,                                   \
        GENERIC_READ,                                   \
        FILE_SHARE_READ,                                \
        NULL,                                           \
        OPEN_EXISTING,                                  \
        0,                                              \
        NULL)

#define OS_FOPEN_WRITE(pPath)                           \
    CreateFile(pPath,                                   \
        GENERIC_WRITE,                                  \
        FILE_SHARE_READ,                                \
        NULL,                                           \
        OPEN_EXISTING,                                  \
        0,                                              \
        NULL)

#define OS_FCLOSE(pHandle)                              \
    CloseHandle(pHandle)

#define OS_FREAD(pBuf, pLen, pNumRead, pHandle)         \
    ReadFile(pHandle, pBuf, pLen, &pNumRead, NULL)

/* TODO check return type */
#define OS_WRITE(pBuf, pLen, pNumWrite, pHandle)        \
    WriteFile(pHandle, pBuf, pLen, &pNumWrite, NULL)

#define OS_SNPRINTF _snprintf

#define OS_FSEEK_SET(pHandle, pOffset)                  \
    /* danger on 64-bit systems for third parameter */  \
    SetFilePointer(pHandle, pOffset, 0, FILE_BEGIN)

#define OS_THREAD_JOIN(pHandle)                         \
    WaitForSingleObject(pHandle,INFINITE);

#define OS_THREAD_CREATE(pHandle, pData, pFunc)         \
    *(pHandle) = CreateThread(NULL, 0,                  \
            pFunc, (void*)(pData),                      \
            0, NULL);

/* user-defined functions */
#define THREAD_FUNC(pFuncName, pData)                   \
    DWORD pFuncName(LPVOID pData)

/* values */
#define OS_FH_INVALID INVALID_HANDLE_VALUE
#define OS_THREAD_RETURN 0

#else
#error "Unsupported platform"
#endif

#endif
