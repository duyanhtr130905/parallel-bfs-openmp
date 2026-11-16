/* Test the private caller validator without changing the public API. */
#define main cli_entry_for_test
#include "../src/main.c"
#undef main
#include <assert.h>

int main(void)
{
    CSRGraph g = {0};
    BFSConfig config = {4, BFS_SCHEDULE_GUIDED};
    BFSMetrics metrics = {0};
    int32_t d[6];
    const int32_t expected[] = {0, 1, 1, 2, -1, -1};
    unsigned char witness[6] = {0};
    size_t reached, i;
    assert(graph_read_edge_list("datasets/small/disconnected.edgelist", 6,
                               GRAPH_DIRECTED, &g) == BFS_OK);
    assert(bfs_serial(&g, 0, d, &config, &metrics) == BFS_OK);
    for (i = 0; i < 6; ++i) assert(d[i] == expected[i]);
    assert(validate_distances(&g, 0, d, witness, &reached) && reached == 4);
    for (i = 0; i < 6; ++i) {
        int32_t saved = d[i];
        d[i] = i == 0 ? 1 : 0;
        memset(witness, 0, sizeof(witness));
        assert(!validate_distances(&g, 0, d, witness, &reached));
        d[i] = saved;
    }
    d[3] = -1; /* An edge from a reached vertex cannot end at unreachable. */
    memset(witness, 0, sizeof(witness));
    assert(!validate_distances(&g, 0, d, witness, &reached));
    d[3] = 1; /* No predecessor at level zero exists for vertex 3. */
    memset(witness, 0, sizeof(witness));
    assert(!validate_distances(&g, 0, d, witness, &reached));
    d[3] = 2;
    d[4] = 2; /* A disconnected self-loop must not certify reachability. */
    memset(witness, 0, sizeof(witness));
    assert(!validate_distances(&g, 0, d, witness, &reached));
    graph_free(&g);
    puts("PASS: loader-to-serial full-distance oracle and caller validation");
    return 0;
}
