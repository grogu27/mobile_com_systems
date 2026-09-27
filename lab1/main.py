
#𝑦(𝑡) = cos(2𝜋𝑓𝑡) +sin(10𝜋𝑓𝑡) + sin(6𝑡), f=4
#omega=2pi*f   f=w/2pi

import numpy as np
import matplotlib.pyplot as plt

f = 4

# 1
print("-------------------------1-------------------------")
array_t = np.linspace(0, 1, 1000)
x_t = np.cos(2 * np.pi * f * array_t)
x2_t = np.sin(10 * np.pi * f * array_t)
x3_t = np.sin(6 * array_t)

sum_sig = x_t + x2_t + x3_t

plt.figure(figsize=(12, 5))
plt.plot(array_t, sum_sig)

plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title(r'График сигнала y(t) = cos(2pi*f*t) + sin(10pi*f*t) + sin(6t), f=4')
plt.grid(True)

plt.savefig("sum_sig.png", dpi=300, format='png')

plt.figure(figsize=(12, 5))
plt.plot(array_t, x_t, color='green', label='y(t)')
plt.plot(array_t, x2_t, color='red', label='y2(t)')
plt.plot(array_t, x3_t, color='black', label='y3(t)')
plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title(r'Графики сигналов y(t) = cos(2pi*f*t), y2(t) = sin(10pi*f*t), y3(t) = sin(6t), f=4')
plt.grid(True)
plt.legend()
plt.savefig("signals.png", dpi=300, format='png')

#2
print("-------------------------2-------------------------")
w1 = 2 * np.pi * 4
w2 = 10 * np.pi * 4
w3 = 6

f1 = w1 / (2 * np.pi)
f2 = w2 / (2 * np.pi)
f3 = w3 / (2 * np.pi)

print(f"Частота y(t): {f1:.3f} Гц, Частота y2(t): {f2:.3f} Гц, Частота y3(t): {f3:.3f} Гц")
spectr = [f1, f2, f3]
print(f"Спектр сигнала: {spectr}")
f_max = max(spectr)
print(f"Максимальная частота в спектре: {f_max:.0f} Гц")

#3
print("-------------------------3-------------------------")
print(f"Теорема Котельникова: f_s > 2*f_max")
f_s_min = f_max * 2 + 10
print(f"Минимальная необходимая частота дискретизация полученного сигнала: {f_s_min:.0f} Гц")

#4
print("-------------------------4-------------------------")
T = 1 # 1 сек длительность сигнала
N = int(f_s_min * T)  # кол-во дискретных точек
t_discrete = np.arange(N) / f_s_min # Временные точки дискретизации
print(f"Временные точки дискретизации: {t_discrete}")
y_discrete = np.cos(2 * np.pi * f * t_discrete) + np.sin(10 * np.pi * f * t_discrete) + np.sin(6 * t_discrete) 
print(f"Значения сигнала в дискретных точках: {y_discrete}")

plt.figure(figsize=(12, 5))

plt.stem(t_discrete, y_discrete)

plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title(f'Оцифрованный сигнал, f_s = {f_s_min} Гц')
plt.grid(True)
plt.savefig("digitized_signal.png", dpi=300, format='png')

#5
print("-------------------------5-------------------------")
Y = np.fft.fft(y_discrete)
print(f"ДПФ сигнала: {Y}")
freq = np.fft.fftfreq(N, d=1 / f_s_min) #d=1 / f_s_min это интервал между соседними отсчётами по времени. Тут есть отрицательные значения, они не нужны.
print(f"Массив частот: {freq}")
mask = freq >= 0
#freq_positive2 = []
#freq_positive2 = [round(float(f), 3) for f in freq if f >= 0]
freq_positive = freq[mask]
print(f"Только пол часть спектра: {freq_positive}")
amplitude_positive = 2 * np.abs(Y[mask]) / N  #двусторонний спектр
print(f"Амплитуды: {amplitude_positive}")

