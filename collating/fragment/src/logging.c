#include <time.h>
#include <stdio.h>

#include "os_def.h"
#include "logging.h"

void print_timestamp(void)
{
    time_t current_time;
    struct tm * time_info;
    char timeString[64] = { '\0' };

    time(&current_time);
    /* TODO use localtime_s instead on windows */
    time_info = localtime(&current_time);
    strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S    ", time_info);

    fprintf(stdout, "%s ", timeString);
}
