/* Compile-only signature check: no BFS implementation or fake runtime result. */
#include "bfs.h"
typedef BFSStatus (*BFSFunction)(const CSRGraph *, uint32_t, int32_t *,
                                 const BFSConfig *, BFSMetrics *);
void check_api_signatures(void);
void check_api_signatures(void)
{
    BFSFunction functions[] = {bfs_serial, bfs_parallel_basic,
                               bfs_parallel_optimized};
    BFSMetrics metrics = {0};
    (void)functions;
    (void)metrics;
}
