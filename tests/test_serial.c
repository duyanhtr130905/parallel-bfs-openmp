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
           BFS_ERR_RANGE);
    assert(metrics.threads_actual == 0);
    graph_free(&graph);
}

int main(void)
{
    test_serial_distances();
    test_nonzero_source_and_isolates();
    test_serial_errors();
    puts("PASS: serial BFS tests");
    return 0;
}
