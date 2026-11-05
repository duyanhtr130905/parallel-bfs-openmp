#include <omp.h>
#include <stdio.h>
#ifndef _OPENMP
#error OpenMP support is required
#endif
int main(void)
{
    int count = 0;
    double start = omp_get_wtime();
    #pragma omp parallel num_threads(2) reduction(+:count)
    count += 1;
    printf("OpenMP=%d team=%d wall_seconds=%.9f\n", _OPENMP, count,
           omp_get_wtime() - start);
    return count >= 1 ? 0 : 1;
}
