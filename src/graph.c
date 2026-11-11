#include "graph.h"

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int size_mul_overflow(size_t left, size_t right, size_t *result)
{
    if (right != 0 && left > SIZE_MAX / right) {
        return 1;
    }
    *result = left * right;
    return 0;
}

static int size_add_overflow(size_t left, size_t right, size_t *result)
{
    if (left > SIZE_MAX - right) {
        return 1;
    }
    *result = left + right;
    return 0;
}

static int valid_mode(GraphMode mode)
{
    return mode == GRAPH_DIRECTED || mode == GRAPH_UNDIRECTED;
}

// Role A: giải phóng an toàn hai buffer do CSR builder sở hữu.
// Sau khi gọi, graph trở về trạng thái zero để có thể free lặp lại.
void graph_free(CSRGraph *graph)
{
    if (graph == NULL) {
        return;
    }

    free(graph->row_offsets);
    free(graph->col_indices);
    *graph = (CSRGraph){0};
}

BFSStatus graph_from_edges(uint32_t vertex_count, const Edge *edges,
                           size_t input_edge_count, GraphMode mode,
                           CSRGraph *out)
{
    // Role A: chuyển edge-list trong bộ nhớ sang biểu diễn CSR bất biến.
    // Chỉ gán vào out sau khi toàn bộ quá trình xây dựng thành công.
    CSRGraph result = {0};
    size_t stored_edges = 0;
    size_t offset_count;
    size_t i;
    size_t *cursor = NULL;

    if (out == NULL || !valid_mode(mode)) {
        return BFS_ERR_ARGUMENT;
    }
    if (vertex_count == 0 || vertex_count > INT32_MAX) {
        return BFS_ERR_RANGE;
    }
    if (input_edge_count != 0 && edges == NULL) {
        return BFS_ERR_ARGUMENT;
    }
    if (size_add_overflow((size_t)vertex_count, 1, &offset_count) ||
        size_mul_overflow(offset_count, sizeof(*result.row_offsets), &i)) {
        return BFS_ERR_RANGE;
    }

    // Kiểm tra ID và đếm số cung thật sự lưu trong CSR.
    // Đồ thị vô hướng nhân đôi cạnh thường, nhưng không nhân đôi self-loop.
    for (i = 0; i < input_edge_count; ++i) {
        size_t contribution = 1;
        if (edges[i].src >= vertex_count || edges[i].dst >= vertex_count) {
            return BFS_ERR_RANGE;
        }
        if (mode == GRAPH_UNDIRECTED && edges[i].src != edges[i].dst) {
            contribution = 2;
        }
        if (size_add_overflow(stored_edges, contribution, &stored_edges)) {
            return BFS_ERR_RANGE;
        }
    }

    result.row_offsets = calloc(offset_count, sizeof(*result.row_offsets));
    if (result.row_offsets == NULL) {
        return BFS_ERR_MEMORY;
    }
    if (stored_edges != 0) {
        size_t bytes;
        if (size_mul_overflow(stored_edges, sizeof(*result.col_indices),
                              &bytes)) {
            graph_free(&result);
            return BFS_ERR_RANGE;
        }
        result.col_indices = malloc(bytes);
        if (result.col_indices == NULL) {
            graph_free(&result);
            return BFS_ERR_MEMORY;
        }
    }

    // Bước 1 của CSR: đếm số láng giềng của từng đỉnh.
    for (i = 0; i < input_edge_count; ++i) {
        ++result.row_offsets[edges[i].src + 1U];
        if (mode == GRAPH_UNDIRECTED && edges[i].src != edges[i].dst) {
            ++result.row_offsets[edges[i].dst + 1U];
        }
    }
    // Bước 2 của CSR: prefix sum tạo khoảng [row_offsets[u], row_offsets[u+1]).
    for (i = 1; i < offset_count; ++i) {
        result.row_offsets[i] += result.row_offsets[i - 1];
    }

    if (size_mul_overflow((size_t)vertex_count, sizeof(*cursor), &i)) {
        graph_free(&result);
        return BFS_ERR_RANGE;
    }
    cursor = malloc(i);
    if (cursor == NULL) {
        graph_free(&result);
        return BFS_ERR_MEMORY;
    }
    for (i = 0; i < (size_t)vertex_count; ++i) {
        cursor[i] = result.row_offsets[i];
    }
    // Bước 3 của CSR: điền các đỉnh kề vào col_indices theo từng hàng.
    for (i = 0; i < input_edge_count; ++i) {
        result.col_indices[cursor[edges[i].src]++] = edges[i].dst;
        if (mode == GRAPH_UNDIRECTED && edges[i].src != edges[i].dst) {
            result.col_indices[cursor[edges[i].dst]++] = edges[i].src;
        }
    }
    free(cursor);

    result.vertex_count = vertex_count;
    result.edge_count = stored_edges;
    *out = result;
    return BFS_OK;
}

static int line_space(int character)
{
    return character == ' ' || character == '\t';
}

static BFSStatus parse_uint32_token(const char **input, uint32_t *value)
{
    // Parser Role A chỉ chấp nhận chữ số thập phân không dấu.
    // Sai lexical là FORMAT; số hợp lệ về dạng nhưng vượt uint32_t là RANGE.
    const unsigned char *cursor = (const unsigned char *)*input;
    uintmax_t parsed = 0;
    size_t digits = 0;

    while (*cursor >= '0' && *cursor <= '9') {
        uintmax_t digit = (uintmax_t)(*cursor - (unsigned char)'0');
        if (parsed > (UINT32_MAX - digit) / 10U) {
            return BFS_ERR_RANGE;
        }
        parsed = parsed * 10U + digit;
        ++cursor;
        ++digits;
    }
    if (digits == 0) {
        return BFS_ERR_FORMAT;
    }
    *value = (uint32_t)parsed;
    *input = (const char *)cursor;
    return BFS_OK;
}