plt.figure(figsize=(12, 5))
plt.stem(freq_positive, amplitude_positive)
plt.xlabel('f, Гц')
plt.ylabel('Амплитуда')
plt.title('Амплитудный спектр сигнала')
plt.grid(True)
plt.xticks(np.arange(0, 25, 1))
plt.savefig("spectrum.png", dpi=300, format='png')

f_min = min(spectr)
spectrum_width = f_max - f_min
print(f"Минимальная частота: {f_min:.3f} Гц")
print(f"Максимальная частота: {f_max:.3f} Гц")
print(f"Ширина спектра: {spectrum_width:.3f} Гц")

memory_bytes = y_discrete.nbytes
print(f"Тип данных: {y_discrete.dtype}")
print(f"Объем памяти: {memory_bytes} байт")


#6
print("-------------------------6-------------------------")
plt.figure(figsize=(12, 5))

plt.plot(array_t, sum_sig, label='Оригинальный сигнал')

plt.plot(t_discrete, y_discrete, label='Восстановленный сигнал')

plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title('Сравнение оригинального и восстановленного сигналов')
plt.legend()
plt.grid(True)

plt.savefig("restored_signal.png", dpi=300, format='png')

#7
print("-------------------------7-------------------------")
f_s = f_s_min * 4

T = 1 # 1 сек длительность сигнала
N = int(f_s * T)  # кол-во дискретных точек
t_discrete = np.arange(N) / f_s # Временные точки дискретизации
print(f"Временные точки дискретизации: {t_discrete}")
y_discrete = np.cos(2 * np.pi * f * t_discrete) + np.sin(10 * np.pi * f * t_discrete) + np.sin(6 * t_discrete) 
print(f"Значения сигнала в дискретных точках: {y_discrete}")

plt.figure(figsize=(12, 5))

plt.stem(t_discrete, y_discrete)

plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title(f'Оцифрованный сигнал, f_s = {f_s} Гц')
plt.grid(True)
plt.savefig("digitized_signal_2.png", dpi=300, format='png')


Y = np.fft.fft(y_discrete)
print(f"ДПФ сигнала: {Y}")
freq = np.fft.fftfreq(N, d=1 / f_s) #d=1 / f_s это интервал между соседними отсчётами по времени. Тут есть отрицательные значения, они не нужны.
print(f"Массив частот: {freq}")
mask = freq >= 0
#freq_positive2 = []
#freq_positive2 = [round(float(f), 3) for f in freq if f >= 0]
freq_positive = freq[mask]
print(f"Только пол часть спектра: {freq_positive}")
amplitude_positive = 2 * np.abs(Y[mask]) / N  #двусторонний спектр
print(f"Амплитуды: {amplitude_positive}")

plt.figure(figsize=(12, 5))
plt.stem(freq_positive, amplitude_positive)
plt.xlabel('f, Гц')
plt.ylabel('Амплитуда')
plt.title('Амплитудный спектр сигнала')
plt.grid(True)
plt.xticks(np.arange(0, 25, 1))
plt.savefig("spectrum_2.png", dpi=300, format='png')

f_min = min(spectr)
spectrum_width = f_max - f_min
print(f"Минимальная частота: {f_min:.3f} Гц")
print(f"Максимальная частота: {f_max:.3f} Гц")
print(f"Ширина спектра: {spectrum_width:.3f} Гц")

memory_bytes = y_discrete.nbytes
print(f"Тип данных: {y_discrete.dtype}")
print(f"Объем памяти: {memory_bytes} байт")



plt.figure(figsize=(12, 5))

plt.plot(array_t, sum_sig, label='Оригинальный сигнал')

plt.plot(t_discrete, y_discrete, label='Восстановленный сигнал')

plt.xlabel('t, с')
plt.ylabel('y(t)')
plt.title('Сравнение оригинального и восстановленного сигналов')
plt.legend()
plt.grid(True)

plt.savefig("restored_signal_2.png", dpi=300, format='png')
