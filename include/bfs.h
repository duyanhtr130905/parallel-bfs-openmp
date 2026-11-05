#ifndef PBFS_BFS_H
#define PBFS_BFS_H

#include "graph.h"

typedef enum {
    BFS_SCHEDULE_STATIC = 0,
    BFS_SCHEDULE_DYNAMIC = 1,
    BFS_SCHEDULE_GUIDED = 2
} BFSSchedule;

typedef struct {
    int threads; /* Requested team size, >= 1. */
    BFSSchedule schedule;
} BFSConfig;

/* All versions use the same signature. Caller owns distance[n]. */
BFSStatus bfs_serial(const CSRGraph *graph, uint32_t source,
                     int32_t *distance, const BFSConfig *config);
BFSStatus bfs_parallel_basic(const CSRGraph *graph, uint32_t source,
                             int32_t *distance, const BFSConfig *config);
BFSStatus bfs_parallel_optimized(const CSRGraph *graph, uint32_t source,
                                 int32_t *distance, const BFSConfig *config);

#endif
