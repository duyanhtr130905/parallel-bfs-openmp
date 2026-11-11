#include "graph.h"

#include <assert.h>
#include <stdio.h>

static void test_directed_csr(void)
{
    const Edge edges[] = {{0, 1}, {0, 2}, {1, 2}};
    const size_t expected_offsets[] = {0, 2, 3, 3};
    const uint32_t expected_columns[] = {1, 2, 2};
    CSRGraph graph = {0};
    size_t i;

    assert(graph_from_edges(3, edges, 3, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(graph.vertex_count == 3);
    assert(graph.edge_count == 3);
    for (i = 0; i < 4; ++i) {
        assert(graph.row_offsets[i] == expected_offsets[i]);
    }
    for (i = 0; i < 3; ++i) {
        assert(graph.col_indices[i] == expected_columns[i]);
    }
    graph_free(&graph);
    graph_free(&graph);
}

static void test_undirected_edges(void)
{
    const Edge edges[] = {{0, 1}, {1, 1}, {0, 1}};
    CSRGraph graph = {0};

    assert(graph_from_edges(3, edges, 3, GRAPH_UNDIRECTED, &graph) == BFS_OK);
    assert(graph.edge_count == 5);
    assert(graph.row_offsets[0] == 0);
    assert(graph.row_offsets[1] == 2);
    assert(graph.row_offsets[2] == 5);
    assert(graph.row_offsets[3] == 5);
    graph_free(&graph);
}

static void test_invalid_arguments(void)
{
    const Edge edge = {0, 1};
    const Edge invalid_edge = {0, 2};
    CSRGraph graph = {0};

    assert(graph_from_edges(0, &edge, 1, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_RANGE);
    assert(graph_from_edges(2, &edge, 1, (GraphMode)99, &graph) ==
           BFS_ERR_ARGUMENT);
    assert(graph_from_edges(2, &edge, 1, GRAPH_DIRECTED, NULL) ==
           BFS_ERR_ARGUMENT);
    assert(graph_from_edges(2, NULL, 1, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_ARGUMENT);
    assert(graph_from_edges(2, &edge, 1, GRAPH_DIRECTED, &graph) ==
           BFS_OK);
    graph_free(&graph);
    assert(graph_from_edges(2, &invalid_edge, 1, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_RANGE);
}

static void test_edge_list_parser(void)
{
    const char *path = "build/test_graph_input.edgelist";
    FILE *file = fopen(path, "wb");
    CSRGraph graph = {0};

    assert(file != NULL);
    fputs("# comment\r\n\n 0 1\r\n0 2\n1 3\n2 3\n4 4", file);
    assert(fclose(file) == 0);

    assert(graph_read_edge_list(path, 6, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(graph.vertex_count == 6);
    assert(graph.edge_count == 5);
    graph_free(&graph);
    remove(path);
}

static void test_bad_edge_list(void)
{
    const char *path = "build/test_bad_graph_input.edgelist";
    FILE *file = fopen(path, "wb");
    CSRGraph graph = {0};

    assert(file != NULL);
    fputs("0 1 2\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 2, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_FORMAT);
    assert(graph.vertex_count == 0);
    assert(graph.row_offsets == NULL);
    remove(path);
}

static void test_empty_and_range_edge_lists(void)
{
    const char *path = "build/test_edge_list_errors.edgelist";
    FILE *file = fopen(path, "wb");
    CSRGraph graph = {0};

    assert(file != NULL);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) == BFS_OK);
    assert(graph.edge_count == 0);
    assert(graph.col_indices == NULL);
    assert(graph.row_offsets[0] == 0);
    assert(graph.row_offsets[3] == 0);
    graph_free(&graph);

    file = fopen(path, "wb");
    assert(file != NULL);
    fputs("0 3\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_RANGE);
    assert(graph.vertex_count == 0);

    file = fopen(path, "wb");
    assert(file != NULL);
    fputs("4294967296 0\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_RANGE);
    assert(graph.vertex_count == 0);

    file = fopen(path, "wb");
    assert(file != NULL);
    fputs("0 1 # trailing comment\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_FORMAT);
    assert(graph.vertex_count == 0);

    file = fopen(path, "wb");
    assert(file != NULL);
    fputs("-1 0\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_FORMAT);
    assert(graph.vertex_count == 0);

    file = fopen(path, "wb");
    assert(file != NULL);
    fputs("\xEF\xBB\xBF" "0 1\n", file);
    assert(fclose(file) == 0);
    assert(graph_read_edge_list(path, 3, GRAPH_DIRECTED, &graph) ==
           BFS_ERR_FORMAT);
    assert(graph.vertex_count == 0);
    remove(path);
}

int main(void)
{
    test_directed_csr();
    test_undirected_edges();
    test_invalid_arguments();
    test_edge_list_parser();
    test_bad_edge_list();
    test_empty_and_range_edge_lists();
    puts("PASS: graph CSR/parser tests");
    return 0;
}