static BFSStatus parse_edge_line(const char *line, Edge *edge, int *is_comment)
{
    // Mỗi dòng hợp lệ có đúng hai token: src dst.
    // Dòng trống và comment toàn dòng được bỏ qua; comment cuối dòng không hợp lệ.
    const char *cursor = line;
    *is_comment = 0;

    while (line_space((unsigned char)*cursor)) {
        ++cursor;
    }
    if (*cursor == '\0') {
        *is_comment = 1;
        return BFS_OK;
    }
    if (*cursor == '#') {
        *is_comment = 1;
        return BFS_OK;
    }
    {
        BFSStatus status = parse_uint32_token(&cursor, &edge->src);
        if (status != BFS_OK) {
            return status;
        }
    }
    if (!line_space((unsigned char)*cursor)) {
        return BFS_ERR_FORMAT;
    }
    while (line_space((unsigned char)*cursor)) {
        ++cursor;
    }
    {
        BFSStatus status = parse_uint32_token(&cursor, &edge->dst);
        if (status != BFS_OK) {
            return status;
        }
    }
    while (line_space((unsigned char)*cursor)) {
        ++cursor;
    }
    return *cursor == '\0' ? BFS_OK : BFS_ERR_FORMAT;
}

static BFSStatus read_line(FILE *file, char **line, size_t *capacity)
{
    // Đọc động để không cắt ngắn dòng hợp lệ; EOF sau dòng cuối không cần newline.
    size_t length = 0;
    int character;

    for (;;) {
        character = fgetc(file);
        if (character == EOF) {
            if (ferror(file)) {
                return BFS_ERR_IO;
            }
            if (length == 0) {
                return BFS_ERR_NOT_IMPLEMENTED;
            }
            break;
        }
        if (character == '\0') {
            // NUL là byte dữ liệu bất hợp lệ trong edge-list; không để nó
            // trở thành terminator và làm phần còn lại của dòng bị bỏ qua.
            return BFS_ERR_FORMAT;
        }
        if (length >= SIZE_MAX - 1 || length + 1 >= *capacity) {
            size_t new_capacity;
            char *new_line;
            if (size_add_overflow(*capacity, *capacity, &new_capacity)) {
                return BFS_ERR_RANGE;
            }
            new_line = realloc(*line, new_capacity);
            if (new_line == NULL) {
                return BFS_ERR_MEMORY;
            }
            *line = new_line;
            *capacity = new_capacity;
        }
        if (character == '\n') {
            break;
        }
        (*line)[length++] = (char)character;
    }
    (*line)[length] = '\0';
    if (length != 0 && (*line)[length - 1] == '\r') {
        (*line)[length - 1] = '\0';
    }
    return BFS_OK;
}

BFSStatus graph_read_edge_list(const char *path, uint32_t vertex_count,
                               GraphMode mode, CSRGraph *out)
{
    // Role A: đọc edge-list từ file, kiểm tra grammar/range,
    // sau đó dùng chung graph_from_edges để tạo CSR.
    FILE *file;
    char *line = NULL;
    size_t capacity = 256;
    Edge *edges = NULL;
    size_t edge_count = 0;
    size_t edge_capacity = 0;
    BFSStatus status = BFS_OK;

    if (out == NULL || path == NULL || path[0] == '\0' ||
        !valid_mode(mode)) {
        return BFS_ERR_ARGUMENT;
    }
    if (vertex_count == 0 || vertex_count > INT32_MAX) {
        return BFS_ERR_RANGE;
    }
    file = fopen(path, "rb");
    if (file == NULL) {
        return BFS_ERR_IO;
    }
    line = malloc(capacity);
    if (line == NULL) {
        fclose(file);
        return BFS_ERR_MEMORY;
    }

    for (;;) {
        Edge edge;
        int is_comment;
        status = read_line(file, &line, &capacity);
        if (status == BFS_ERR_NOT_IMPLEMENTED) {
            status = BFS_OK;
            break;
        }
        if (status != BFS_OK) {
            break;
        }
        status = parse_edge_line(line, &edge, &is_comment);
        if (status != BFS_OK) {
            break;
        }
        if (is_comment || line[0] == '\0') {
            continue;
        }
        if (edge.src >= vertex_count || edge.dst >= vertex_count) {
            status = BFS_ERR_RANGE;
            break;
        }
        if (edge_count == edge_capacity) {
            size_t new_capacity = edge_capacity == 0 ? 16 : edge_capacity * 2;
            size_t bytes;
            Edge *new_edges;
            if (new_capacity < edge_capacity ||
                size_mul_overflow(new_capacity, sizeof(*edges), &bytes)) {
                status = BFS_ERR_RANGE;
                break;
            }
            new_edges = realloc(edges, bytes);
            if (new_edges == NULL) {
                status = BFS_ERR_MEMORY;
                break;
            }
            edges = new_edges;
            edge_capacity = new_capacity;
        }
        edges[edge_count++] = edge;
    }

    if (fclose(file) != 0 && status == BFS_OK) {
        status = BFS_ERR_IO;
    }
    free(line);
    if (status != BFS_OK) {
        free(edges);
        return status;
    }

    status = graph_from_edges(vertex_count, edges, edge_count, mode, out);
    free(edges);
    return status;
}
