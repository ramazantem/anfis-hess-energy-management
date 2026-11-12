"""E2W (elektrikli iki tekerlekli) güç talebi modeli.

Parametreler makalenin Tablo 3'ünden (Kumaresan & Rammohan, 2025).
"""
import numpy as np

G = 9.81  # m/s^2
RHO = 1.2  # kg/m^3, hava yoğunluğu (makalede verilmemiş, standart değer)

PARAMS = {
    "mass": 200.0,   # kg, toplam ağırlık (Tablo 3)
    "cd": 0.22,      # sürükleme katsayısı (Tablo 3)
    "area": 0.875,   # m^2, ön alan (Tablo 3)
    "crr": 0.015,    # yuvarlanma direnci katsayısı (Tablo 3)
    "eta_trans": 0.95,  # aktarma verimi (Tablo 3)
}


def power_demand(v, dt, eta_drive=1.0, p_aux=0.0, **overrides):
    """Hız profilinden DC baradaki güç talebini (W) hesaplar.

    + değer: çekiş (enerji harcanıyor), - değer: frenleme (geri kazanılabilir güç).
    eta_drive: motor + inverter verimi (makalede verilmemiş, 1,0 = ek kayıp yok).
    p_aux: sabit yardımcı yük (W), KALİBRASYON; makalenin tüketim değerine yaklaşmak için.
    """
    p = {**PARAMS, **overrides}
    a = np.gradient(v, dt)
    force = (p["mass"] * a
             + 0.5 * RHO * p["cd"] * p["area"] * v**2
             + p["crr"] * p["mass"] * G)
    p_wheel = force * v
    eta = p["eta_trans"] * eta_drive
    return np.where(p_wheel >= 0, p_wheel / eta, p_wheel * eta) + p_aux
