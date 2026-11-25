#include "bfs.h"
#include "wall_timer.h"
#include <inttypes.h>
#include <math.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static void oracle(const CSRGraph *graph, int32_t *expected, uint32_t *queue)
{
    for (uint32_t v = 0; v < graph->vertex_count; ++v)
        expected[v] = -1;
    expected[0] = 0;
    queue[0] = 0;
    size_t tail = 1;
    for (size_t head = 0; head < tail; ++head) {
        uint32_t v = queue[head];
        for (size_t e = graph->row_offsets[v]; e < graph->row_offsets[v + 1]; ++e) {
            uint32_t u = graph->col_indices[e];
            if (expected[u] == -1) {
                expected[u] = expected[v] + 1;
                queue[tail++] = u;
            }
        }
    }
}

static void profile(const CSRGraph *graph, const int32_t *expected, uint32_t *width)
{
    int32_t depth = 0;
    size_t arcs = 0;
    memset(width, 0, graph->vertex_count * sizeof(*width));
    for (uint32_t v = 0; v < graph->vertex_count; ++v) {
        if (expected[v] < 0)
            continue;
        ++width[expected[v]];
        if (expected[v] > depth)
            depth = expected[v];
        arcs += graph->row_offsets[v + 1] - graph->row_offsets[v];
    }
    fprintf(stderr, "csr_arcs,%zu\nscanned_arcs,%zu\n", graph->edge_count, arcs);
    for (int32_t level = 0; level <= depth; ++level)
        fprintf(stderr, "frontier,%" PRId32 ",%" PRIu32 "\n", level, width[level]);
}

static int measure(const CSRGraph *graph, const int32_t *expected, int32_t *distance, int threads)
{
    const char *names[] = {"serial", "omp-basic", "omp-opt"};
    BFSStatus (*algorithms[])(const CSRGraph *, uint32_t, int32_t *,
                             const BFSConfig *, BFSMetrics *) = {
        bfs_serial, bfs_parallel_basic, bfs_parallel_optimized
    };
    puts("round,slot,utc,algorithm,requested,actual,ms,bfs_status,validated");
    for (int round = -2; round < 12; ++round) {
        for (int slot = 0; slot < 3; ++slot) {
            int index = (slot + round + 2) % 3;
            BFSConfig config = {index ? threads : 1, BFS_SCHEDULE_STATIC};
            BFSMetrics metrics = {0};
            WallTimer timer;
            double seconds = 0;
            char utc[32];
            time_t now = time(NULL);
            struct tm *calendar = gmtime(&now);
            if (!calendar || !strftime(utc, sizeof(utc), "%Y-%m-%dT%H:%M:%SZ", calendar) ||
                !wall_timer_start(&timer))
                return 0;
            BFSStatus status = algorithms[index](graph, 0, distance, &config, &metrics);
            int timed = wall_timer_stop(&timer, &seconds) && isfinite(seconds) && seconds > 0;
            int validated = status == BFS_OK &&
                memcmp(expected, distance, graph->vertex_count * sizeof(*distance)) == 0;
            printf("%d,%d,%s,%s,%d,%d,%.12g,%d,%d\n", round, slot, utc, names[index],
                   config.threads, metrics.threads_actual, timed ? seconds * 1000 : 0,
                   (int)status, validated);
            fflush(stdout);
            if (!timed || !validated || metrics.threads_actual != config.threads)
                return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    if (argc != 5 || (strcmp(argv[3], "directed") && strcmp(argv[3], "undirected")))
        return EXIT_FAILURE;
    char *end;
    unsigned long vertices = strtoul(argv[2], &end, 10);
    if (*end || vertices == 0 || vertices > INT32_MAX)
        return EXIT_FAILURE;
    long threads = strtol(argv[4], &end, 10);
    if (*end || threads < 1 || threads > 64)
        return EXIT_FAILURE;
    CSRGraph graph = {0};
    GraphMode mode = !strcmp(argv[3], "directed") ? GRAPH_DIRECTED : GRAPH_UNDIRECTED;
    if (graph_read_edge_list(argv[1], (uint32_t)vertices, mode, &graph) != BFS_OK)
        return EXIT_FAILURE;
    uint32_t *queue = malloc(vertices * sizeof(*queue));
    int32_t *expected = malloc(vertices * sizeof(*expected));
    int32_t *distance = malloc(vertices * sizeof(*distance));
    int ok = queue && expected && distance;
    if (ok) {
        oracle(&graph, expected, queue);
        profile(&graph, expected, queue);
        free(queue);
        queue = NULL;
        omp_set_dynamic(0);
        ok = measure(&graph, expected, distance, (int)threads);
    }
    free(queue);
    free(expected);
    free(distance);
    graph_free(&graph);
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
