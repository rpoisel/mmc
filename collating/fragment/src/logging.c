#include <stdio.h>
#include <stdarg.h>

#include "os_def.h"
#include "logging.h"

void print_timestamp(void)
{
    time_t current_time;
    struct tm * time_info;
    char timeString[32];  // space for "HH:MM:SS\0"

    time(&current_time);
    time_info = localtime(&current_time);

    strftime(timeString, sizeof(timeString), "%Y-%m-%d %T    ", time_info);
    fprintf(stdout, "%s ", timeString);
}

void print_loglevel(enum LogLevel pLogLevel)
{
    switch(pLogLevel)
    {
        case LOG_EMERG:
            fprintf(stdout, "EMERG ");
            break;
        case LOG_ALERT:
            fprintf(stdout, "ALERT ");
            break;
        case LOG_CRIT:
            fprintf(stdout, "CRIT ");
            break;
        case LOG_ERROR:
            fprintf(stdout, "ERROR ");
            break;
        case LOG_WARN:
            fprintf(stdout, "WARN ");
            break;
        case LOG_NOTICE:
            fprintf(stdout, "NOTICE ");
            break;
        case LOG_INFO:
            fprintf(stdout, "INFO ");
            break;
        case LOG_DEBUG:
            fprintf(stdout, "DEBUG ");
            break;
        default:
            break;
    }
}
