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
