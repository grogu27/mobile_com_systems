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
    printf("Период синхропоследовательности: %d\n", PERIOD);
    int count = 0;
    for (int i = 0; i < COUNT; i++){
        res[i] = (x5 + y5) % 2;
        new_x1 = (x5 + x4) % 2;
        x5 = x4;
        x4 = x3;
        x3 = x2;
        x2 = x1;
        x1 = new_x1;

        new_y1 = (y5 + y2) % 2;
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


    printf("=== ЗАДАНИЕ 2: Таблица автокорреляции ===\n");
    printf("%-6s | %-6s | %-6s | %-6s | %s\n", "Сдвиг", "бит 1", "бит 2", "бит 3", "Автокорреляция");
    printf("--------------------------------------------------\n");
    int idx;
    for (int shift = 0; shift < PERIOD; shift++) {
        double sum = 0;
        for (int i = 0; i < PERIOD; i++) {
            idx = (i + shift) % PERIOD;
            // Перевод битов 0/1 в уровни +1/-1 для корреляции
            double a = res[i] == 0 ? 1.0 : -1.0;
            double b = res[idx] == 1 ? -1.0 : 1.0;
            //sum += res[i] * res[idx];
            sum += a * b;
        }
        double corr = sum / (double)PERIOD;
        printf("%-6d | %-6d | %-6d | %-6d | %7.3f\n", 
               shift, res[shift], res[shift+1], res[shift+2], corr);
    }
    printf("\n");


      // ==========================================
    // ЗАДАНИЕ 3: Вторая последовательность (x+1, y-5)
    // ==========================================

    uint8_t x1_b, x2_b, x3_b, x4_b, x5_b;
    uint8_t y1_b, y2_b, y3_b, y4_b, y5_b;
    uint8_t new_x1_b;
    uint8_t new_y1_b;
    
    // Исходные данные для первой последовательности: 
    // x = 14 -> 0b01110, y = 21 -> 0b10101
    // Для второй последовательности: 
    // x_new = 14 + 1 = 15 -> 0b01111
    // y_new = 21 - 5 = 16 -> 0b10000
    
    //  15 (01111):
    x1_b = 0b0; x2_b = 0b1; x3_b = 0b1; x4_b = 0b1; x5_b = 0b1; 
    
    // 16 (10000):
    y1_b = 0b1; y2_b = 0b0; y3_b = 0b0; y4_b = 0b0; y5_b = 0b0; 
    
    uint8_t *res2 = malloc(sizeof(uint8_t) * COUNT*2);
    if (!res2) { perror("malloc"); return 1; }
    int count2 = 0;
    printf("=== ЗАДАНИЕ 3: Вторая последовательность (x+1, y-5) ===\n");
    printf("x_b: %d %d %d %d %d\n", x1_b, x2_b, x3_b, x4_b, x5_b);
    printf("y_b: %d %d %d %d %d\n", y1_b, y2_b, y3_b, y4_b, y5_b);
    for (int i = 0; i < COUNT*2; i++){
        res2[i] = (x5_b + y5_b) % 2;
        
        new_x1_b = (x5_b + x4_b) % 2;
        x5_b = x4_b;
        x4_b = x3_b;
        x3_b = x2_b;
        x2_b = x1_b;
        x1_b = new_x1_b;

        new_y1_b = (y5_b + y2_b) % 2;
        y5_b = y4_b; 
        y4_b = y3_b;
        y3_b = y2_b;
        y2_b = y1_b;
        y1_b = new_y1_b;
        if (x1_b == 0b0 && x2_b == 0b1 && x3_b == 0b1 && x4_b == 0b1 && x5_b == 0b1 && y1_b == 0b1 && y2_b == 0b0 && y3_b == 0b0 && y4_b == 0b0 && y5_b == 0b0)
            printf("%d) Registers returned to initial state at step %d\n", ++count2, i + 1);
    }
    for(int i=0; i<COUNT*2; i++) {
        printf("%b ", res2[i]);
        if((i+1) % PERIOD == 0) printf("\n");
    }
    printf("\n");

    // ==========================================
    // ЗАДАНИЕ 4: Взаимная корреляция
    // ==========================================
    printf("=== ЗАДАНИЕ 4: Взаимная корреляция ===\n");
    
    double cross_corr_sum = 0;
    for (int i = 0; i < PERIOD; i++) {
        // Перевод битов 0/1 в уровни +1/-1 для корреляции
        double val1 = res[i] == 0 ? 1.0 : -1.0;
        double val2 = res2[i] == 0 ? 1.0 : -1.0;
        cross_corr_sum += val1 * val2;
    }
    double cross_corr = cross_corr_sum / (double)PERIOD;
    
    printf("Значение взаимной корреляции: %.4f\n", cross_corr);

    free(res);
    free(res2);
    return 0;
}