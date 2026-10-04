#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct __attribute__((packed)) {
    char     chunkID[4];
    uint32_t chunkSize;
    char     format[4];

    char     subchunk1ID[4];
    uint32_t subchunk1Size;
    uint16_t audioFormat;
    uint16_t numChannels;
    uint32_t sampleRate;
    uint32_t byteRate;
    uint16_t blockAlign;
    uint16_t bitsPerSample;

    char     subchunk2ID[4];
    uint32_t subchunk2Size;
} wav_header_t;


/* Линейная интерполяция int16-сигнала к new_len отсчётам.
   signal — массив int16 длиной old_len,
   возвращает новый массив int16 длиной new_len (malloc). */
int16_t *resample_linear_int16(const int16_t *signal,
                               size_t old_len,
                               size_t new_len)
{
    int16_t *out = malloc(new_len * sizeof(int16_t));
    if (!out) return NULL;

    if (new_len == 1) {
        out[0] = signal[0];
        return out;
    }
    if (old_len == 1) {
        for (size_t i = 0; i < new_len; ++i) out[i] = signal[0];
        return out;
    }

    double step = (double)(old_len - 1) / (double)(new_len - 1);

    for (size_t i = 0; i < new_len; ++i) {
        double pos = i * step;
        size_t i0 = (size_t)pos;
        size_t i1 = (i0 + 1 < old_len) ? i0 + 1 : i0;
        double t  = pos - i0;

        double v = (1.0 - t) * signal[i0] + t * signal[i1];
        if (v >  32767.0) v =  32767.0;
        if (v < -32768.0) v = -32768.0;
        out[i] = (int16_t)(v >= 0 ? v + 0.5 : v - 0.5);
    }
    return out;
}


int main(void)
{
    FILE *fd = fopen("Моя_запись1.wav", "rb");
    if (!fd) { perror("fopen"); return 1; }

    wav_header_t header;
    if (fread(&header, 1, sizeof(header), fd) != sizeof(header)) {
        perror("fread header"); fclose(fd); return 1;
    }

    if (header.bitsPerSample != 16 || header.numChannels != 1) {
        fprintf(stderr, "Ожидается моно 16 бит\n");
        fclose(fd); return 1;
    }

    /* читаем все сэмплы как int16 */
    size_t n_samples = header.subchunk2Size / 2;
    int16_t *samples = malloc(n_samples * sizeof(int16_t));
    if (!samples) { perror("malloc"); fclose(fd); return 1; }

    if (fread(samples, 2, n_samples, fd) != n_samples) {
        perror("fread data"); free(samples); fclose(fd); return 1;
    }
    fclose(fd);

    /* ---------- писклявый голос: децимация + интерполяция ---------- */
    const int K = 2;   /* во сколько раз повышаем тон */

    size_t decim_len = (n_samples + K - 1) / K;
    int16_t *decim = malloc(decim_len * sizeof(int16_t));
    if (!decim) { perror("malloc"); free(samples); return 1; }

    for (size_t i = 0, j = 0; i < n_samples; i += K, ++j) {
        decim[j] = samples[i];
    }

    /* растягиваем обратно к исходной длине */
    int16_t *out = resample_linear_int16(decim, decim_len, n_samples);
    if (!out) { perror("malloc"); free(samples); free(decim); return 1; }

    /* ---------- формируем новый WAV ---------- */
    wav_header_t new_header = header;
    new_header.sampleRate    = header.sampleRate;   /* НЕ меняем! */
    new_header.byteRate      = new_header.sampleRate *
                               new_header.numChannels *
                               new_header.bitsPerSample / 8;
    new_header.subchunk2Size = (uint32_t)(n_samples * 2);
    new_header.chunkSize     = new_header.subchunk2Size
                             + sizeof(wav_header_t) - 8;

    FILE *fd2 = fopen("Моя_запись1_chipmunk.wav", "w+b");
    if (!fd2) { perror("fopen out"); free(samples); free(decim); free(out); return 1; }

    fwrite(&new_header, 1, sizeof(new_header), fd2);
    fwrite(out,         1, new_header.subchunk2Size, fd2);

    fclose(fd2);
    free(samples);
    free(decim);
    free(out);

    printf("Готово: Моя_запись1_chipmunk.wav\n");
    printf("  тон повышен в %d раз, длительность сохранена (%.3f с)\n",
           K, (double)n_samples / header.sampleRate);
    return 0;
}