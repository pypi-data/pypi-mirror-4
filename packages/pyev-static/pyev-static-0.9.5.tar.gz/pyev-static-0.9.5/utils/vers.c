// check libev version

#include <stdio.h>
#include "ev.h"

int main(int argc, char **argv){
    int major, minor;
    major = ev_version_major();
    minor = ev_version_minor();
    fprintf(stdout, "vers: %d.%d\n", major, minor);
    return 0;
}
