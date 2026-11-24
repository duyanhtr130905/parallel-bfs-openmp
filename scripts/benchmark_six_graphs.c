#include "bfs.h"
#include "wall_timer.h"
#include <inttypes.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { CYCLE, GRID, TREE, LADDER } Shape;
typedef struct {
    const char *name;
    Shape shape;
    uint32_t n, width, seed;
} Dataset;

static const Dataset datasets[] = {
    {"cycle2048", CYCLE, 2048, 0, 0},
    {"grid96x64", GRID, 96 * 64, 96, 0},
    {"ladder1024", LADDER, 2048, 0, 0},
    {"tree3-small", TREE, 29524, 3, 71},
    {"tree2-large", TREE, (1u << 24) - 1, 2, 2026},
    {"tree4-large", TREE, 5592405, 4, 83},
};

static uint32_t random_next(uint32_t *state)
{
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return *state = x;
}

static int build(const Dataset *d, CSRGraph *graph, int32_t *expected)
{
    Edge *edges = malloc(2 * (size_t)d->n * sizeof(*edges));
    uint32_t *ids = malloc((size_t)d->n * sizeof(*ids));
    if (!edges || !ids) {
        free(edges);
        free(ids);
        return 0;
    }
    size_t count = 0;
    for (uint32_t i = 0; i < d->n; ++i) ids[i] = i;
    if (d->seed) {
        uint32_t state = d->seed;
        for (uint32_t i = d->n - 1; i > 1; --i) {
            uint32_t j = 1 + random_next(&state) % i;
            uint32_t saved = ids[j];
            ids[j] = ids[i];
            ids[i] = saved;
        }
    }
    expected[0] = 0;
    for (uint32_t i = 0; i < d->n; ++i) {
        switch (d->shape) {
        case CYCLE:
            edges[count++] = (Edge){i, (i + 1) % d->n};
            expected[i] = (int32_t)i;
            break;
        case GRID:
            if ((i + 1) % d->width) edges[count++] = (Edge){i, i + 1};
            if (i + d->width < d->n) edges[count++] = (Edge){i, i + d->width};
            expected[i] = (int32_t)(i / d->width + i % d->width);
            break;
        case LADDER:
            if (!(i % 2)) edges[count++] = (Edge){i, i + 1};
            if (i + 2 < d->n) edges[count++] = (Edge){i, i + 2};
            expected[i] = (int32_t)(i / 2 + i % 2);
            break;
        case TREE:
            if (i) {
                uint32_t parent = ids[(i - 1) / d->width];
                edges[count++] = (Edge){parent, ids[i]};
                expected[ids[i]] = expected[parent] + 1;
            }
            break;
        }
    }
    BFSStatus status = graph_from_edges(d->n, edges, count, GRAPH_DIRECTED, graph);
    free(ids);
    free(edges);
    return status == BFS_OK;
}

static int benchmark(const Dataset *d)
{
    CSRGraph graph = {0};
    int32_t *expected = malloc((size_t)d->n * sizeof(*expected));
    int32_t *distance = malloc((size_t)d->n * sizeof(*distance));
    int ok = expected && distance && build(d, &graph, expected);
    if (ok) {
        int32_t depth = 0;
        for (uint32_t i = 0; i < d->n; ++i)
            if (expected[i] > depth) depth = expected[i];
        const char *names[] = {"serial", "omp-basic", "omp-opt"};
        BFSStatus (*algorithms[])(const CSRGraph *, uint32_t, int32_t *,
                                  const BFSConfig *, BFSMetrics *) = {
            bfs_serial, bfs_parallel_basic, bfs_parallel_optimized
        };
        for (int round = -2; round < 12 && ok; ++round) {
            for (int slot = 0; slot < 3; ++slot) {
                int index = (slot + round + 2) % 3;
                BFSConfig config = {index ? 8 : 1, BFS_SCHEDULE_STATIC};
                BFSMetrics metrics = {0};
                WallTimer timer;
                double seconds;
                if (!wall_timer_start(&timer) ||
                    algorithms[index](&graph, 0, distance, &config, &metrics) != BFS_OK ||
                    !wall_timer_stop(&timer, &seconds) ||
                    metrics.threads_actual != config.threads ||
                    memcmp(expected, distance, (size_t)d->n * sizeof(*distance)) != 0) {
                    ok = 0;
                    break;
                }
                printf("%s,%" PRIu32 ",%zu,%" PRId32 ",%d,%s,%d,%.9f\n", d->name,
                       d->n, graph.edge_count, depth, round, names[index],
                       metrics.threads_actual, seconds * 1000.0);
                fflush(stdout);
            }
        }
    }
    graph_free(&graph);
    free(expected);
    free(distance);
    return ok;
}

int main(void)
{
    omp_set_dynamic(0);
    puts("graph,vertices,edges,max_depth,round,algorithm,threads,ms");
    for (size_t i = 0; i < sizeof(datasets) / sizeof(*datasets); ++i) {
        if (!benchmark(&datasets[i])) {
            fprintf(stderr, "Benchmark failed on %s\n", datasets[i].name);
            return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}
