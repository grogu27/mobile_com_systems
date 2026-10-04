import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# ИСХОДНЫЙ СИГНАЛ
# ============================================================

f = 4

# Частота дискретизации
f_s = 1000

# Длительность сигнала
T = 1

# Количество отсчётов
N = int(f_s * T)

# Временные отсчёты
t = np.arange(N) / f_s

# Исходный сигнал:
# y(t) = cos(2*pi*f*t) + sin(10*pi*f*t) + sin(6*t)
signal = (
    np.cos(2 * np.pi * f * t)
    + np.sin(10 * np.pi * f * t)
    + np.sin(6 * t)
)


# ============================================================
# ФУНКЦИЯ КВАНТОВАНИЯ
# ============================================================

def quantize_signal(signal, bits):
    """
    Квантует сигнал с заданной разрядностью АЦП.

    signal - исходный сигнал
    bits   - количество разрядов АЦП

    Возвращает:
    quantized_signal - квантованный сигнал
    """

    # Количество уровней квантования
    levels = 2 ** bits

    # Максимальное значение кода АЦП
    max_code = levels - 1

    # Диапазон исходного сигнала
    signal_min = np.min(signal)
    signal_max = np.max(signal)

    # Переводим сигнал из диапазона:
    #
    # [signal_min, signal_max]
    #
    # в диапазон кодов:
    #
    # [0, max_code]

    normalized = (
        (signal - signal_min)
        / (signal_max - signal_min)
    )

    codes = normalized * max_code

    # Округление до ближайшего уровня АЦП
    codes = np.round(codes)

    # Ограничиваем диапазон 0 ... max_code
    codes = np.clip(codes, 0, max_code)

    # Возвращаем коды обратно в диапазон амплитуд
    quantized_signal = (
        codes / max_code
        * (signal_max - signal_min)
        + signal_min
    )

    return quantized_signal


# ============================================================
# ФУНКЦИЯ ДПФ
# ============================================================

def calculate_spectrum(signal, sample_rate):

    N = len(signal)

    # Убираем постоянную составляющую
    signal_without_dc = signal - np.mean(signal)

    # ДПФ
    X = np.fft.fft(signal_without_dc)

    # Частоты
    frequencies = np.fft.fftfreq(
        N,
        d=1 / sample_rate
    )

    # Только положительная часть спектра
    mask = frequencies >= 0

    frequencies = frequencies[mask]

    amplitude = np.abs(X[mask]) / N

    # Для одностороннего спектра
    if N > 1:
        amplitude[1:] *= 2

    return frequencies, amplitude


# ============================================================
# СПЕКТР ИСХОДНОГО СИГНАЛА
# ============================================================

freq_original, spectrum_original = calculate_spectrum(
    signal,
    f_s
)


# ============================================================
# РАЗРЯДНОСТИ АЦП
# ============================================================

bits_list = [3, 4, 5, 6]

# Здесь будем хранить средние ошибки
errors = []


# ============================================================
# КВАНТОВАНИЕ ДЛЯ 3 / 4 / 5 / 6 БИТ
# ============================================================

for bits in bits_list:

    # Квантуем сигнал
    quantized_signal = quantize_signal(
        signal,
        bits
    )

    # --------------------------------------------------------
    # Средняя абсолютная ошибка квантования
    # --------------------------------------------------------

    error = np.mean(
        np.abs(signal - quantized_signal)
    )

    errors.append(error)

    # --------------------------------------------------------
    # ДПФ квантованного сигнала
    # --------------------------------------------------------

    frequencies, spectrum_quantized = calculate_spectrum(
        quantized_signal,
        f_s
    )

    # --------------------------------------------------------
    # Вывод результатов
    # --------------------------------------------------------

    print("=" * 60)
    print(f"Разрядность АЦП: {bits} бит")
    print(f"Количество уровней: {2 ** bits}")
    print(f"Коды АЦП: 0 ... {2 ** bits - 1}")

    print(
        f"Средняя ошибка квантования: "
        f"{error:.6f}"
    )

    # --------------------------------------------------------
    # График квантованного сигнала
    # --------------------------------------------------------

    plt.figure(figsize=(12, 5))

    plt.plot(
        t,
        signal,
        label="Исходный сигнал"
    )

    plt.step(
        t,
        quantized_signal,
        where="mid",
        label=f"Квантованный сигнал ({bits} бит)"
    )

    plt.xlabel("t, с")
    plt.ylabel("Амплитуда")

    plt.title(
        f"Квантование сигнала, {bits} бит"
    )

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        f"quantization_{bits}_bit.png",
        dpi=300
    )

    #plt.show()

    # --------------------------------------------------------
    # Сравнение спектров
    # --------------------------------------------------------

    plt.figure(figsize=(12, 5))

    plt.plot(
        freq_original,
        spectrum_original,
        label="Исходный сигнал"
    )

    plt.plot(
        frequencies,
        spectrum_quantized,
        label=f"Квантованный сигнал ({bits} бит)"
    )

    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплитуда")

    plt.title(
        f"Сравнение спектров, {bits} бит"
    )

    plt.xlim(0, 30)

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        f"spectrum_quantization_{bits}_bit.png",
        dpi=300
    )

    #plt.show()


# ============================================================
# ТАБЛИЦА ОШИБОК
# ============================================================

print()
print("=" * 60)
print("СРЕДНЯЯ ОШИБКА КВАНТОВАНИЯ")
print("=" * 60)

for bits, error in zip(bits_list, errors):

    print(
        f"{bits} бит: "
        f"{error:.6f}"
    )


# ============================================================
# ГРАФИК ОШИБКИ
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    bits_list,
    errors,
    marker="o"
)

plt.xlabel("Разрядность АЦП, бит")
plt.ylabel("Средняя ошибка квантования")

plt.title(
    "Зависимость средней ошибки квантования "
    "от разрядности АЦП"
)

plt.xticks(bits_list)
plt.grid(True)

plt.tight_layout()

plt.savefig(
    "quantization_error.png",
    dpi=300
)

#plt.show()