#ifndef __LOGGING_H__
#define __LOGGING_H__ 1

#include <time.h>

#define LOG_EMERG    0
#define LOG_ALERT    1
#define LOG_CRIT     2
#define LOG_ERROR    3
#define LOG_WARN     4
#define LOG_NOTICE   5
#define LOG_INFO     6
#define LOG_DEBUG    7
#define LOG_NONE     8

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

#if LOG_LEVEL == LOG_EMERG
#define _LOG_LEVEL fprintf(stdout, "EMERG ");
#elif LOG_LEVEL == LOG_ALERT
#define _LOG_LEVEL fprintf(stdout, "ALERT ");
#elif LOG_LEVEL == LOG_CRIT
#define _LOG_LEVEL fprintf(stdout, "CRIT ");
#elif LOG_LEVEL == LOG_ERROR
#define _LOG_LEVEL fprintf(stdout, "ERROR ");
#elif LOG_LEVEL == LOG_WARN
#define _LOG_LEVEL fprintf(stdout, "WARN ");
#elif LOG_LEVEL == LOG_NOTICE
#define _LOG_LEVEL fprintf(stdout, "NOTICE ");
#elif LOG_LEVEL == LOG_INFO
#define _LOG_LEVEL fprintf(stdout, "INFO ");
#elif LOG_LEVEL == LOG_INFO
#define _LOG_LEVEL fprintf(stdout, "DEBUG ");
#else
#define _LOG_LEVEL
#endif

#define LOGGING(pLogLevel, ...)                             \
    /* change this to compile time conditional */           \
    if (pLogLevel <= LOG_LEVEL)                             \
    {                                                       \
        _LOG_PREAMBLE                                       \
        _LOG_LEVEL                                          \
        fprintf(stdout, ##__VA_ARGS__);                     \
    }

#endif /* __LOGGING_H__ */
