/*
 * Basic level-synchronous OpenMP BFS.
 *
 * One persistent parallel team is created for the whole BFS call.  Every
 * level scans the current frontier with an `omp for` whose schedule is the
 * one requested by the caller.  A neighbour is claimed exactly once with an
 * atomic exchange on a private visited array; the winner writes its distance
 * and appends it to the next frontier through an atomic shared counter.
 *
 * The graph, distance and metrics buffers are caller-owned.  The only
 * scratch allocations made here are the two frontier arrays and the visited
 * flags; all of them are released on every path.
 */
#include "bfs.h"

#include <omp.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint32_t *current;
    uint32_t *next;
    _Atomic unsigned char *visited;
    _Atomic size_t next_size;
    _Atomic int overflow;
    uint32_t current_size;
} BasicState;

static void expand_vertex(uint32_t u, const CSRGraph *graph, int32_t *distance,
                          _Atomic unsigned char *visited, uint32_t *next,
                          size_t capacity, _Atomic size_t *next_size,
                          _Atomic int *overflow)
{
    const size_t begin = graph->row_offsets[u];
    const size_t end = graph->row_offsets[u + 1u];
    const int32_t candidate = distance[u] + 1;

    for (size_t j = begin; j < end; ++j) {
        const uint32_t v = graph->col_indices[j];

        /* Exactly one thread observes the previous value 0.  Relaxed is
         * sufficient: the frontier/distance publication is ordered by the
         * implicit barrier at the end of the level. */
        if (atomic_exchange_explicit(&visited[v], 1u, memory_order_relaxed) != 0u) {
            continue;
        }

        distance[v] = candidate;

        const size_t index =
            atomic_fetch_add_explicit(next_size, 1u, memory_order_relaxed);
        if (index < capacity) {
            next[index] = v;
        } else {
            /* Unreachable while every vertex is claimed once; kept as a
             * defensive runtime failure instead of a buffer overrun. */
            atomic_store_explicit(overflow, 1, memory_order_relaxed);
        }
    }
}

BFSStatus bfs_parallel_basic(const CSRGraph *graph, uint32_t source,
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

    BasicState state = {0};
    state.current = (uint32_t *)malloc(n * sizeof(*state.current));
    state.next = (uint32_t *)malloc(n * sizeof(*state.next));
    state.visited = (_Atomic unsigned char *)calloc(n, sizeof(*state.visited));
    if (state.current == NULL || state.next == NULL || state.visited == NULL) {
        free(state.current);
        free(state.next);
        free(state.visited);
        return BFS_ERR_MEMORY;
    }
    atomic_init(&state.next_size, 0u);
    atomic_init(&state.overflow, 0);

    int team = 0;
    int status = BFS_OK;

#pragma omp parallel num_threads(config->threads)
    {
#pragma omp single
        {
            team = omp_get_num_threads();
        }

#pragma omp for schedule(static)
        for (uint32_t i = 0u; i < graph->vertex_count; ++i) {
            distance[i] = -1;
            atomic_store_explicit(&state.visited[i], 0u, memory_order_relaxed);
        }

#pragma omp single
        {
            distance[source] = 0;
            atomic_store_explicit(&state.visited[source], 1u, memory_order_relaxed);
            state.current[0] = source;
            state.current_size = 1u;
        }

        while (state.current_size > 0u) {
#pragma omp single
            {
                atomic_store_explicit(&state.next_size, 0u, memory_order_relaxed);
                atomic_store_explicit(&state.overflow, 0, memory_order_relaxed);
            }

            if (config->schedule == BFS_SCHEDULE_STATIC) {
#pragma omp for schedule(static)
                for (uint32_t i = 0u; i < state.current_size; ++i) {
                    expand_vertex(state.current[i], graph, distance, state.visited,
                                  state.next, n, &state.next_size, &state.overflow);
                }
            } else if (config->schedule == BFS_SCHEDULE_DYNAMIC) {
#pragma omp for schedule(dynamic)
                for (uint32_t i = 0u; i < state.current_size; ++i) {
                    expand_vertex(state.current[i], graph, distance, state.visited,
                                  state.next, n, &state.next_size, &state.overflow);
                }
            } else {
#pragma omp for schedule(guided)
                for (uint32_t i = 0u; i < state.current_size; ++i) {
                    expand_vertex(state.current[i], graph, distance, state.visited,
                                  state.next, n, &state.next_size, &state.overflow);
                }
            }

#pragma omp single
            {
                const size_t produced = atomic_load_explicit(
                    &state.next_size, memory_order_relaxed);
                if (atomic_load_explicit(&state.overflow, memory_order_relaxed) != 0 ||
                    produced > n) {
                    status = BFS_ERR_RUNTIME;
                } else {
                    uint32_t *tmp = state.current;
                    state.current = state.next;
                    state.next = tmp;
                    state.current_size = (uint32_t)produced;
                }
            }

            /* The single region above has an implicit barrier, so every
             * thread observes the same status value. */
            if (status != BFS_OK) {
                break;
            }
        }
    }

    free(state.current);
    free(state.next);
    free(state.visited);

    if (status != BFS_OK) {
        return status;
    }
    metrics->threads_actual = (team > 0) ? team : 1;
    return BFS_OK;
}
