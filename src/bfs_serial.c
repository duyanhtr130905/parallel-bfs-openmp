#include "bfs.h"

#include <limits.h>
#include <stdint.h>
#include <stdlib.h>

static int valid_schedule(BFSSchedule schedule)
{
    return schedule == BFS_SCHEDULE_STATIC ||
           schedule == BFS_SCHEDULE_DYNAMIC ||
           schedule == BFS_SCHEDULE_GUIDED;
}

BFSStatus bfs_serial(const CSRGraph *graph, uint32_t source,
                     int32_t *distance, const BFSConfig *config,
                     BFSMetrics *metrics)
{
    uint32_t *queue;
    size_t head = 0;
    size_t tail = 0;
    size_t i;
    size_t vertex_count;

    if (metrics != NULL) {
        metrics->threads_actual = 0;
    }
    if (graph == NULL || distance == NULL || config == NULL ||
        metrics == NULL) {
        return BFS_ERR_ARGUMENT;
    }
    if (graph->vertex_count == 0 || graph->vertex_count > INT32_MAX ||
        source >= graph->vertex_count || config->threads < 1 ||
        !valid_schedule(config->schedule)) {
        return BFS_ERR_RANGE;
    }

    vertex_count = (size_t)graph->vertex_count;
    if (vertex_count > SIZE_MAX / sizeof(*queue)) {
        return BFS_ERR_RANGE;
    }
    queue = malloc(vertex_count * sizeof(*queue));
    if (queue == NULL) {
        return BFS_ERR_MEMORY;
    }
    for (i = 0; i < vertex_count; ++i) {
        distance[i] = -1;
    }

    distance[source] = 0;
    queue[tail++] = source;
    while (head < tail) {
        uint32_t vertex = queue[head++];
        size_t begin = graph->row_offsets[vertex];
        size_t end = graph->row_offsets[vertex + 1U];
        size_t neighbor_index;

        for (neighbor_index = begin; neighbor_index < end; ++neighbor_index) {
            uint32_t neighbor = graph->col_indices[neighbor_index];
            if (distance[neighbor] == -1) {
                distance[neighbor] = distance[vertex] + 1;
                queue[tail++] = neighbor;
            }
        }
    }

    free(queue);
    metrics->threads_actual = 1;
    return BFS_OK;
}
