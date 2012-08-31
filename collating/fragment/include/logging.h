#ifndef __LOGGING_H__
#define __LOGGING_H__ 1

#include <time.h>

enum LogLevel
{
    LOG_EMERG  = 0,
    LOG_ALERT  = 1,
    LOG_CRIT   = 2,
    LOG_ERROR  = 3,
    LOG_WARN   = 4,
    LOG_NOTICE = 5,
    LOG_INFO   = 6, 
    LOG_DEBUG  = 7,
    LOG_NONE   = 8,
};

/* set the global logging level here */
#define LOG_LEVEL LOG_INFO

void print_timestamp(void);
void print_loglevel(enum LogLevel);

#define LOGGING(pLogLevel, ...)                             \
    if (pLogLevel <= LOG_LEVEL)                             \
    {                                                       \
        if (pLogLevel == LOG_DEBUG)                         \
        {                                                   \
            fprintf(stdout, "%s:%d ", __FILE__, __LINE__);  \
        }                                                   \
        else                                                \
        {                                                   \
            print_timestamp();                              \
        }                                                   \
        print_loglevel(pLogLevel);                          \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }

#endif /* __LOGGING_H__ */
