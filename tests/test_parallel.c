/*
 * Correctness tests for the two OpenMP BFS implementations.
 *
 * CSR input comes from the production loader (graph_from_edges from module A);
 * one case also goes through graph_read_edge_list.  Every distance element is
 * compared against an independent queue-based oracle written here and against
 * bfs_serial, so the parallel results are checked against both a hand-written
 * oracle and the sequential production implementation.
 */
#include "bfs.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    CSRGraph graph;
} Fixture;

typedef BFSStatus (*BfsFunction)(const CSRGraph *, uint32_t, int32_t *,
                                 const BFSConfig *, BFSMetrics *);

static int failures = 0;

#define CHECK(condition)                                                       \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__,            \
                    #condition);                                               \
            ++failures;                                                        \
        }                                                                      \
    } while (0)

#define CHECK_MSG(condition, ...)                                              \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "FAIL %s:%d: ", __FILE__, __LINE__);               \
            fprintf(stderr, __VA_ARGS__);                                      \
            fprintf(stderr, "\n");                                             \
            ++failures;                                                        \
        }                                                                      \
    } while (0)

static const struct {
    const char *name;
    BfsFunction function;
} implementations[] = {
    {"serial", bfs_serial},
    {"basic", bfs_parallel_basic},
    {"optimized", bfs_parallel_optimized},
};

static void fixture_free(Fixture *fixture)
{
    graph_free(&fixture->graph);
}

/* Build a fixture with the production CSR loader so the tests exercise the
 * same ownership, overflow and undirected-mirroring rules as the library. */
static int fixture_build(Fixture *fixture, uint32_t vertex_count,
                         const Edge *edges, size_t edge_count, GraphMode mode)
{
    memset(fixture, 0, sizeof(*fixture));
    return graph_from_edges(vertex_count, edges, edge_count, mode,
                            &fixture->graph) == BFS_OK;
}

