"""Batarya ve süperkapasitör modelleri.

Paket değerleri makalenin Bölüm 2 ve Tablo 2'sinden:
  Batarya: 3,7 kWh, 52,5 V, 70 Ah, boşalma derinliği %80 (100 -> 20)
  Süperkapasitör: 48 V, 406 F, 0,012 ohm (enerji 130 Wh)
Makalede verilmeyen iç direnç ve verim değerleri VARSAYIMDIR (aşağıda işaretli).
"""
import numpy as np


def _current(v, r, p):
    """P = V*I - R*I^2 denkleminden akım. p>0 deşarj, p<0 şarj."""
    p = min(p, v**2 / (4 * r) * 0.99)  # fiziksel güç sınırı
    return (v - np.sqrt(v**2 - 4 * r * p)) / (2 * r)


class Battery:
    """Coulomb sayımlı batarya. p_w: terminal gücü (+ deşarj, - şarj)."""

    def __init__(self, v_nom=52.5, cap_ah=70.0, r_int=0.05, soc=1.0):
        self.v = v_nom
        self.q = cap_ah * 3600.0       # C
        self.r = r_int                 # ohm, VARSAYIM (maks. akımı ~130 A'ya yaklaştırmak için)
        self.soc = soc
        self.loss_j = 0.0

    def step(self, p_w, dt):
        i = _current(self.v, self.r, p_w)
        self.soc -= i * dt / self.q
        self.loss_j += self.r * i**2 * dt
        return i


class Supercap:
    """Süperkapasitör. SC_SoC = V / V_max (gerilim oranı)."""

    def __init__(self, v_max=48.0, c_f=406.0, r_esr=0.012, soc=1.0, soc_min=0.30):
        self.v_max = v_max
        self.c = c_f
        self.r = r_esr
        self.v = soc * v_max
        self.soc_min = soc_min         # VARSAYIM: makaledeki SC_SoC ~%30'da duruyor (Şekil 17)

    @property
    def soc(self):
        return self.v / self.v_max

    def limit(self, p_w):
        """SC'nin o anda verebileceği/alabileceği gücü sınırlar."""
        if p_w > 0 and self.soc <= self.soc_min:
            return 0.0
        if p_w < 0 and self.soc >= 1.0:
            return 0.0
        return p_w

    def step(self, p_w, dt):
        i = _current(self.v, self.r, p_w)
        self.v = float(np.clip(self.v - i * dt / self.c, 0.5, self.v_max))
        return i

    @property
    def energy_wh(self):
        return 0.5 * self.c * self.v**2 / 3600.0
