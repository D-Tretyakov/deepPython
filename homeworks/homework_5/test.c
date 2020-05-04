#include <stdio.h>
#include <string.h>

void dot_product(long *a1, long *a2, long *res, int i_size_1, int j_size_1, int i_size_2, int j_size_2) {
    for (int i = 0; i < i_size_1; i++) {
        for (int j = 0; j < j_size_2; j++) {
            res[i * (j_size_1) + j] = 0;
            for (int k = 0; k < i_size_2; k++) {
                 res[i * (j_size_2) + j] += a1[i * (j_size_1) + k] * a2[k * (j_size_2) + j];
            }
        }
    }
}

int main(void) {
    long a1[] = {1, 2, 3, 4};
    long a2[] = {5, 6, 0, 7};
    long res[4];

    dot_product(a1, a2, res, 2, 2, 2, 2);
    for(int i = 0; i < 4; i++) {
            res[i] *= 10;
            printf("%ld ", res[i]);
    }
    printf("%f", (float) 5 / (long)2);
    return 0;
}