static uint64_t fixture_checksum(const Fixture *fixture)
{
    uint64_t hash = UINT64_C(1469598103934665603);
    for (uint32_t i = 0u; i <= fixture->graph.vertex_count; ++i) {
        hash ^= (uint64_t)fixture->graph.row_offsets[i];
        hash *= UINT64_C(1099511628211);
    }
    for (size_t i = 0u; i < fixture->graph.edge_count; ++i) {
        hash ^= (uint64_t)fixture->graph.col_indices[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static int oracle_bfs(const Fixture *fixture, uint32_t source, int32_t *distance)
{
    const uint32_t n = fixture->graph.vertex_count;
    uint32_t *queue = (uint32_t *)malloc((size_t)n * sizeof(*queue));
    if (queue == NULL) {
        return 0;
    }

    for (uint32_t i = 0u; i < n; ++i) {
        distance[i] = -1;
    }
    distance[source] = 0;

    size_t head = 0u;
    size_t tail = 0u;
    queue[tail++] = source;
    while (head < tail) {
        const uint32_t u = queue[head++];
        const size_t begin = fixture->graph.row_offsets[u];
        const size_t end = fixture->graph.row_offsets[u + 1u];
        for (size_t j = begin; j < end; ++j) {
            const uint32_t v = fixture->graph.col_indices[j];
            if (distance[v] == -1) {
                distance[v] = distance[u] + 1;
                queue[tail++] = v;
            }
        }
    }

    free(queue);
    return 1;
}

static void compare_distances(const char *fixture_name, const char *impl_name,
                              const char *schedule_name, uint32_t source,
                              int threads, const int32_t *expected,
                              const int32_t *actual, uint32_t n)
{
    for (uint32_t i = 0u; i < n; ++i) {
        if (actual[i] != expected[i]) {
            CHECK_MSG(0,
                      "%s/%s/%s source=%u threads=%d vertex=%u: got %d, expected %d",
                      fixture_name, impl_name, schedule_name,
                      (unsigned)source, threads, (unsigned)i,
                      (int)actual[i], (int)expected[i]);
            return;
        }
    }
}

static const char *schedule_name(BFSSchedule schedule)
{
    switch (schedule) {
    case BFS_SCHEDULE_STATIC:
        return "static";
    case BFS_SCHEDULE_DYNAMIC:
        return "dynamic";
    case BFS_SCHEDULE_GUIDED:
        return "guided";
    default:
        return "invalid";
    }
}

static void run_fixture(const char *name, const Fixture *fixture,
                        const uint32_t *sources, size_t source_count, int heavy)
{
    const uint32_t n = fixture->graph.vertex_count;
    int32_t *expected = (int32_t *)malloc((size_t)n * sizeof(*expected));
    int32_t *actual = (int32_t *)malloc((size_t)n * sizeof(*actual));
    if (expected == NULL || actual == NULL) {
        free(expected);
        free(actual);
        CHECK_MSG(0, "%s: could not allocate test buffers", name);
        return;
    }

    const uint64_t before = fixture_checksum(fixture);
    const int all_threads[] = {1, 2, 4, 8};
    const int heavy_threads[] = {1, 4, 8};
    const int *thread_values = heavy ? heavy_threads : all_threads;
    const size_t thread_count = heavy ? (sizeof(heavy_threads) / sizeof(heavy_threads[0]))
                                      : (sizeof(all_threads) / sizeof(all_threads[0]));
    const int repeats = heavy ? 1 : 2;

    for (size_t impl = 0u;
         impl < sizeof(implementations) / sizeof(implementations[0]); ++impl) {
        for (size_t s = 0u; s < source_count; ++s) {
            const uint32_t source = sources[s];
            if (!oracle_bfs(fixture, source, expected)) {
                CHECK_MSG(0, "%s: oracle allocation failed", name);
                continue;
            }

            for (int schedule = (int)BFS_SCHEDULE_STATIC;
                 schedule <= (int)BFS_SCHEDULE_GUIDED; ++schedule) {
                for (size_t t = 0u; t < thread_count; ++t) {
                    for (int repeat = 0; repeat < repeats; ++repeat) {
                        BFSConfig config;
                        config.threads = thread_values[t];
                        config.schedule = (BFSSchedule)schedule;
                        BFSMetrics metrics;
                        metrics.threads_actual = 12345;

                        memset(actual, 0xA5, (size_t)n * sizeof(*actual));
                        const BFSStatus status = implementations[impl].function(
                            &fixture->graph, source, actual, &config, &metrics);
                        CHECK_MSG(status == BFS_OK,
                                  "%s/%s/%s source=%u threads=%d repeat=%d: status %d",
                                  name, implementations[impl].name,
                                  schedule_name((BFSSchedule)schedule),
                                  (unsigned)source, thread_values[t], repeat,
                                  (int)status);
                        if (status != BFS_OK) {
                            continue;
                        }

                        CHECK_MSG(metrics.threads_actual >= 1,
                                  "%s/%s/%s: threads_actual=%d",
                                  name, implementations[impl].name,
                                  schedule_name((BFSSchedule)schedule),
                                  metrics.threads_actual);
                        if (config.threads == 1) {
                            CHECK_MSG(metrics.threads_actual == 1,
                                      "%s/%s/%s: requested 1 thread but actual=%d",
                                      name, implementations[impl].name,
                                      schedule_name((BFSSchedule)schedule),
                                      metrics.threads_actual);
                        }
                        CHECK_MSG(metrics.threads_actual <= config.threads,
                                  "%s/%s/%s: actual %d > requested %d",
                                  name, implementations[impl].name,
                                  schedule_name((BFSSchedule)schedule),
                                  metrics.threads_actual, config.threads);
                        compare_distances(name, implementations[impl].name,
                                          schedule_name((BFSSchedule)schedule),
                                          source, config.threads, expected, actual, n);
                        CHECK_MSG(fixture_checksum(fixture) == before,
                                  "%s/%s: CSR changed during BFS", name,
                                  implementations[impl].name);
                    }
                }
            }
        }
    }

    free(expected);
    free(actual);
}

static void test_hand_fixture(void)
{
    /* Same data as datasets/small/disconnected.edgelist and its hand-written
     * expected distances: source=0, directed, n=6. */
    const Edge edges[] = {
        {0u, 1u}, {0u, 2u}, {1u, 3u}, {2u, 3u}, {4u, 4u},
    };
    const int32_t expected[6] = {0, 1, 1, 2, -1, -1};
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, 6u, edges,
                            sizeof(edges) / sizeof(edges[0]), GRAPH_DIRECTED),
              "hand fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        return;
    }

    for (size_t impl = 0u;
         impl < sizeof(implementations) / sizeof(implementations[0]); ++impl) {
        for (int schedule = (int)BFS_SCHEDULE_STATIC;
             schedule <= (int)BFS_SCHEDULE_GUIDED; ++schedule) {
            BFSConfig config;
            config.threads = 4;
            config.schedule = (BFSSchedule)schedule;
            BFSMetrics metrics = {0};
            int32_t actual[6] = {0};
            const BFSStatus status = implementations[impl].function(
                &fixture.graph, 0u, actual, &config, &metrics);
            CHECK_MSG(status == BFS_OK,
                      "hand fixture/%s/%s: status %d",
                      implementations[impl].name,
                      schedule_name((BFSSchedule)schedule), (int)status);
            if (status == BFS_OK) {
                compare_distances("hand", implementations[impl].name,
                                  schedule_name((BFSSchedule)schedule), 0u,
                                  config.threads, expected, actual, 6u);
            }
        }
    }
    fixture_free(&fixture);
}

static void test_edge_list_loader(void)
{
    /* End-to-end loader path: edge-list text (comment, CRLF, self-loop) goes
     * through graph_read_edge_list and then the same BFS matrix. */
    const char *path = "build/test_parallel_input.edgelist";
    const char *content =
        "# synthetic edge-list for the parallel BFS integration test\n"
        "0 1\n"
        "0 2\r\n"
        "1 3\n"
        "2 3\n"
        "4 4\n";
    FILE *file = fopen(path, "wb");
    CHECK_MSG(file != NULL, "could not create %s", path);
    if (file == NULL) {
        return;
    }
    const size_t length = strlen(content);
    CHECK_MSG(fwrite(content, 1u, length, file) == length,
              "short write to %s", path);
    CHECK_MSG(fclose(file) == 0, "could not close %s", path);

    Fixture fixture;
    memset(&fixture, 0, sizeof(fixture));
    const BFSStatus status =
        graph_read_edge_list(path, 6u, GRAPH_DIRECTED, &fixture.graph);
    CHECK_MSG(status == BFS_OK, "graph_read_edge_list returned %d", (int)status);
    if (status == BFS_OK) {
        const uint32_t sources[] = {0u};
        run_fixture("edge_list", &fixture, sources, 1u, 0);
    }
    fixture_free(&fixture);
    CHECK_MSG(remove(path) == 0, "could not remove %s", path);
}

static void test_invalid_arguments(void)
{
    const Edge edges[] = {{0u, 1u}, {1u, 2u}, {2u, 3u}};
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, 4u, edges,
                            sizeof(edges) / sizeof(edges[0]), GRAPH_UNDIRECTED),
              "invalid-argument fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        return;
    }

    for (size_t impl = 0u;
         impl < sizeof(implementations) / sizeof(implementations[0]); ++impl) {
        BfsFunction function = implementations[impl].function;
        const char *name = implementations[impl].name;
        int32_t distance[4] = {0};
        BFSConfig good;
        good.threads = 2;
        good.schedule = BFS_SCHEDULE_STATIC;
        BFSMetrics metrics;

        metrics.threads_actual = 77;
        CHECK_MSG(function(NULL, 0u, distance, &good, &metrics) == BFS_ERR_ARGUMENT,
                  "%s: NULL graph was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for NULL graph", name);

        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, NULL, &good, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: NULL distance was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for NULL distance", name);

        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, NULL, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: NULL config was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for NULL config", name);

        CHECK_MSG(function(&fixture.graph, 0u, distance, &good, NULL) ==
                      BFS_ERR_ARGUMENT,
                  "%s: NULL metrics was not rejected", name);

        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 4u, distance, &good, &metrics) ==
                      BFS_ERR_RANGE,
                  "%s: out-of-range source was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for out-of-range source", name);

        BFSConfig bad = good;
        bad.threads = 0;
        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, &bad, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: threads=0 was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for threads=0", name);

        bad.threads = -3;
        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, &bad, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: negative threads was not rejected", name);

        bad = good;
        bad.schedule = (BFSSchedule)99;
        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, &bad, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: invalid schedule was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for invalid schedule", name);

        bad.schedule = (BFSSchedule)-1;
        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, &bad, &metrics) ==
                      BFS_ERR_ARGUMENT,
                  "%s: negative schedule was not rejected", name);

        CSRGraph empty = {0u, 0u, NULL, NULL};
        metrics.threads_actual = 77;
        CHECK_MSG(function(&empty, 0u, distance, &good, &metrics) == BFS_ERR_RANGE,
                  "%s: empty graph was not rejected", name);
        CHECK_MSG(metrics.threads_actual == 0,
                  "%s: metrics not reset for empty graph", name);

        /* bfs_serial's contract does not require rejecting a structurally
         * inconsistent CSR (NULL offsets/columns); the parallel
         * implementations add that guard.  Calling serial with those inputs
         * would dereference the missing arrays, so only the parallel
         * implementations are exercised here. */
        if (function != bfs_serial) {
            CSRGraph broken = {4u, 0u, NULL, NULL};
            metrics.threads_actual = 77;
            CHECK_MSG(function(&broken, 0u, distance, &good, &metrics) ==
                          BFS_ERR_ARGUMENT,
                      "%s: missing row_offsets was not rejected", name);

            CSRGraph missing_columns = {4u, 1u, fixture.graph.row_offsets, NULL};
            metrics.threads_actual = 77;
            CHECK_MSG(function(&missing_columns, 0u, distance, &good, &metrics) ==
                          BFS_ERR_ARGUMENT,
                      "%s: missing col_indices with edges was not rejected", name);
            CHECK_MSG(metrics.threads_actual == 0,
                      "%s: metrics not reset for missing col_indices", name);
        }

        metrics.threads_actual = 77;
        CHECK_MSG(function(&fixture.graph, 0u, distance, &good, &metrics) == BFS_OK,
                  "%s: valid call failed", name);
        CHECK_MSG(metrics.threads_actual >= 1 && metrics.threads_actual <= 2,
                  "%s: valid call published threads_actual=%d", name,
                  metrics.threads_actual);
    }

    fixture_free(&fixture);
}

