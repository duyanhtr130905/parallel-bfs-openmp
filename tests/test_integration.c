/* Role C: input-edge Floyd-Warshall oracle, independent of CSR construction. */
#include "bfs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

enum { N = 35, INF = 1000 };
typedef BFSStatus (*Function)(const CSRGraph *, uint32_t, int32_t *,
                              const BFSConfig *, BFSMetrics *);

static void check(const Edge *edges, size_t count, GraphMode mode)
{
    int oracle[N][N];
    CSRGraph g = {0};
    size_t rows[N + 1];
    uint32_t columns[2 * N * N];
    const Function functions[] = {bfs_serial, bfs_parallel_basic, bfs_parallel_optimized};
    const int threads[] = {1, 2, 4, 8};
    const uint32_t sources[] = {0, 17, N - 1};
    for (int u = 0; u < N; ++u)
        for (int v = 0; v < N; ++v) oracle[u][v] = u == v ? 0 : INF;
    for (size_t i = 0; i < count; ++i) {
        uint32_t u = edges[i].src, v = edges[i].dst;
        if (u != v) {
            oracle[u][v] = 1;
            if (mode == GRAPH_UNDIRECTED) oracle[v][u] = 1;
        }
    }
    for (int k = 0; k < N; ++k)
        for (int u = 0; u < N; ++u)
            for (int v = 0; v < N; ++v)
                if (oracle[u][k] + oracle[k][v] < oracle[u][v])
                    oracle[u][v] = oracle[u][k] + oracle[k][v];
    assert(graph_from_edges(N, edges, count, mode, &g) == BFS_OK);
    memcpy(rows, g.row_offsets, sizeof(rows));
    assert(g.edge_count <= sizeof(columns) / sizeof(columns[0]));
    memcpy(columns, g.col_indices, g.edge_count * sizeof(columns[0]));
    for (size_t f = 0; f < 3; ++f)
        for (size_t s = 0; s < 3; ++s)
            for (int schedule = 0; schedule < 3; ++schedule)
                for (size_t t = 0; t < 4; ++t)
                    for (int repeat = 0; repeat < 3; ++repeat) {
                        BFSConfig config = {threads[t], (BFSSchedule)schedule};
                        BFSMetrics metrics = {777};
                        int32_t d[N];
                        memset(d, 0xa5, sizeof(d));
                        assert(functions[f](&g, sources[s], d, &config, &metrics) == BFS_OK);
                        assert(metrics.threads_actual >= 1 && metrics.threads_actual <= threads[t]);
                        if (f == 0 || threads[t] == 1) assert(metrics.threads_actual == 1);
                        for (int v = 0; v < N; ++v)
                            assert(d[v] == (oracle[sources[s]][v] == INF ? -1 : oracle[sources[s]][v]));
                        assert(memcmp(rows, g.row_offsets, sizeof(rows)) == 0);
                        assert(memcmp(columns, g.col_indices, g.edge_count * sizeof(columns[0])) == 0);
                    }
    graph_free(&g);
}

int main(void)
{
    Edge edges[N * N];
    size_t count = 0;
    /* 5x7 grid, with input duplicates and loops. */
    for (uint32_t u = 0; u < N; ++u) {
        if (u % 7 < 6) edges[count++] = (Edge){u, u + 1};
        if (u + 7 < N) edges[count++] = (Edge){u, u + 7};
    }
    edges[count++] = (Edge){0, 1};
    edges[count++] = (Edge){17, 17};
    check(edges, count, GRAPH_DIRECTED);
    check(edges, count, GRAPH_UNDIRECTED);
    /* Disconnected fixed-seed random input; last vertex remains isolated. */
    uint32_t seed = UINT32_C(0x12345678);
    count = 0;
    for (int i = 0; i < 150; ++i) {
        seed = seed * UINT32_C(1664525) + UINT32_C(1013904223);
        uint32_t u = seed % (N - 1);
        seed = seed * UINT32_C(1664525) + UINT32_C(1013904223);
        edges[count++] = (Edge){u, seed % (N - 1)};
    }
    check(edges, count, GRAPH_DIRECTED);
    check(edges, count, GRAPH_UNDIRECTED);
    puts("PASS: 1296 BFS calls; input-edge Floyd-Warshall oracle, full distance, grid/random, CSR byte equality");
    return 0;
}
