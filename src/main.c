/* Bootstrap CLI only. No graph loader or BFS implementation is linked. */
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "bfs.h"

static int number(const char *s, uintmax_t limit, uintmax_t *out)
{
    const unsigned char *p = (const unsigned char *)s;
    char *end;
    uintmax_t value;
    if (*p == 0) return 0;
    for (; *p; ++p) if (*p < '0' || *p > '9') return 0;
    errno = 0;
    value = strtoumax(s, &end, 10);
    if (errno == ERANGE || *end || value > limit) return 0;
    *out = value;
    return 1;
}

static int usage_error(void)
{
    fputs("Invalid arguments. Use --help.\n", stderr);
    return 2;
}

int main(int argc, char **argv)
{
    const char *names[] = {"--graph", "--vertices", "--source", "--algo",
                           "--threads", "--schedule", "--directed", "--undirected"};
    unsigned seen = 0;
    uintmax_t n = 0, source = 0, threads = 1;
    BFSConfig config = {1, BFS_SCHEDULE_STATIC};
    const char *graph = NULL;
    int i;
    if (argc == 2 && strcmp(argv[1], "--help") == 0) {
        puts("Usage: bfs --graph PATH --vertices N --source S\n"
             "  --algo serial|omp-basic|omp-opt [--threads P]\n"
             "  [--schedule static|dynamic|guided] (--directed|--undirected)\n"
             "BOOTSTRAP: graph and BFS modules are not implemented.");
        return 0;
    }
    for (i = 1; i < argc; ++i) {
        int k;
        const char *value;
        for (k = 0; k < 8; ++k) if (strcmp(argv[i], names[k]) == 0) break;
        if (k == 8 || (seen & (1u << k))) return usage_error();
        seen |= 1u << k;
        if (k >= 6) continue;
        if (++i >= argc || strncmp(argv[i], "--", 2) == 0) return usage_error();
        value = argv[i];
        switch (k) {
        case 0: if (!*value) return usage_error(); graph = value; break;
        case 1: if (!number(value, INT32_MAX, &n) || n == 0) return usage_error(); break;
        case 2: if (!number(value, UINT32_MAX, &source)) return usage_error(); break;
        case 3:
            if (strcmp(value, "serial") && strcmp(value, "omp-basic") &&
                strcmp(value, "omp-opt")) return usage_error();
            break;
        case 4:
            if (!number(value, INT_MAX, &threads) || threads == 0) return usage_error();
            config.threads = (int)threads;
            break;
        case 5:
            if (!strcmp(value, "static")) config.schedule = BFS_SCHEDULE_STATIC;
            else if (!strcmp(value, "dynamic")) config.schedule = BFS_SCHEDULE_DYNAMIC;
            else if (!strcmp(value, "guided")) config.schedule = BFS_SCHEDULE_GUIDED;
            else return usage_error();
            break;
        default: return usage_error();
        }
    }
    if ((seen & 15u) != 15u || source >= n ||
        ((seen >> 6) & 3u) == 0 || ((seen >> 6) & 3u) == 3u) return usage_error();
    (void)graph;
    (void)config;
    fputs("BFS_ERR_NOT_IMPLEMENTED: graph/BFS execution modules are absent; "
          "no benchmark was run.\n", stderr);
    return 3;
}
