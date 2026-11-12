"""Sürüş çevrimi.

Makale (Kumaresan & Rammohan, 2025) gerçek bir E2W hız ölçümü kullanıyor (Şekil 8):
900 s, 12,4 km, tepe hız 82,9 km/h, ortalama hız 47,5 km/h, ivme -2,655..+2,723 m/s^2.
Veri paylaşılmadığı için burada Şekil 8'den okunan (zaman, hız) köşe noktalarından
yaklaşık bir profil kuruluyor. Bu bir YAKLAŞIMDIR, makalenin kendi verisi değildir.
"""
import numpy as np

# (zaman [s], hız [km/h]) - Şekil 8'den yaklaşık okunan köşe noktaları
WAYPOINTS = [
    (0, 0), (5, 0), (10, 15), (20, 40), (28, 50), (35, 20), (45, 35), (60, 68),
    (65, 69), (70, 30), (72, 24), (80, 45), (90, 60), (100, 65), (110, 70),
    (120, 72), (130, 60), (135, 58), (140, 75), (150, 81), (160, 79), (180, 75),
    (200, 80), (210, 78), (235, 80), (245, 80), (255, 70), (265, 52), (270, 50),
    (290, 62), (300, 64), (305, 52), (320, 58), (340, 64), (350, 65), (355, 40),
    (360, 5), (375, 5), (380, 0), (395, 0), (400, 5), (410, 30), (430, 45),
    (450, 58), (460, 60), (475, 52), (490, 68), (500, 70), (510, 62), (520, 33),
    (525, 10), (535, 25), (545, 22), (555, 40), (570, 50), (585, 50), (600, 52),
    (620, 55), (640, 50), (655, 40), (660, 25), (665, 12), (675, 28), (678, 8),
    (690, 40), (710, 56), (720, 42), (730, 40), (745, 54), (760, 56), (770, 50),
    (785, 20), (790, 35), (800, 25), (810, 55), (825, 54), (830, 25), (840, 35),
    (850, 22), (860, 48), (880, 50), (895, 30), (900, 0),
]


def one_cycle(dt=1.0):
    """Tek 900 s'lik çevrim. Dönüş: zaman (s), hız (m/s)."""
    t_w = np.array([p[0] for p in WAYPOINTS], dtype=float)
    v_w = np.array([p[1] for p in WAYPOINTS], dtype=float) / 3.6
    t = np.arange(0, 900 + dt, dt)
    v = np.interp(t, t_w, v_w)
    return t, v


def repeated_cycle(n_cycles=7, dt=1.0):
    """Çevrimi arka arkaya n kez tekrarlar (makalede ~7000 s'lik testler var)."""
    t1, v1 = one_cycle(dt)
    v = np.concatenate([v1[:-1]] * n_cycles + [v1[-1:]])
    t = np.arange(len(v)) * dt
    return t, v


def cycle_stats(t, v):
    """Özet: süre, mesafe, tepe ve ortalama hız, tepe ivme/yavaşlama."""
    dt = t[1] - t[0]
    a = np.gradient(v, dt)
    return {
        "süre_s": t[-1] - t[0],
        "mesafe_km": np.sum(v) * dt / 1000,
        "tepe_hız_kmh": v.max() * 3.6,
        "ort_hız_kmh": v.mean() * 3.6,
        "maks_ivme": a.max(),
        "maks_yavaşlama": a.min(),
    }