static void test_single_vertex(void)
{
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, 1u, NULL, 0u, GRAPH_DIRECTED),
              "single-vertex fixture could not be built");
    const uint32_t sources[] = {0u};
    run_fixture("single_vertex", &fixture, sources, 1u, 0);
    fixture_free(&fixture);
}

static void test_no_edges(void)
{
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, 4u, NULL, 0u, GRAPH_UNDIRECTED),
              "no-edge fixture could not be built");
    const uint32_t sources[] = {0u, 3u};
    run_fixture("no_edges", &fixture, sources, 2u, 0);
    fixture_free(&fixture);
}

static void test_path(void)
{
    enum { n = 513 };
    Edge *edges = (Edge *)malloc((size_t)(n - 1) * sizeof(*edges));
    CHECK_MSG(edges != NULL, "path edges allocation failed");
    if (edges == NULL) {
        return;
    }
    for (uint32_t i = 0u; i + 1u < (uint32_t)n; ++i) {
        edges[i].src = i;
        edges[i].dst = i + 1u;
    }
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, (uint32_t)n, edges, (size_t)(n - 1),
                            GRAPH_UNDIRECTED),
              "path fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        free(edges);
        return;
    }
    const uint32_t sources[] = {0u, (uint32_t)n / 2u, (uint32_t)n - 1u};
    run_fixture("path513", &fixture, sources, 3u, 0);
    fixture_free(&fixture);
    free(edges);
}

