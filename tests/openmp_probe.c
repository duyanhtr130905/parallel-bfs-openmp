#include <omp.h>
#include <stdio.h>
#include <string.h>
#ifndef _OPENMP
#error OpenMP support is required
#endif

int main(int argc, char **argv)
{
    int strict = 1;
    int team = 0;
    int count = 0;
    if (argc == 2 && strcmp(argv[1], "--basic") == 0) {
        strict = 0;
    } else if (!(argc == 1 ||
                 (argc == 2 && strcmp(argv[1], "--strict") == 0))) {
        fprintf(stderr, "usage: openmp_probe [--strict|--basic]\n");
        return 2;
    }
    omp_set_dynamic(0);
    #pragma omp parallel num_threads(2) reduction(+:count) shared(team)
    {
        #pragma omp single
        team = omp_get_num_threads();
        count += 1;
    }
    printf("OpenMP=%d team=%d participants=%d mode=%s\n", _OPENMP, team,
           count, strict ? "strict" : "basic");
    if (team < 1 || count != team || (strict && team != 2)) {
        fprintf(stderr, "OpenMP team requirement not met\n");
        return 1;
    }
    return 0;
}
