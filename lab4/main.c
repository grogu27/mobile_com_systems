#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>

#define N 5

#define PERIOD ((1 << N) - 1)
#define COUNT (PERIOD * 20)

int main(){
    
    uint8_t x1, x2, x3, x4, x5;
    uint8_t y1, y2, y3, y4, y5;
    x1 = 0b0; x2 = 0b1; x3 = 0b1; x4 = 0b1; x5 = 0b0;
    y1 = 0b1; y2 = 0b0; y3 = 0b1; y4 = 0b0; y5 = 0b1;
    uint8_t new_x1;
    uint8_t new_y1;

    uint8_t *res = malloc(sizeof(uint8_t) * COUNT);
    if (!res) { perror("malloc"); return 1; }
    printf("x: %d %d %d %d %d\n", x1, x2, x3, x4, x5);
    printf("y: %d %d %d %d %d\n", y1, y2, y3, y4, y5);
    int period = (1 << 5) - 1; // 31
    printf("Период сихропоследовательности: %d\n", PERIOD);
    int count = 0;
    for (int i = 0; i < COUNT; i++){
        res[i] = (x5 + y5) % 2;
        //res[i] = x5 ^ y5;
        new_x1 = (x5 + x4) % 2;
        //new_x1 = x5 ^ x4;
        x5 = x4;
        x4 = x3;
        x3 = x2;
        x2 = x1;
        x1 = new_x1;

        new_y1 = (y5 + y2) % 2;
        //new_y1 = y5 ^ y2;
        y5 = y4; 
        y4 = y3;
        y3 = y2;
        y2 = y1;
        y1 = new_y1;
        if (x1 == 0b0 && x2 == 0b1 && x3 == 0b1 && x4 == 0b1 && x5 == 0b0 && y1 == 1 && y2 == 0 && y3 == 1 && y4 == 0 && y5 == 1)
            printf("%d) Registers returned to initial state at step %d\n", ++count, i + 1);
    
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


// 14 -> 01110
// 21 -> 10101