static void test_star(void)
{
    enum { n = 2049 };
    const size_t edge_count = (size_t)n - 1u;
    Edge *edges = (Edge *)malloc(edge_count * sizeof(*edges));
    CHECK_MSG(edges != NULL, "star edges allocation failed");
    if (edges == NULL) {
        return;
    }
    for (uint32_t i = 1u; i < (uint32_t)n; ++i) {
        edges[i - 1u].src = 0u;
        edges[i - 1u].dst = i;
    }
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, (uint32_t)n, edges, edge_count,
                            GRAPH_UNDIRECTED),
              "star fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        free(edges);
        return;
    }
    const uint32_t sources[] = {0u, 1u, (uint32_t)n - 1u};
    run_fixture("star2049", &fixture, sources, 3u, 1);
    fixture_free(&fixture);
    free(edges);
}

static void test_diamond(void)
{
    const Edge edges[] = {
        {0u, 1u}, {0u, 2u}, {1u, 3u}, {2u, 3u}, {3u, 4u},
    };
    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, 5u, edges,
                            sizeof(edges) / sizeof(edges[0]), GRAPH_DIRECTED),
              "diamond fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        return;
    }
    const uint32_t sources[] = {0u, 1u, 3u};
    run_fixture("diamond5", &fixture, sources, 3u, 0);
    fixture_free(&fixture);
}

