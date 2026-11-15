#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#define N 4
#define PERIOD ((1 << N) - 1)
#define COUNT (PERIOD * 19)

int main(){
    
    uint8_t x1, x2, x3, x4;
    x1 = 0b1; x2 = 0b0; x3 = 0b0; x4 = 0b0;
    uint8_t new_x1;
    uint8_t new_y1;

    uint8_t *res = malloc(sizeof(uint8_t) * COUNT);
    if (!res) { perror("malloc"); return 1; }
    printf("x: %d %d %d %d\n", x1, x2, x3, x4);
    int count = 0;
    printf("Период сихропоследовательности: %d\n", PERIOD);
    for (int i = 0; i < COUNT; i++){
        res[i] = x4;
        new_x1 = (x4 + x3) % 2;
        
        x4 = x3;
        x3 = x2;
        x2 = x1;
        x1 = new_x1;


    if (x1 == 1 && x2 == 0 && x3 == 0 && x4 == 0)
        printf("%d) Register returned to initial state at step %d\n", ++count, i + 1);
    }
    int k = 1;
    for (size_t i = 0; i < COUNT; i++)
    {
        printf("%b ", res[i]);
        if(k == PERIOD){
            printf("\n");
            k = 0;
        }
            
        k++;

    }
    printf("\n");
    free(res);
    return 0;
}


