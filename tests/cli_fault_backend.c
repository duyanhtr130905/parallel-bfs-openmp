/* Test-only fault injection. NEVER linked into the production BFS binary. */
#include "../src/main.c"

static BFSStatus injected(const CSRGraph *g, uint32_t s, int32_t *d,
                           const BFSConfig *c, BFSMetrics *m)
{
    const char *fault = getenv("BFS_TEST_FAULT");
    (void)c;
    m->threads_actual = 0;
    if (!fault) return BFS_ERR_ARGUMENT;
    if (!strcmp(fault, "memory")) return BFS_ERR_MEMORY;
    if (!strcmp(fault, "runtime")) return BFS_ERR_RUNTIME;
    if (!strcmp(fault, "unimplemented")) return BFS_ERR_NOT_IMPLEMENTED;
    for (uint32_t i = 0; i < g->vertex_count; ++i) d[i] = -1;
    d[s] = 0; /* Incorrect for the nonempty connected fixture. */
    if (strcmp(fault, "metrics") != 0) m->threads_actual = 1;
    return BFS_OK;
}

BFSStatus bfs_serial(const CSRGraph *g, uint32_t s, int32_t *d,
                     const BFSConfig *c, BFSMetrics *m) { return injected(g,s,d,c,m); }
BFSStatus bfs_parallel_basic(const CSRGraph *g, uint32_t s, int32_t *d,
                             const BFSConfig *c, BFSMetrics *m) { return injected(g,s,d,c,m); }
BFSStatus bfs_parallel_optimized(const CSRGraph *g, uint32_t s, int32_t *d,
                                 const BFSConfig *c, BFSMetrics *m) { return injected(g,s,d,c,m); }