static void test_cycle_and_duplicates(void)
{
    const Edge cycle[] = {
        {0u, 1u}, {1u, 2u}, {2u, 3u}, {3u, 4u}, {4u, 5u}, {5u, 0u},
    };
    Fixture cycle_fixture;
    CHECK_MSG(fixture_build(&cycle_fixture, 6u, cycle,
                            sizeof(cycle) / sizeof(cycle[0]), GRAPH_DIRECTED),
              "cycle fixture could not be built");
    if (cycle_fixture.graph.row_offsets == NULL) {
        return;
    }
    const uint32_t cycle_sources[] = {0u, 2u, 5u};
    run_fixture("directed_cycle6", &cycle_fixture, cycle_sources, 3u, 0);
    fixture_free(&cycle_fixture);

    const Edge duplicates[] = {
        {0u, 1u}, {0u, 1u}, {1u, 1u}, {1u, 2u}, {2u, 2u},
    };
    Fixture duplicate_fixture;
    CHECK_MSG(fixture_build(&duplicate_fixture, 4u, duplicates,
                            sizeof(duplicates) / sizeof(duplicates[0]),
                            GRAPH_UNDIRECTED),
              "duplicate fixture could not be built");
    if (duplicate_fixture.graph.row_offsets == NULL) {
        return;
    }
    const uint32_t duplicate_sources[] = {0u, 2u, 3u};
    run_fixture("duplicates4", &duplicate_fixture, duplicate_sources, 3u, 0);
    fixture_free(&duplicate_fixture);
}

