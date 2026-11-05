#ifndef PBFS_GRAPH_H
#define PBFS_GRAPH_H

#include <stddef.h>
#include <stdint.h>
#include "status.h"

typedef struct { uint32_t src; uint32_t dst; } Edge;
typedef struct {
    uint32_t vertex_count;
    size_t edge_count; /* Stored CSR arcs, not input edge records. */
    size_t *row_offsets;
    uint32_t *col_indices;
} CSRGraph;

typedef enum { GRAPH_DIRECTED = 0, GRAPH_UNDIRECTED = 1 } GraphMode;

/* out must be zero-initialized; see docs/CONTRACT.md for ownership/errors. */
BFSStatus graph_from_edges(uint32_t vertex_count, const Edge *edges,
                           size_t input_edge_count, GraphMode mode,
                           CSRGraph *out);
BFSStatus graph_read_edge_list(const char *path, uint32_t vertex_count,
                              GraphMode mode, CSRGraph *out);
void graph_free(CSRGraph *graph);

#endif
