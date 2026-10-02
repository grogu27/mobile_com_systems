#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct __attribute__((packed)) {
    char     chunkID[4];     // Содержит "RIFF" (4 байта)
    uint32_t chunkSize;      // Размер файла минус 8 байт (4 байта)
    char     format[4];      // Содержит "WAVE" (4 байта)
    
    char     subchunk1ID[4]; // Содержит "fmt " (4 байта)
    uint32_t subchunk1Size;  // Размер подраздела, обычно 16 для PCM (4 байта)
    uint16_t audioFormat;    // Тип аудио, например 1 = PCM (2 байта)
    uint16_t numChannels;    // Количество каналов (1 = моно, 2 = стерео) (2 байта)
    uint32_t sampleRate;     // Частота дискретизации, например 44100 (4 байта)
    uint32_t byteRate;       // Скорость передачи данных (sampleRate * numChannels * bitsPerSample / 8) (4 байта)
    uint16_t blockAlign;     // (numChannels * bitsPerSample / 8) (2 байта)
    uint16_t bitsPerSample;  // Глубина цвета, например 16 бит (2 байта)
    
    char     subchunk2ID[4]; // Содержит "data" (4 байта)
    uint32_t subchunk2Size;  // Размер аудиоданных в байтах (4 байта)
} wav_header_t;



int main(){
    //10
    wav_header_t header = {0};
    
    FILE *fd = fopen("Моя_запись1.wav", "rb");
    if (!fd) {
        perror("fopen");
        return 1;
    }

    size_t n = fread(&header, 1, sizeof(header), fd);

    printf("sampleRate: %u Гц\n", header.sampleRate);

    double duration = (double)header.subchunk2Size / header.byteRate;
    printf("Duration %lf секунд\n", duration);

    uint32_t total_samples = header.subchunk2Size / header.blockAlign;
    printf("total_samples: %u\n", total_samples);

    double fs_calc = total_samples / duration;
    printf("sampleRate calc: %.2lf Гц\n", fs_calc);
    printf("size:  %u\n", header.chunkSize + 4 * 8);
    printf("chunkID:      '%.4s'\n", header.chunkID);
    printf("format:       '%.4s'\n", header.format);
    printf("subchunk1ID:  '%.4s'\n", header.subchunk1ID);
    printf("subchunk2ID:  '%.4s'\n", header.subchunk2ID);
    printf("audioFormat:  %u\n", header.audioFormat);
    printf("numChannels:  %u\n", header.numChannels);
    printf("bitsPerSample:%u\n", header.bitsPerSample);
    printf("blockAlign:   %u\n", header.blockAlign);
    printf("byteRate:     %u\n", header.byteRate);
    printf("subchunk2Size:%u\n", header.subchunk2Size);

    //fclose(fd);

    //11

    
    /* ---------- 11: создание файла с прореживанием в 3 раза ---------- */
    const int DECIM = 10;

    size_t frame_size = header.blockAlign;        
    size_t bytes_per_sample = header.bitsPerSample / 8; 

    uint32_t total_frames = header.subchunk2Size / frame_size;

    //printf("ftell: %ld\n", ftell(fd));
    uint8_t *data = malloc(header.subchunk2Size);
    if (!data) { perror("malloc"); fclose(fd); return 1; }

    if (fread(data, 1, header.subchunk2Size, fd) != header.subchunk2Size) {
        perror("fread data"); free(data); fclose(fd); return 1;
    }
    fclose(fd);

    /* сколько кадров останется после децимации */
    uint32_t new_total_frames = (total_frames + DECIM - 1) / DECIM;
    uint32_t new_data_size = new_total_frames * (uint32_t)frame_size;

    uint8_t *new_data = malloc(new_data_size);
    if (!new_data) 
    { perror("malloc"); 
        free(data); 
        return 1; 
    }

    /* берём каждый DECIM-й кадр */
    for (uint32_t i = 0, j = 0; i < total_frames; i += DECIM, ++j) {
        memcpy(new_data + (size_t)j * frame_size,
               data  + (size_t)i * frame_size,
               frame_size);
    }

    /* обновляем заголовок */
    wav_header_t new_header = header;
    new_header.sampleRate  = header.sampleRate / DECIM / 1;
        new_header.byteRate    = new_header.sampleRate *
                             new_header.numChannels *
                             new_header.bitsPerSample / 8;
    new_header.subchunk2Size = new_data_size;
    new_header.chunkSize     = new_header.subchunk2Size
                             + sizeof(wav_header_t) - 8;


    FILE *fd2 = fopen("Моя_запись1_11.wav", "w+b");
    if (!fd2) { perror("fopen out"); free(data); free(new_data); return 1; }

    fwrite(&new_header, 1, sizeof(new_header), fd2);
    fwrite(new_data,   1, new_data_size,       fd2);

    fclose(fd2);
    free(data);
    free(new_data);

    printf("\nНовый файл создан:\n");
    printf("  sampleRate    = %u\n", new_header.sampleRate);
    printf("  byteRate      = %u\n", new_header.byteRate);
    printf("  subchunk2Size = %u\n", new_header.subchunk2Size);
    printf("  total_frames  = %u\n", new_total_frames);
    printf("  size  = %u\n", new_header.chunkSize);


    //12













    // FILE *fd2 = fopen("Моя_запись1_copy.wav", "r+b");
    // if (!fd) {
    //     perror("fopen");
    //     return 1;
    // }
    // fseek(fd2, sizeof(wav_header_t), SEEK_SET);
    // char *buf = malloc(header.subchunk2Size);
    // if(!buf){
    //     perror("malloc");
    //     exit(1);
    // }
    
    // char *iter = buf;
    // int start = 16000;

    //free(buf);

    return 0;
}