static void test_contention(void)
{
    /* Wide bipartite layer: every one of `hubs` level-1 vertices points to all
     * `targets` level-2 vertices, so each target is claimed `hubs` times in a
     * single level.  This exercises the atomic visit claim under contention
     * and a large next frontier. */
    enum { hubs = 64, targets = 256 };
    const uint32_t n = (uint32_t)(1 + hubs + targets);
    const size_t edge_count = (size_t)hubs + (size_t)hubs * (size_t)targets;
    Edge *edges = (Edge *)malloc(edge_count * sizeof(*edges));
    CHECK_MSG(edges != NULL, "contention edges allocation failed");
    if (edges == NULL) {
        return;
    }

    size_t k = 0u;
    for (uint32_t h = 0u; h < (uint32_t)hubs; ++h) {
        edges[k].src = 0u;
        edges[k].dst = 1u + h;
        ++k;
    }
    for (uint32_t h = 0u; h < (uint32_t)hubs; ++h) {
        for (uint32_t t = 0u; t < (uint32_t)targets; ++t) {
            edges[k].src = 1u + h;
            edges[k].dst = 1u + (uint32_t)hubs + t;
            ++k;
        }
    }
    CHECK_MSG(k == edge_count, "contention fixture produced %zu of %zu edges", k,
              edge_count);

    Fixture fixture;
    CHECK_MSG(fixture_build(&fixture, n, edges, k, GRAPH_DIRECTED),
              "contention fixture could not be built");
    if (fixture.graph.row_offsets == NULL) {
        free(edges);
        return;
    }
    const uint32_t sources[] = {0u};
    run_fixture("contention", &fixture, sources, 1u, 1);
    fixture_free(&fixture);
    free(edges);
}

static uint32_t next_random(uint32_t *state)
{
    *state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
    return *state;
}

static void test_random_graphs(void)
{
    const uint32_t n = 257u;
    const size_t edge_count = 1024u;
    Edge *edges = (Edge *)malloc(edge_count * sizeof(*edges));
    CHECK_MSG(edges != NULL, "random edges allocation failed");
    if (edges == NULL) {
        return;
    }
    uint32_t state = UINT32_C(0xC0FFEE42);
    for (size_t i = 0u; i < edge_count; ++i) {
        edges[i].src = next_random(&state) % n;
        edges[i].dst = next_random(&state) % n;
    }

    Fixture directed;
    CHECK_MSG(fixture_build(&directed, n, edges, edge_count, GRAPH_DIRECTED),
              "random directed fixture could not be built");
    if (directed.graph.row_offsets == NULL) {
        free(edges);
        return;
    }
    const uint32_t sources[] = {0u, n / 2u, n - 1u};
    run_fixture("random257_directed", &directed, sources, 3u, 0);
    fixture_free(&directed);

    Fixture undirected;
    const uint32_t undirected_n = 193u;
    const size_t undirected_edges = 800u;
    uint32_t undirected_state = UINT32_C(0x5EED1234);
    for (size_t i = 0u; i < undirected_edges; ++i) {
        edges[i].src = next_random(&undirected_state) % undirected_n;
        edges[i].dst = next_random(&undirected_state) % undirected_n;
    }
    CHECK_MSG(fixture_build(&undirected, undirected_n, edges, undirected_edges,
                            GRAPH_UNDIRECTED),
              "random undirected fixture could not be built");
    if (undirected.graph.row_offsets == NULL) {
        free(edges);
        return;
    }
    const uint32_t undirected_sources[] = {0u, 96u, 192u};
    run_fixture("random193_undirected", &undirected, undirected_sources, 3u, 0);
    fixture_free(&undirected);

    free(edges);
}

int main(void)
{
    test_hand_fixture();
    test_edge_list_loader();
    test_single_vertex();
    test_no_edges();
    test_path();
    test_star();
    test_diamond();
    test_cycle_and_duplicates();
    test_contention();
    test_random_graphs();
    test_invalid_arguments();

    if (failures != 0) {
        fprintf(stderr, "FAIL: %d parallel BFS check(s) failed\n", failures);
        return 1;
    }
    printf("PASS: parallel BFS oracle, thread/schedule sweep, metrics and CSR immutability\n");
    return 0;
}
