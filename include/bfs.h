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

typedef struct {
    int threads_actual; /* 0 on failure; measured team size on success. */
} BFSMetrics;

/* API v1 bootstrap revision (ADR-0002). Non-NULL caller-owned metrics.
 * Reset threads_actual to 0 before validation; publish only on BFS_OK.
 * Serial reports 1. Parallel measures inside each BFS work region; changing
 * team sizes across regions is BFS_ERR_RUNTIME, never a guessed maximum.
 * Caller owns distance[n] and separate non-aliasing metrics for every call. */
BFSStatus bfs_serial(const CSRGraph *graph, uint32_t source,
                     int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);
BFSStatus bfs_parallel_basic(const CSRGraph *graph, uint32_t source,
                             int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);
BFSStatus bfs_parallel_optimized(const CSRGraph *graph, uint32_t source,
                                 int32_t *distance, const BFSConfig *config, BFSMetrics *metrics);

#endif
