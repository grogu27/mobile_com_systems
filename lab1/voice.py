import numpy as np
import matplotlib.pyplot as plt
import wave


# ============================================================
# ФУНКЦИЯ ЧТЕНИЯ WAV
# ============================================================

def read_wav(filename):
    with wave.open(filename, 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        n_frames = wav.getnframes()

        raw_data = wav.readframes(n_frames)

    # Определяем тип данных по глубине звука
    if sample_width == 1:
        data = np.frombuffer(raw_data, dtype=np.uint8)
        data = data.astype(np.float64) - 128  #128 соответствует нулю сигнала.

    elif sample_width == 2:
        data = np.frombuffer(raw_data, dtype=np.int16)
        data = data.astype(np.float64)

    elif sample_width == 4:
        data = np.frombuffer(raw_data, dtype=np.int32)
        data = data.astype(np.float64)

    else:
        raise ValueError(
            f"Неподдерживаемая глубина звука: {sample_width * 8} бит"
        )

    # Если стерео — преобразуем в моно
    if n_channels > 1:
        data = data.reshape(-1, n_channels)
        data = np.mean(data, axis=1)
    
    return data, sample_rate


# ============================================================
# ДПФ
# ============================================================

def calculate_dft(signal, sample_rate):
    N = len(signal)

    # Убираем постоянную составляющую
    signal = signal - np.mean(signal)

    # ДПФ
    X = np.fft.fft(signal)

    # Частоты
    frequencies = np.fft.fftfreq(N, d=1 / sample_rate)

    mask = frequencies >= 0

    frequencies = frequencies[mask]
    amplitude = np.abs(X[mask]) / N

    # Для одностороннего спектра амплитуду нужно удвоить,
    # кроме компоненты на 0 Гц
    if N > 1:
        amplitude[1:] *= 2

    return frequencies, amplitude


# ============================================================
# ОПРЕДЕЛЕНИЕ ГРАНИЦ СПЕКТРА
# ============================================================

def find_spectrum_width(frequencies, amplitude):
    # Чтобы шум не считался частью спектра,
    # задаём порог относительно максимальной амплитуды.
    threshold = np.max(amplitude) * 0.02

    significant = amplitude >= threshold

    if not np.any(significant):
        return None, None, None

    f_min = frequencies[significant][0]
    f_max = frequencies[significant][-1]

    width = f_max - f_min

    return f_min, f_max, width


# ============================================================
# АНАЛИЗ ОДНОГО СИГНАЛА
# ============================================================

def analyze_wav(filename, title, output_image):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    signal, fs = read_wav(filename)

    print(f"Файл: {filename}")
    print(f"Частота дискретизации: {fs} Гц")
    print(f"Количество отсчётов: {len(signal)}")
    print(f"Длительность: {len(signal) / fs:.3f} с")

    # ДПФ
    frequencies, amplitude = calculate_dft(signal, fs)

    # Границы спектра
    f_min, f_max, width = find_spectrum_width(
        frequencies,
        amplitude
    )

    print()
    print("Результаты ДПФ:")
    print(f"f_min = {f_min:.3f} Гц")
    print(f"f_max = {f_max:.3f} Гц")
    print(f"Ширина спектра:")
    print(f"Δf = f_max - f_min = {width:.3f} Гц")

    # Максимальная амплитуда
    max_index = np.argmax(amplitude)

    print()
    print(
        f"Максимальная амплитуда: "
        f"{amplitude[max_index]:.3f}"
    )
    print(
        f"Основная частота: "
        f"{frequencies[max_index]:.3f} Гц"
    )

    # ========================================================
    # ГРАФИК СПЕКТРА
    # ========================================================

    plt.figure(figsize=(12, 5))

    plt.plot(
        frequencies,
        amplitude
    )

    # Показываем найденные границы
    plt.axvline(
        f_min,
        linestyle='--',
        label=f'f_min = {f_min:.2f} Гц'
    )

    plt.axvline(
        f_max,
        linestyle='--',
        label=f'f_max = {f_max:.2f} Гц'
    )

    plt.xlabel('Частота, Гц')
    plt.ylabel('Амплитуда')
    plt.title(
        f'{title}\n'
        f'Ширина спектра = {width:.2f} Гц'
    )

    plt.grid(True)
    plt.legend()
    #plt.xlim(0, 2000)
    plt.xscale('log')
    plt.xlim(50, 10000)
    plt.xticks([50, 100, 200, 500, 1000, 2000, 5000, 10000],
           ['50', '100', '200', '500', '1k', '2k', '5k', '10k'])
    # Показываем только область с полезным спектром
    #plt.xlim(0, min(fs / 2, f_max * 1.2))

    plt.tight_layout()
    plt.savefig(
        output_image,
        dpi=300,
        format='png'
    )

    #plt.show()

    return frequencies, amplitude


# ============================================================
# 1. ОРИГИНАЛЬНЫЙ WAV
# ============================================================

freq_original, amp_original = analyze_wav(
    "Моя_запись1.wav",
    "Оригинальный сигнал",
    "spectrum_original.png"
)


# ============================================================
# 2. ПРОРЕЖЕННЫЙ WAV
# ============================================================

freq_decimated, amp_decimated = analyze_wav(
    "Моя_запись1_11.wav",
    "Прореженный сигнал",
    "spectrum_decimated.png"
)


# ============================================================
# 3. СРАВНЕНИЕ СПЕКТРОВ
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    freq_original,
    amp_original,
    label='Оригинальный сигнал'
)

