#ifndef PBFS_WALL_TIMER_H
#define PBFS_WALL_TIMER_H

/* Caller-only timer. No graph loading, allocation or validation in interval. */
#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
typedef struct { LARGE_INTEGER start, frequency; } WallTimer;
static int wall_timer_start(WallTimer *timer)
{
    return QueryPerformanceFrequency(&timer->frequency) &&
           timer->frequency.QuadPart > 0 && QueryPerformanceCounter(&timer->start);
}
static int wall_timer_stop(const WallTimer *timer, double *seconds)
{
    LARGE_INTEGER end;
    if (!QueryPerformanceCounter(&end) || end.QuadPart < timer->start.QuadPart)
        return 0;
    *seconds = (double)(end.QuadPart - timer->start.QuadPart) /
               (double)timer->frequency.QuadPart;
    return 1;
}
#else
#include <omp.h>
typedef struct { double start; } WallTimer;
static int wall_timer_start(WallTimer *timer)
{
    timer->start = omp_get_wtime();
    return 1;
}
static int wall_timer_stop(const WallTimer *timer, double *seconds)
{
    *seconds = omp_get_wtime() - timer->start;
    return 1;
}
#endif
#endif
