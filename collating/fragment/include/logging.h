#ifndef __LOGGING_H__
#define __LOGGING_H__ 1

#include <stdio.h>
#include <time.h>

#define LOG_NONE     0
#define LOG_ERROR    1
#define LOG_WARN     2
#define LOG_INFO     3
#define LOG_DEBUG    4

/* set the global logging level here */
#define LOG_LEVEL LOG_INFO

void print_timestamp(void);

#if LOG_LEVEL == LOG_DEBUG
#define _LOG_PREAMBLE                                       \
        fprintf(stdout, "%s:%d ", __FILE__, __LINE__);
#else
#define _LOG_PREAMBLE                                       \
        print_timestamp();
#endif

#if LOG_LEVEL >= LOG_ERROR
#define LOGGING_ERROR(...)                                  \
    {                                                       \
        _LOG_PREAMBLE                                       \
        fprintf(stdout, "ERROR ");                          \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }
#else
#define LOGGING_ERROR(...)
#endif

#if LOG_LEVEL >= LOG_WARN
#define LOGGING_WARN(...)                                   \
    {                                                       \
        _LOG_PREAMBLE                                       \
        fprintf(stdout, "WARN ");                           \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }
#else
#define LOGGING_WARN(...)
#endif

#if LOG_LEVEL >= LOG_INFO
#define LOGGING_INFO(...)                                   \
    {                                                       \
        _LOG_PREAMBLE                                       \
        fprintf(stdout, "INFO ");                           \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }
#else
#define LOGGING_INFO(...)
#endif

#if LOG_LEVEL >= LOG_DEBUG
#define LOGGING_DEBUG(...)                                  \
    {                                                       \
        _LOG_PREAMBLE                                       \
        fprintf(stdout, "DEBUG ");                          \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }
#else
#define LOGGING_DEBUG(...)
#endif

#endif /* __LOGGING_H__ */