plt.plot(
    freq_decimated,
    amp_decimated,
    label='Прореженный сигнал'
)

plt.xlabel('Частота, Гц')
plt.ylabel('Амплитуда')

plt.title(
    'Сравнение амплитудных спектров'
)

plt.grid(True)
plt.legend()

# Удобно смотреть только первую часть спектра
plt.xlim(
    0,
    min(
        freq_original[-1],
        freq_decimated[-1]
    )
)

plt.tight_layout()
plt.savefig(
    "spectrum_comparison.png",
    dpi=300,
    format='png'
)

#plt.show()

# ============================================================
# 4. СПЕКТРЫ В ДБ
# ============================================================

def to_db(amplitude):
    """Перевод амплитуды в дБ относительно максимума."""
    amp_max = np.max(amplitude)
    if amp_max <= 0:
        return np.full_like(amplitude, -np.inf)
    return 20 * np.log10(amplitude / amp_max + 1e-12)


amp_original_db  = to_db(amp_original)
amp_decimated_db = to_db(amp_decimated)


# --- 4a. Оригинал в дБ ---
plt.figure(figsize=(12, 5))

plt.plot(freq_original, amp_original_db, color='C0', lw=0.7)

plt.xlabel('Частота, Гц')
plt.ylabel('Уровень, дБ')
plt.title('Амплитудный спектр оригинала (дБ)')

plt.ylim(-80, 5)
plt.xlim(0, freq_original[-1])
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("spectrum_original_db.png", dpi=300, format='png')


# --- 4b. Прореженный в дБ ---
plt.figure(figsize=(12, 5))

plt.plot(freq_decimated, amp_decimated_db, color='C1', lw=0.7)

plt.axvline(
    freq_decimated[-1],
    color='g', ls=':',
    label=f'Найквист = {freq_decimated[-1]:.0f} Гц'
)

plt.xlabel('Частота, Гц')
plt.ylabel('Уровень, дБ')
plt.title('Амплитудный спектр прореженного сигнала (дБ)')

plt.ylim(-80, 5)
plt.xlim(0, freq_decimated[-1])
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("spectrum_decimated_db.png", dpi=300, format='png')


# --- 4c. Сравнение в дБ ---
plt.figure(figsize=(12, 6))

plt.plot(
    freq_original, amp_original_db,
    label=f'Оригинал (fs = {freq_original[-1]*2:.0f} Гц)',
    color='C0', lw=0.7
)

