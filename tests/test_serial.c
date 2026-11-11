#include "bfs.h"

#include <assert.h>
#include <stdio.h>

static void test_serial_distances(void)
{
    const Edge edges[] = {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {4, 4}};
    const int32_t expected[] = {0, 1, 1, 2, -1, -1};
    int32_t distance[6] = {99, 99, 99, 99, 99, 99};
    BFSConfig config = {4, BFS_SCHEDULE_STATIC};
    BFSMetrics metrics = {99};
    CSRGraph graph = {0};
    size_t i;

    assert(graph_from_edges(6, edges, 5, GRAPH_DIRECTED, &graph) == BFS_OK);
    for (config.schedule = BFS_SCHEDULE_STATIC;
         config.schedule <= BFS_SCHEDULE_GUIDED;
         config.schedule = (BFSSchedule)(config.schedule + 1)) {
        assert(bfs_serial(&graph, 0, distance, &config, &metrics) == BFS_OK);
        assert(metrics.threads_actual == 1);
        for (i = 0; i < 6; ++i) {
            assert(distance[i] == expected[i]);
        }
    }
    graph_free(&graph);
}

static void test_nonzero_source_and_isolates(void)
{
    const Edge edges[] = {{0, 1}, {1, 2}};
    const int32_t expected[] = {-1, -1, 0, -1};
    int32_t distance[4] = {0, 0, 0, 0};
    BFSConfig config = {1, BFS_SCHEDULE_STATIC};
    BFSMetrics metrics = {0};
    CSRGraph graph = {0};
    size_t i;

    assert(graph_from_edges(4, edges, 2, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 2, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 4; ++i) {
        assert(distance[i] == expected[i]);
    }
    graph_free(&graph);
}

static void test_small_graph_oracles(void)
{
    const Edge path_edges[] = {{0, 1}, {1, 2}, {2, 3}};
    const Edge star_edges[] = {{0, 1}, {0, 2}, {0, 3}};
    const Edge cycle_edges[] = {{0, 1}, {1, 2}, {2, 0}};
    const Edge one_edge[] = {{0, 1}};
    const int32_t path_expected[] = {0, 1, 2, 3};
    const int32_t star_expected[] = {0, 1, 1, 1};
    const int32_t cycle_expected[] = {0, 1, 2};
    const int32_t one_directed_expected[] = {-1, 0};
    const int32_t one_undirected_expected[] = {1, 0};
    const int32_t one_vertex_expected[] = {0};
    int32_t distance[4];
    BFSConfig config = {1, BFS_SCHEDULE_STATIC};
    BFSMetrics metrics = {0};
    CSRGraph graph = {0};
    size_t i;

    assert(graph_from_edges(4, path_edges, 3, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 4; ++i) assert(distance[i] == path_expected[i]);
    graph_free(&graph);

    assert(graph_from_edges(4, star_edges, 3, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 4; ++i) assert(distance[i] == star_expected[i]);
    graph_free(&graph);

    assert(graph_from_edges(3, cycle_edges, 3, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 3; ++i) assert(distance[i] == cycle_expected[i]);
    graph_free(&graph);

    assert(graph_from_edges(2, one_edge, 1, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 1, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 2; ++i) assert(distance[i] == one_directed_expected[i]);
    graph_free(&graph);

    assert(graph_from_edges(2, one_edge, 1, GRAPH_UNDIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 1, distance, &config, &metrics) == BFS_OK);
    for (i = 0; i < 2; ++i) assert(distance[i] == one_undirected_expected[i]);
    graph_free(&graph);

    assert(graph_from_edges(1, NULL, 0, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) == BFS_OK);
    assert(distance[0] == one_vertex_expected[0]);
    graph_free(&graph);
}

static void test_serial_errors(void)
{
    const Edge edge = {0, 1};
    int32_t distance[2] = {7, 7};
    BFSConfig config = {1, BFS_SCHEDULE_STATIC};
    BFSMetrics metrics = {42};
    CSRGraph graph = {0};

    assert(graph_from_edges(2, &edge, 1, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(bfs_serial(&graph, 2, distance, &config, &metrics) ==
           BFS_ERR_RANGE);
    assert(metrics.threads_actual == 0);
    assert(bfs_serial(&graph, 0, distance, &config, NULL) ==
           BFS_ERR_ARGUMENT);
    config.threads = 0;
    metrics.threads_actual = 42;
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) ==
           BFS_ERR_ARGUMENT);
    assert(metrics.threads_actual == 0);
    config.threads = 1;
    config.schedule = (BFSSchedule)99;
    metrics.threads_actual = 42;
    assert(bfs_serial(&graph, 0, distance, &config, &metrics) ==
           BFS_ERR_ARGUMENT);
    assert(metrics.threads_actual == 0);
    assert(bfs_serial(NULL, 0, distance, &config, &metrics) ==
           BFS_ERR_ARGUMENT);
    assert(bfs_serial(&graph, 0, NULL, &config, &metrics) ==
           BFS_ERR_ARGUMENT);
    assert(bfs_serial(&graph, 0, distance, NULL, &metrics) ==
           BFS_ERR_ARGUMENT);
    graph_free(&graph);
}

int main(void)
{
    test_serial_distances();
    test_nonzero_source_and_isolates();
    test_small_graph_oracles();
    test_serial_errors();
    puts("PASS: serial BFS tests");
    return 0;
}
