
import math
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Исходные данные из задания
# ==========================================

P_BS = 46.0          # Мощность БС, дБм
P_UE = 24.0          # Мощность UE, дБм
G_BS = 21.0          # Усиление антенны БС, дБи
MIMO = 3.0           # Выигрыш MIMO 2x2, дБ
FEEDER = 2.9         # Потери: фидер 2 + МШУ 0.4 + джампер 0.5, дБ
PENETRATION = 15.0   # Потери проникновения, дБ
INTERFERENCE = 1.0   # Запас на интерференцию, дБ

F_MHZ = 1800.0       # Частота, МГц
F_GHZ = F_MHZ / 1000  # Частота, ГГц

BW_UL = 10e6         # Полоса UL, Гц
BW_DL = 20e6         # Полоса DL, Гц

NF_BS = 2.4          # Коэффициент шума БС, дБ
NF_UE = 6.0          # Коэффициент шума UE, дБ

SINR_UL = 4.0        # Требуемый SINR UL, дБ
SINR_DL = 2.0        # Требуемый SINR DL, дБ

AREA_MACRO = 100.0   # Площадь макросети, км²
AREA_MICRO = 4.0     # Площадь ТЦ и бизнес-центров, км²
SECTORS = 3          # Число секторов на БС

# Параметры COST231-Hata
H_BS = 50.0          # Высота антенны БС, м
H_UE = 1.5           # Высота антенны UE, м

# ==========================================
# Чувствительность приемника
# ==========================================

def thermal_noise(bandwidth):
    """Тепловой шум, дБм."""
    return -174 + 10 * math.log10(bandwidth)


def receiver_sensitivity(nf, bandwidth, sinr):
    """Чувствительность приемника, дБм."""
    return nf + thermal_noise(bandwidth) + sinr


noise_ul = thermal_noise(BW_UL)
noise_dl = thermal_noise(BW_DL)

rx_bs = receiver_sensitivity(NF_BS, BW_UL, SINR_UL)
rx_ue = receiver_sensitivity(NF_UE, BW_DL, SINR_DL)

# ==========================================
# Бюджет радиканала
# ==========================================

mapl_ul = P_UE - FEEDER + G_BS + MIMO - INTERFERENCE - PENETRATION - rx_bs


mapl_dl = P_BS - FEEDER + G_BS + MIMO - INTERFERENCE - PENETRATION - rx_ue


print("=== БЮДЖЕТ РАДИОЛИНИИ ===")
print(f"Тепловой шум UL: {noise_ul:.2f} дБм")
print(f"Тепловой шум DL: {noise_dl:.2f} дБм")
print(f"Чувствительность БС: {rx_bs:.2f} дБм")
print(f"Чувствительность UE: {rx_ue:.2f} дБм")
print(f"MAPL UL: {mapl_ul:.2f} дБ")
print(f"MAPL DL: {mapl_dl:.2f} дБ")

# ==========================================
# Модель UMiNLOS
# Расстояние в метрах
# ==========================================

def pl_umi(d_m):
    return 26 * math.log10(F_GHZ) + 22.7 + 36.7 * math.log10(d_m)

# ==========================================
# Модель COST231-Hata
# Расстояние в километрах
# ==========================================

def pl_cost231(d_km):
    f = F_MHZ

    A = 46.3 # f 1500-2000 Mhz
    B = 33.9
    Lclutter = 0 #Городская местность: Lclutter = 0, так как Urban
    
    a = 3.2 * (math.log10(11.75 * H_UE) ** 2) - 4.97 # Городская местность
    
    if d_km >= 1:
        s = 44.9 - 6.55 * math.log10(f)  # d >= 1 km
    elif d_km < 1:  # d < 1 km
        s = (47.88 + 13.9 * math.log10(f) - 13.9 * math.log10(H_BS)) * (1 / (math.log10(50)))

    return (
        A + B * math.log10(f)
        - 13.82 * math.log10(H_BS)
        - a
        + s * math.log10(d_km)
        + Lclutter 
    )


# ==========================================
# Модель Walfisch-Ikegami, LOS
# Расстояние в километрах
# ==========================================

def pl_walfisch_los(d_km):
    return (
        42.6
        + 20 * math.log10(F_MHZ)
        + 26 * math.log10(d_km)
    )
"""
def pl_walfisch_nlos(d_km):
    return (
        42.6
        + 20 * math.log10(F_MHZ)
        + 26 * math.log10(d_km)
    )
"""

# ==========================================
# Поиск радиуса по заданному MAPL
# ==========================================

def find_radius(pl_function, target_loss, d_min, d_max,
                unit="km", steps=200000):
    """
    Находит максимальное расстояние, на котором PL <= MAPL.
    Поиск выполняется численно.
    """
    distances = np.geomspace(d_min, d_max, steps)
    losses = np.array([pl_function(d) for d in distances])

    valid = np.where(losses <= target_loss)[0]

    if len(valid) == 0:
        return None

    index = valid[-1]

    if index == len(distances) - 1:
        return None

    # Линейная интерполяция между соседними точками
    x1, x2 = distances[index:index + 2]
    y1, y2 = losses[index:index + 2]

    radius = x1 + (target_loss - y1) * (x2 - x1) / (y2 - y1)
    return radius


# Радиусы микросот и фемтосот по UMiNLOS
r_umi_ul_m = find_radius(
    pl_umi, mapl_ul, 1, 10000, unit="m"
)
r_umi_dl_m = find_radius(
    pl_umi, mapl_dl, 1, 10000, unit="m"
)