plt.plot(
    freq_decimated, amp_decimated_db,
    label=f'Прореженный (fs = {freq_decimated[-1]*2:.0f} Гц)',
    color='C1', lw=0.7, alpha=0.85
)

plt.axhline(-40, color='k', ls='--', lw=0.8, label='порог −40 дБ')
plt.axvline(freq_decimated[-1], color='g', ls=':', label='Найквист прореженного')

plt.xlabel('Частота, Гц')
plt.ylabel('Уровень, дБ')
plt.title('Сравнение спектров в дБ')

plt.ylim(-80, 5)
plt.xlim(0, freq_original[-1])
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("spectrum_comparison_db.png", dpi=300, format='png')



# ============================================================
# 5. СДВИГ СПЕКТРА НА +{SHIFT_HZ} Гц (писклявый голос)
# ============================================================

SHIFT_HZ = 200.0


def frequency_shift_fft_v2(signal, fs, shift_hz):
    """
    Сдвиг спектра вещественного сигнала на shift_hz (SSB).
    """
    N = len(signal)
    X = np.fft.fft(signal)

    dk = int(round(shift_hz * N / fs))

    X_analytic = np.zeros_like(X)
    X_analytic[0] = X[0]                     
    X_analytic[1:N//2] = 2 * X[1:N//2]       # положительные частоты ×2
    if N % 2 == 0:
        X_analytic[N//2] = X[N//2]           

    # 2. Сдвигаем  спектр вправо на dk позиций
    X_shifted = np.zeros_like(X)
    if 0 <= dk < N:
        X_shifted[dk:N] = X_analytic[:N - dk]

    y = np.fft.ifft(X_shifted).real

    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * np.max(np.abs(signal))

    return y

# --- 5a. Сдвигаем оригинал ---
signal_orig, fs_orig = read_wav("Моя_запись1.wav")

signal_shifted = frequency_shift_fft_v2(
    signal_orig,
    fs_orig,
    SHIFT_HZ
)

# Сохраняем как int16 WAV
out_shifted = np.clip(
    np.round(signal_shifted),
    -32768, 32767
).astype(np.int16)

with wave.open("Моя_запись1_shift1000.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(fs_orig)
    w.writeframes(out_shifted.tobytes())

print()
print("=" * 60)
print(f"Сдвиг спектра на +{SHIFT_HZ:.0f} Гц")
print("=" * 60)
print(f"Файл: Моя_запись1_shift1000.wav")
print(f"Частота дискретизации: {fs_orig} Гц")
print(f"Количество отсчётов: {len(signal_shifted)}")


# --- 5b. Анализ спектра сдвинутого сигнала ---
freq_shifted, amp_shifted = analyze_wav(
    "Моя_запись1_shift1000.wav",
    f"Сдвиг спектра на +{SHIFT_HZ:.0f} Гц",
    "spectrum_shift1000.png"
)


# --- 5c. Сравнение спектров в дБ ---
amp_shifted_db = to_db(amp_shifted)

plt.figure(figsize=(12, 6))

plt.plot(
    freq_original, amp_original_db,
    label='Оригинал',
    color='C0', lw=0.7
)

plt.plot(
    freq_shifted, amp_shifted_db,
    label=f'Сдвиг на +{SHIFT_HZ:.0f} Гц',
    color='C2', lw=0.7, alpha=0.85
)

plt.xlabel('Частота, Гц')
plt.ylabel('Уровень, дБ')
plt.title(f'Спектры: оригинал vs сдвиг на +{SHIFT_HZ:.0f} Гц')

plt.ylim(-80, 5)
#plt.xlim(0, fs_orig / 2)
#plt.xlim(0, 2000)
plt.xscale('log')
plt.xlim(50, 10000)
plt.xticks([50, 100, 200, 500, 1000, 2000, 5000, 10000],
           ['50', '100', '200', '500', '1k', '2k', '5k', '10k'])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(
    "spectrum_shift1000_db.png",
    dpi=300,
    format='png'
)