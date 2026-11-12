#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include <math.h>
#include <stdio.h>
#include <time.h>
#include "../src/wall_timer.h"
int main(void)
{
    WallTimer timer;
    double seconds;
    if (!wall_timer_start(&timer)) return 1;
#ifdef _WIN32
    Sleep(30);
#else
    const struct timespec delay = {0, 30000000};
    if (nanosleep(&delay, NULL) != 0) return 1;
#endif
    if (!wall_timer_stop(&timer, &seconds) || !isfinite(seconds) ||
        seconds < 0.02 || seconds > 5.0) return 1;
#ifdef _WIN32
    if (timer.frequency.QuadPart < 1000000) return 1;
    printf("PASS: QPC frequency=%lld Hz; sleep interval=%.9f s\n",
           (long long)timer.frequency.QuadPart, seconds);
#else
    printf("PASS: OpenMP wall timer; sleep interval=%.9f s\n", seconds);
#endif
    return 0;
}
