#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include <math.h>

#define N 4
#define PERIOD ((1 << N) - 1)
#define COUNT (PERIOD * 19)

struct checker{
    int first_pr;
    int second_pr;
    int third_pr;
};

int check_mseq(uint8_t *seq, int len, struct checker *ch){
    //1
    printf("Period: %d\n", len);
    int count_zeros = 0;
    int count_ones = 0;
    for(int i = 0; i < len; i++){
        if (seq[i] == 0b0) count_zeros++;
        if (seq[i] == 0b1) count_ones++;
    }
    int res = abs(count_ones - count_zeros);
    if (res == 1 || res == 0)
        ch->first_pr = 1;
    else
        ch->first_pr = 0;   
    printf("Количество единиц: %d\tКоличество нулей: %d\n", count_ones, count_zeros);
    //2
    int runs[10] = {0};
    //int len_1 = 0; int len_2 = 0; int len_3 = 0; int len_4 = 0; int len_5 = 0;
    int current_len = 1;
    for (int i = 0; i < len; i++){
        int next_id = (i + 1) % len;
        if(seq[i] == seq[next_id])
            current_len++;
        else{
            // if(current_len == 1) len_1++;
            // else if (current_len == 2) len_2 ++;
            // else if (current_len == 3) len_3 ++;
            // else if (current_len == 4) len_4++;
            // else if (current_len == 5) len_5++;
            runs[current_len-1]++;
            current_len = 1;

        }
    }   
    //int count_series = len_1 + len_2 + len_3 + len_4 + len_5;
    int count_series = runs[0] + runs[1] + runs[2] + runs[3] + runs[4] + runs[5] + runs[6] + runs[7] + runs[8] + runs[9]; 
    //printf("Количество серий: %d\n", count_series);
    if(count_series == 0)
        ch->second_pr = 0;
    else if ((runs[0] > ((count_series / 2) - 2)) && (runs[0] < ((count_series / 2) + 2 ))  && (runs[1] > ((count_series / 4) - 2)) && (runs[1] < ((count_series / 4) + 2 )) && (runs[2] > ((count_series / 8) - 2) && (runs[2] < ((count_series / 8) + 2)))  && (runs[3] > ((count_series / 16) - 2) && (runs[3] < ((count_series / 16) + 2)))  && (runs[4] > ((count_series / 32) - 2) && (runs[4] < ((count_series / 32) + 2)))            ){
        ch->second_pr = 1;
    }
    else
        ch->second_pr = 0;
    
    printf("Количество циклов с длинной 1: %d\nКоличество циклов с длинной 2: %d\nКоличество циклов с длинной 3: %d\nКоличество циклов с длинной 4: %d\nКоличество циклов с длинной 5: %d\n",runs[0], runs[1], runs[2], runs[3], runs[4] );
    
    //3
    int idx2;
    int is_good_corr = 1; // Флаг: 1 - корреляция хорошая, 0 - плохая
    double ideal_val = -1.0 / PERIOD; // Идеальное значение для M-последовательности

    for (int shift = 0; shift < PERIOD; shift++) { 
        double sum = 0;
        for (int i = 0; i < PERIOD; i++) {
            idx2 = (i + shift) % PERIOD;
            double a = seq[i] == 0 ? 1.0 : -1.0;
            double b = seq[idx2] == 0 ? 1.0 : -1.0;
            sum += a * b;
        }
        double corr = sum / (double)PERIOD; //  Значение для текущего сдвига
        printf("Сдвиг %d: %lf\n", shift, corr); 
        
        if (fabs(corr - ideal_val) > 0.1 && shift != 0) {
            is_good_corr = 0;
            break; 
        }
    }

    if (is_good_corr) {
        ch->third_pr = 1;
    } else {
        ch->third_pr = 0;
    }
}



int main(){
    
    uint8_t x1, x2, x3, x4;
    //x1 = 0b0; x2 = 0b0; x3 = 0b0; x4 = 0b0;
    x1 = 0b0; x2 = 0b1; x3 = 0b1; x4 = 0b0;

    uint8_t new_x1;
    uint8_t new_y1;
    int true_period = 0;
    int k = 0;
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


    if (x1 == 1 && x2 == 0 && x3 == 0 && x4 == 0){
        k ++;
                printf("%d) Register returned to initial state at step %d\n", ++count, i + 1);
                if(k == 1)
                    true_period = i + 1;
    }
    }
    int k2 = 1;
    for (size_t i = 0; i < COUNT; i++)
    {
        printf("%b ", res[i]);
        if(k2 == PERIOD){
            printf("\n");
            k2 = 0;
        }
            
        k2++;

    }
    printf("\n");


    ////--------------------
    printf("======================checker===============\n");
    struct checker ch;

    check_mseq(res, PERIOD, &ch);

    if(ch.first_pr == 1 && ch.second_pr == 1 && ch.third_pr == 1){
        printf("Последовательность соответсвует свойствам: 1: %d\t 2: %d\t 3: %d\n", ch.first_pr, ch.second_pr, ch.third_pr);
    }
    else{
        printf("Последовательность не соответсвует свойствам: 1: %d\t 2: %d\t 3: %d\n", ch.first_pr, ch.second_pr, ch.third_pr);

    }
    free(res);
    return 0;
}