# Радиусы макросот по COST231-Hata
r_cost_ul_km = find_radius(
    pl_cost231, mapl_ul, 0.01, 20
)
r_cost_dl_km = find_radius(
    pl_cost231, mapl_dl, 0.01, 20
)

r_walfisch_dl_km = find_radius(
    pl_walfisch_los, mapl_dl, 0.01, 40
)

r_walfisch_ul_km = find_radius(
    pl_walfisch_los, mapl_ul, 0.01, 40
)
"""

r_walfisch_nlos_dl_km = find_radius(
    pl_walfisch_nlos, mapl_ul, 0.01, 40
)

r_walfisch_nlos_ul_km = find_radius(
    pl_walfisch_nlos, mapl_ul, 0.01, 40
)
"""

print("\n=== РАДИУСЫ СОТ ===")
print(f"UMiNLOS UL: {r_umi_ul_m:.2f} м")
print(f"UMiNLOS DL: {r_umi_dl_m:.2f} м")
print(f"COST231-Hata UL: {r_cost_ul_km:.3f} км")
print(f"COST231-Hata DL: {r_cost_dl_km:.3f} км")
print(f"Walfisch_LOS UL: {r_walfisch_ul_km:.3f} км")
print(f"Walfisch_LOS DL: {r_walfisch_dl_km:.3f} км")
"""
print(f"Walfisch_NLOS UL: {r_walfisch_nlos_ul_km:.3f} км")
print(f"Walfisch_NLOS DL: {r_walfisch_nlos_dl_km:.3f} км")
"""

# ==========================================
# Площадь покрытия и число базовых станций
# ==========================================

def calculate_network(area_km2, radius_km, sectors=3):
    """
    Площадь сайта для трех секторов:
    S = 1.95 * R^2
    """
    area_per_site = 1.95 * radius_km ** 2
    sites = math.ceil(area_km2 / area_per_site)
    return area_per_site, sites


# Для проектирования используем меньший радиус UL/DL
r_macro = min(r_cost_ul_km, r_cost_dl_km)
r_micro = min(r_umi_ul_m, r_umi_dl_m) / 1000

s_macro, n_macro = calculate_network(AREA_MACRO, r_macro)
s_micro, n_micro = calculate_network(AREA_MICRO, r_micro)

print("\n=== ПРОЕКТИРОВАНИЕ СЕТИ ===")
print(f"Макросота: радиус {r_macro:.3f} км")
print(f"Площадь одного сайта: {s_macro:.3f} км²")
print(f"Число сайтов на 100 км²: {n_macro}")

print(f"\nМикросота: радиус {r_micro * 1000:.2f} м")
print(f"Площадь одного сайта: {s_micro:.4f} км²")
print(f"Число сайтов на 4 км²: {n_micro}")

# ==========================================
# График потерь сигнала
# ==========================================

dist_umi = np.geomspace(1, 2000, 500)  # метры
dist_cost = np.geomspace(0.01, 30, 500)  # км

plt.figure(figsize=(10, 6))

plt.plot(
    dist_umi,
    [pl_umi(d) for d in dist_umi],
    label="UMiNLOS (дальность в метрах)"
)

plt.axhline(
    mapl_ul, linestyle="--",
    label=f"MAPL UL = {mapl_ul:.1f} дБ"
)
plt.axhline(
    mapl_dl, linestyle="--",
    label=f"MAPL DL = {mapl_dl:.1f} дБ"
)
plt.axvline(r_umi_dl_m, linestyle="--", color="blue")
plt.axvline(r_umi_ul_m, linestyle="--", color="blue")
plt.axvline(r_umi_dl_m, linestyle="--", label=f"d DL = {r_umi_dl_m:.1f} м")
plt.axvline(r_umi_ul_m, linestyle="--", label=f"d UL = {r_umi_ul_m:.1f} м")

plt.xscale("log")
plt.xlabel("Расстояние, м")
plt.ylabel("Потери сигнала, дБ")
plt.title("UMiNLOS: потери сигнала и пределы MAPL")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.savefig("UMiNLOS.png")

plt.figure(figsize=(10, 6))

plt.plot(
    dist_cost,
    [pl_cost231(d) for d in dist_cost],
    label="COST231-Hata, город"
)

plt.plot(
    dist_cost,
    [pl_walfisch_los(d) for d in dist_cost],
    label="Walfisch-Ikegami LOS"
)
"""
pl_umi_res_km = np.array([pl_umi(d) for d in dist_umi]) / 1000
plt.plot(
    dist_umi,
    pl_umi_res_km,
    label="UMiNLOS"
)
"""
plt.axhline(mapl_ul, linestyle="--", label=f"MAPL UL = {mapl_ul:.1f} дБ", color="green")
plt.axhline(mapl_dl, linestyle="--", label=f"MAPL DL = {mapl_dl:.1f} дБ", color="red")
plt.axvline(r_cost_dl_km, linestyle="--", label=f"d DL = {r_cost_dl_km:.1f} км")
plt.axvline(r_cost_ul_km, linestyle="--", label=f"d UL = {r_cost_ul_km:.1f} км")
plt.axvline(r_walfisch_ul_km, linestyle="--", label=f"d UL = {r_walfisch_ul_km:.1f} км", color="orange")
plt.axvline(r_walfisch_dl_km, linestyle="--", label=f"d DL = {r_walfisch_dl_km:.1f} км", color="orange")
plt.text(
    r_cost_dl_km, 
    0,  
    f'{r_cost_dl_km:.2f} км',  
    color='red',
    verticalalignment='top',
)
plt.xscale("log")
plt.xlabel("Расстояние, км")
plt.ylabel("Потери сигнала, дБ")
plt.title("Сравнение моделей распространения")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.savefig("cmp.png")