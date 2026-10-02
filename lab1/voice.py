import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import welch

# ---------- 1. Чтение файлов ----------
fs_orig, x_orig = wavfile.read("Моя_запись1.wav")
fs_dec,  x_dec  = wavfile.read("Моя_запись1_11.wav")

print(f"Оригинал:   fs = {fs_orig} Гц, отсчётов = {len(x_orig)}, "
      f"длительность = {len(x_orig)/fs_orig:.3f} с")
print(f"Прореженный: fs = {fs_dec} Гц, отсчётов = {len(x_dec)}, "
      f"длительность = {len(x_dec)/fs_dec:.3f} с")

# Приводим к float и моно (на случай стерео)
def to_mono_float(x):
    if x.ndim > 1:
        x = x.mean(axis=1)
    if x.dtype == np.int16:
        x = x.astype(np.float64) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float64) / 2147483648.0
    else:
        x = x.astype(np.float64)
    return x

x_orig = to_mono_float(x_orig)
x_dec  = to_mono_float(x_dec)

# ---------- 2. Прямое ДПФ (БПФ) ----------
def compute_spectrum(x, fs):
    N = len(x)
    # окно Ханна, чтобы уменьшить утечку спектра
    w = np.hanning(N)
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(N, d=1.0/fs)
    # нормировка амплитуды: учитываем окно и односторонний спектр
    amp = np.abs(X) * 2.0 / (N * w.sum() / N) / 2.0
    # проще: amp = 2*|X| / sum(w)
    amp = 2.0 * np.abs(X) / np.sum(w)
    return freqs, amp

f_orig, A_orig = compute_spectrum(x_orig, fs_orig)
f_dec,  A_dec  = compute_spectrum(x_dec,  fs_dec)

# ---------- 3. Определение ширины спектра ----------
def spectrum_width(freqs, amp, threshold_db=-40, f_max=None):
    """
    Ширина спектра: максимальная частота, на которой амплитуда
    ещё превышает threshold_db от максимума.
    f_max — верхняя граница поиска (например, fs/2 для антиалиасинга).
    """
    amp_db = 20 * np.log10(amp / amp.max() + 1e-12)
    mask = amp_db > threshold_db
    if f_max is not None:
        mask &= (freqs <= f_max)
    if not np.any(mask):
        return 0.0
    return freqs[mask][-1]

W_orig = spectrum_width(f_orig, A_orig, threshold_db=-40)
W_dec  = spectrum_width(f_dec,  A_dec,  threshold_db=-40)

print(f"\nШирина спектра оригинала  (-40 дБ): {W_orig:.1f} Гц")
print(f"Ширина спектра прореженного (-40 дБ): {W_dec:.1f} Гц")
print(f"Теоретический предел для прореженного (fs/2): {fs_dec/2:.1f} Гц")

# ---------- 4. Графики ----------
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Оригинал
axes[0].plot(f_orig, A_orig, color='C0', lw=0.7)
axes[0].axvline(W_orig, color='r', ls='--', label=f'ширина ≈ {W_orig:.0f} Гц')
axes[0].axvline(fs_dec/2, color='g', ls=':', label=f'Найквист прореж. = {fs_dec/2:.0f} Гц')
axes[0].set_title(f'Амплитудный спектр оригинала (fs = {fs_orig} Гц)')
axes[0].set_xlabel('Частота, Гц')
axes[0].set_ylabel('Амплитуда')
axes[0].set_xlim(0, fs_orig/2)
axes[0].grid(True, alpha=0.3)
axes[0].legend()

# Прореженный
axes[1].plot(f_dec, A_dec, color='C1', lw=0.7)
axes[1].axvline(W_dec, color='r', ls='--', label=f'ширина ≈ {W_dec:.0f} Гц')
axes[1].axvline(fs_dec/2, color='g', ls=':', label=f'Найквист = {fs_dec/2:.0f} Гц')
axes[1].set_title(f'Амплитудный спектр прореженного сигнала (fs = {fs_dec} Гц)')
axes[1].set_xlabel('Частота, Гц')
axes[1].set_ylabel('Амплитуда')
axes[1].set_xlim(0, fs_orig/2)   # одинаковый масштаб по X для сравнения
axes[1].grid(True, alpha=0.3)
axes[1].legend()

plt.tight_layout()
plt.savefig("spectra.png", dpi=300)
#plt.show()

# ---------- 5. Дополнительно: спектр в дБ ----------
fig2, ax = plt.subplots(figsize=(12, 5))
ax.plot(f_orig, 20*np.log10(A_orig/A_orig.max()+1e-12),
        label=f'оригинал (fs={fs_orig})', lw=0.7)
ax.plot(f_dec,  20*np.log10(A_dec /A_dec.max() +1e-12),
        label=f'прореженный (fs={fs_dec})', lw=0.7, alpha=0.8)
ax.axhline(-40, color='k', ls='--', lw=0.8, label='порог −40 дБ')
ax.axvline(fs_dec/2, color='g', ls=':', label=f'Найквист = {fs_dec/2:.0f} Гц')
ax.set_xlim(0, fs_orig/2)
ax.set_ylim(-100, 5)
ax.set_xlabel('Частота, Гц')
ax.set_ylabel('Уровень, дБ')
ax.set_title('Спектры в логарифмическом масштабе')
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig("spectra_db.png", dpi=300)
#plt.show()