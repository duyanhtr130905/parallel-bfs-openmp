#ifndef PBFS_STATUS_H
#define PBFS_STATUS_H

typedef enum {
    BFS_OK = 0,
    BFS_ERR_ARGUMENT = 1,
    BFS_ERR_RANGE = 2,
    BFS_ERR_MEMORY = 3,
    BFS_ERR_IO = 4,
    BFS_ERR_FORMAT = 5,
    BFS_ERR_NOT_IMPLEMENTED = 6,
    BFS_ERR_RUNTIME = 7
} BFSStatus;

#endif
