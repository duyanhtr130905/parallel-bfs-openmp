/*
 * Optimized level-synchronous OpenMP BFS.
 *
 * The visited claim is identical to the basic version: an atomic exchange
 * decides which thread owns a newly discovered vertex.  The difference is
 * how the next frontier is collected.  Winners append to a thread-local
 * buffer instead of contending on one shared atomic counter.  At the end of
 * a level the per-thread counts are prefix-summed inside a single region and
 * every thread copies its own buffer into the shared next frontier.
 */
#include "bfs.h"

#include <omp.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

/* Return 1 when appended, 0 when the level already holds all vertices and
 * -1 when the local buffer could not grow.  Callers treat 0 as a defensive
 * runtime failure and -1 as an allocation failure. */
static int append_local(uint32_t **buffer, size_t *capacity, size_t *count,
                        size_t limit, uint32_t value)
{
    if (*count >= limit) {
        return 0;
    }
    if (*count == *capacity) {
        size_t new_capacity = (*capacity == 0u) ? 64u : *capacity * 2u;
        if (new_capacity > limit) {
            new_capacity = limit;
        }
        if (new_capacity <= *capacity) {
            return 0;
        }
        uint32_t *grown =
            (uint32_t *)realloc(*buffer, new_capacity * sizeof(*grown));
        if (grown == NULL) {
            return -1;
        }
        *buffer = grown;
        *capacity = new_capacity;
    }
    (*buffer)[*count] = value;
    ++*count;
    return 1;
}

static void expand_vertex_opt(uint32_t u, const CSRGraph *graph, int32_t *distance,
                              _Atomic unsigned char *visited, uint32_t **buffer,
                              size_t *capacity, size_t *count, size_t limit,
                              _Atomic int *allocation_failed,
                              _Atomic int *frontier_overflow)
{
    const size_t begin = graph->row_offsets[u];
    const size_t end = graph->row_offsets[u + 1u];
    const int32_t candidate = distance[u] + 1;

    for (size_t j = begin; j < end; ++j) {
        const uint32_t v = graph->col_indices[j];

        /* See bfs_parallel_basic.c: relaxed exchange is enough because the
         * level barrier publishes distance and frontier writes. */
        if (atomic_exchange_explicit(&visited[v], 1u, memory_order_relaxed) != 0u) {
            continue;
        }

        distance[v] = candidate;

        const int appended = append_local(buffer, capacity, count, limit, v);
        if (appended < 0) {
            atomic_store_explicit(allocation_failed, 1, memory_order_relaxed);
            return;
        }
        if (appended == 0) {
            atomic_store_explicit(frontier_overflow, 1, memory_order_relaxed);
            return;
        }
    }
}

