#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

#include "ncd.h"

int main(int argc, char* argv[])
{
    double lNCDResult = -INFINITY;

    unsigned const char* lFragment1 = "aaaaaaaaaaaa";
    unsigned const char* lFragment2 = "aaaaaaaaaaaa";

    lNCDResult = ncd(lFragment1, 
            lFragment2,
            (unsigned int)strlen((const char*)lFragment1));

    fprintf(stdout, "NCD Result: %f\n", lNCDResult);

    return EXIT_SUCCESS;
}

