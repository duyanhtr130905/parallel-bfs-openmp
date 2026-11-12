/* Serial integration; OpenMP dispatch awaits the independently merged B module. */
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "bfs.h"

static int number(const char *s, uintmax_t limit, uintmax_t *out)
{
    const unsigned char *p = (const unsigned char *)s;
    char *end;
    uintmax_t value;
    if (*p == 0) return 0;
    for (; *p; ++p) if (*p < '0' || *p > '9') return 0;
    errno = 0;
    value = strtoumax(s, &end, 10);
    if (errno == ERANGE || *end || value > limit) return 0;
    *out = value;
    return 1;
}

static int usage_error(void)
{
    fputs("Invalid arguments. Use --help.\n", stderr);
    return 2;
}

/* Verify shortest paths outside the timer: edge inequalities establish a lower
 * bound, and one predecessor at distance-1 per reached vertex proves a path.
 * Distances decrease along witnesses, so a disconnected cycle cannot pass. */
static int validate_distances(const CSRGraph *g, uint32_t source,
                              const int32_t *d, unsigned char *witness,
                              size_t *reachable)
{
    size_t u, j;
    *reachable = 0;
    if (d[source] != 0) return 0;
    for (u = 0; u < g->vertex_count; ++u) {
        if (d[u] < -1 || d[u] >= (int32_t)g->vertex_count ||
            (u != source && d[u] == 0)) return 0;
        if (d[u] < 0) continue;
        ++*reachable;
        for (j = g->row_offsets[u]; j < g->row_offsets[u + 1]; ++j) {
            uint32_t v = g->col_indices[j];
            if (d[v] < 0 || d[v] > d[u] + 1) return 0;
            if (d[v] == d[u] + 1) witness[v] = 1;
        }
    }
    for (u = 0; u < g->vertex_count; ++u)
        if (u != source && d[u] >= 0 && !witness[u]) return 0;
    return 1;
}

int main(int argc, char **argv)
{
    const char *names[] = {"--graph", "--vertices", "--source", "--algo",
                           "--threads", "--schedule", "--directed", "--undirected"};
    unsigned seen = 0;
    uintmax_t n = 0, source = 0, threads = 1;
    BFSConfig config = {1, BFS_SCHEDULE_STATIC};
    const char *graph = NULL;
    const char *algorithm = NULL;
    int i;
    if (argc == 2 && strcmp(argv[1], "--help") == 0) {
        puts("Usage: bfs --graph PATH --vertices N --source S\n"
             "  --algo serial|omp-basic|omp-opt [--threads P]\n"
             "  [--schedule static|dynamic|guided] (--directed|--undirected)\n"
             "Serial BFS available; OpenMP algorithms await integration.");
        return 0;
    }
    for (i = 1; i < argc; ++i) {
        int k;
        const char *value;
        for (k = 0; k < 8; ++k) if (strcmp(argv[i], names[k]) == 0) break;
        if (k == 8 || (seen & (1u << k))) return usage_error();
        seen |= 1u << k;
        if (k >= 6) continue;
        if (++i >= argc || strncmp(argv[i], "--", 2) == 0) return usage_error();
        value = argv[i];
        switch (k) {
        case 0: if (!*value) return usage_error(); graph = value; break;
        case 1: if (!number(value, INT32_MAX, &n) || n == 0) return usage_error(); break;
        case 2: if (!number(value, UINT32_MAX, &source)) return usage_error(); break;
        case 3:
            if (strcmp(value, "serial") && strcmp(value, "omp-basic") &&
                strcmp(value, "omp-opt")) return usage_error();
            algorithm = value;
            break;
        case 4:
            if (!number(value, INT_MAX, &threads) || threads == 0) return usage_error();
            config.threads = (int)threads;
            break;
        case 5:
            if (!strcmp(value, "static")) config.schedule = BFS_SCHEDULE_STATIC;
            else if (!strcmp(value, "dynamic")) config.schedule = BFS_SCHEDULE_DYNAMIC;
            else if (!strcmp(value, "guided")) config.schedule = BFS_SCHEDULE_GUIDED;
            else return usage_error();
            break;
        default: return usage_error();
        }
    }
    if ((seen & 15u) != 15u || source >= n ||
        ((seen >> 6) & 3u) == 0 || ((seen >> 6) & 3u) == 3u) return usage_error();
    if (strcmp(algorithm, "serial") != 0) {
        fputs("BFS_ERR_NOT_IMPLEMENTED: OpenMP module not integrated.\n", stderr);
        return 3;
    }
    {
        CSRGraph g = {0};
        BFSMetrics metrics = {0};
        GraphMode mode = (seen & (1u << 6)) ? GRAPH_DIRECTED : GRAPH_UNDIRECTED;
        int32_t *distance = NULL;
        unsigned char *witness = NULL;
        BFSStatus status;
        double start, elapsed;
        size_t reachable = 0;
        int result = 4;

        status = graph_read_edge_list(graph, (uint32_t)n, mode, &g);
        if (status != BFS_OK) goto cleanup;
        if ((size_t)n > SIZE_MAX / sizeof(*distance)) {
            status = BFS_ERR_RANGE;
            goto cleanup;
        }
        distance = malloc((size_t)n * sizeof(*distance));
        witness = calloc((size_t)n, sizeof(*witness));
        if (!distance || !witness) {
            status = BFS_ERR_MEMORY;
            goto cleanup;
        }
        start = omp_get_wtime();
        status = bfs_serial(&g, (uint32_t)source, distance, &config, &metrics);
        elapsed = omp_get_wtime() - start;
        if (status != BFS_OK) goto cleanup;
        if (metrics.threads_actual != 1 || !isfinite(elapsed) || elapsed < 0 ||
            !validate_distances(&g, (uint32_t)source, distance, witness, &reachable)) {
            status = BFS_ERR_RUNTIME;
            goto cleanup;
        }
        if (printf("{\"schema_version\":1,\"status\":\"ok\",\"algorithm\":\"serial\","
                   "\"runtime_seconds\":%.17g,\"threads_requested\":%d,"
                   "\"threads_actual\":%d,\"schedule\":\"none\",\"vertices\":%" PRIu32 ","
                   "\"edges\":%zu,\"source\":%" PRIu32 ",\"reachable\":%zu,\"directed\":%s}\n",
                   elapsed, config.threads, metrics.threads_actual, g.vertex_count,
                   g.edge_count, (uint32_t)source, reachable,
                   mode == GRAPH_DIRECTED ? "true" : "false") < 0 || fflush(stdout) == EOF) {
            status = BFS_ERR_IO;
            goto cleanup;
        }
        result = 0;
cleanup:
        if (result != 0) fprintf(stderr, "BFS execution failed (API status %d).\n", (int)status);
        free(witness);
        free(distance);
        graph_free(&g);
        return result;
    }
}