BFSStatus bfs_parallel_optimized(const CSRGraph *graph, uint32_t source,
                                 int32_t *distance, const BFSConfig *config,
                                 BFSMetrics *metrics)
{
    if (metrics != NULL) {
        metrics->threads_actual = 0;
    }
    if (graph == NULL || distance == NULL || config == NULL || metrics == NULL) {
        return BFS_ERR_ARGUMENT;
    }
    if (config->threads < 1 ||
        (unsigned)config->schedule > (unsigned)BFS_SCHEDULE_GUIDED) {
        return BFS_ERR_ARGUMENT;
    }
    if (graph->vertex_count == 0u || graph->vertex_count > (uint32_t)INT32_MAX ||
        source >= graph->vertex_count) {
        return BFS_ERR_RANGE;
    }
    if (graph->row_offsets == NULL ||
        (graph->edge_count > 0u && graph->col_indices == NULL)) {
        return BFS_ERR_ARGUMENT;
    }

    const size_t n = (size_t)graph->vertex_count;
    if (n > SIZE_MAX / sizeof(uint32_t)) {
        return BFS_ERR_RANGE;
    }

    uint32_t *current = (uint32_t *)malloc(n * sizeof(*current));
    uint32_t *next = (uint32_t *)malloc(n * sizeof(*next));
    _Atomic unsigned char *visited =
        (_Atomic unsigned char *)calloc(n, sizeof(*visited));
    if (current == NULL || next == NULL || visited == NULL) {
        free(current);
        free(next);
        free(visited);
        return BFS_ERR_MEMORY;
    }

    int team = 0;
    int status = BFS_OK;
    int setup_failed = 0;
    uint32_t current_size = 0u;
    size_t next_size = 0u;
    _Atomic int allocation_failed = 0;
    _Atomic int frontier_overflow = 0;
    uint32_t **local_buffers = NULL;
    size_t *local_capacities = NULL;
    size_t *local_counts = NULL;
    size_t *offsets = NULL;

#pragma omp parallel num_threads(config->threads)
    {
#pragma omp single
        {
            team = omp_get_num_threads();
            const size_t team_size = (size_t)team;
            local_buffers =
                (uint32_t **)calloc(team_size, sizeof(*local_buffers));
            local_capacities =
                (size_t *)calloc(team_size, sizeof(*local_capacities));
            local_counts = (size_t *)calloc(team_size, sizeof(*local_counts));
            offsets = (size_t *)calloc(team_size + 1u, sizeof(*offsets));
            if (local_buffers == NULL || local_capacities == NULL ||
                local_counts == NULL || offsets == NULL) {
                setup_failed = 1;
                status = BFS_ERR_MEMORY;
            } else {
                atomic_store_explicit(&allocation_failed, 0, memory_order_relaxed);
                atomic_store_explicit(&frontier_overflow, 0, memory_order_relaxed);
            }
        }

        if (!setup_failed) {
            const int tid = omp_get_thread_num();

#pragma omp for schedule(static)
            for (uint32_t i = 0u; i < graph->vertex_count; ++i) {
                distance[i] = -1;
                atomic_store_explicit(&visited[i], 0u, memory_order_relaxed);
            }

#pragma omp single
            {
                distance[source] = 0;
                atomic_store_explicit(&visited[source], 1u, memory_order_relaxed);
                current[0] = source;
                current_size = 1u;
            }

            while (current_size > 0u && status == BFS_OK) {
                local_counts[tid] = 0u;

#pragma omp single
                {
                    atomic_store_explicit(&allocation_failed, 0,
                                          memory_order_relaxed);
                    atomic_store_explicit(&frontier_overflow, 0,
                                          memory_order_relaxed);
                }

                if (config->schedule == BFS_SCHEDULE_STATIC) {
#pragma omp for schedule(static)
                    for (uint32_t i = 0u; i < current_size; ++i) {
                        const uint32_t u = current[i];
                        expand_vertex_opt(u, graph, distance, visited,
                                          &local_buffers[tid],
                                          &local_capacities[tid],
                                          &local_counts[tid], n,
                                          &allocation_failed, &frontier_overflow);
                    }
                } else if (config->schedule == BFS_SCHEDULE_DYNAMIC) {
#pragma omp for schedule(dynamic)
                    for (uint32_t i = 0u; i < current_size; ++i) {
                        const uint32_t u = current[i];
                        expand_vertex_opt(u, graph, distance, visited,
                                          &local_buffers[tid],
                                          &local_capacities[tid],
                                          &local_counts[tid], n,
                                          &allocation_failed, &frontier_overflow);
                    }
                } else {
#pragma omp for schedule(guided)
                    for (uint32_t i = 0u; i < current_size; ++i) {
                        const uint32_t u = current[i];
                        expand_vertex_opt(u, graph, distance, visited,
                                          &local_buffers[tid],
                                          &local_capacities[tid],
                                          &local_counts[tid], n,
                                          &allocation_failed, &frontier_overflow);
                    }
                }

                /* The omp for above has an implicit barrier, so every thread
                 * observes the same failure flags. */
                if (atomic_load_explicit(&allocation_failed,
                                         memory_order_relaxed) != 0) {
#pragma omp single
                    {
                        status = BFS_ERR_MEMORY;
                    }
                    break;
                }
                if (atomic_load_explicit(&frontier_overflow,
                                         memory_order_relaxed) != 0) {
#pragma omp single
                    {
                        status = BFS_ERR_RUNTIME;
                    }
                    break;
                }

#pragma omp single
                {
                    size_t total = 0u;
                    int invalid = 0;
                    for (int t = 0; t < team; ++t) {
                        if (local_counts[t] > n - total) {
                            invalid = 1;
                            break;
                        }
                        offsets[t] = total;
                        total += local_counts[t];
                    }
                    if (invalid || total > n) {
                        status = BFS_ERR_RUNTIME;
                    } else {
                        offsets[team] = total;
                        next_size = total;
                    }
                }
                if (status != BFS_OK) {
                    break;
                }

                /* Each thread copies its own segment; the offset table was
                 * published by the single region's implicit barrier. */
                const size_t own = local_counts[tid];
                for (size_t j = 0u; j < own; ++j) {
                    next[offsets[tid] + j] = local_buffers[tid][j];
                }

#pragma omp barrier

#pragma omp single
                {
                    uint32_t *tmp = current;
                    current = next;
                    next = tmp;
                    current_size = (uint32_t)next_size;
                }
            }

            free(local_buffers[tid]);
        }
    }

    free(local_buffers);
    free(local_capacities);
    free(local_counts);
    free(offsets);
    free(current);
    free(next);
    free(visited);

    if (status != BFS_OK) {
        return status;
    }
    metrics->threads_actual = (team > 0) ? team : 1;
    return BFS_OK;
}
