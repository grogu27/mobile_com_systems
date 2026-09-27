#include <stdio.h>
#include <stdint.h>

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
    fclose(fd);
}


