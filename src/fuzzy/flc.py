"""Mamdani Tip-1 bulanık mantık denetleyicisi (FLC), 36 kural.

Makale (Kumaresan & Rammohan, 2025): giriş B_SoC (3 MF), SC_SoC (3 MF), P_D (4 MF),
trapezoidal; 3x3x4 = 36 kural. Giriş MF köşeleri makalenin Şekil 4'ünden yaklaşık okundu.

ÖNEMLİ: Makale kural tablosunu YAYIMLAMIYOR. Aşağıdaki 36 kural bu projede, mühendislik
mantığıyla (bkz. build_rule_table) YENİDEN YAZILMIŞTIR. Makaledeki kurallarla aynı olduğu
iddia edilmez.

Çıkış: süperkapasitör güç payı (0-100 %). Batarya payı = 100 - SC payı.
(Makale iki çıkış, batarya ve SC katsayısı, kullanıyor; burada ikisi birbirinin tümleyeni.)
"""
import numpy as np

# ---------- üyelik fonksiyonları ----------
def trapmf(x, a, b, c, d):
    """Trapezoidal MF: (a,0)-(b,1)-(c,1)-(d,0)."""
    x = np.asarray(x, dtype=float)
    left = np.where(b > a, (x - a) / max(b - a, 1e-12), (x >= b).astype(float))
    right = np.where(d > c, (d - x) / max(d - c, 1e-12), (x <= c).astype(float))
    return np.clip(np.minimum(left, right), 0.0, 1.0)


def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    return np.clip(np.minimum((x - a) / max(b - a, 1e-12), (c - x) / max(c - b, 1e-12)), 0.0, 1.0)


# Şekil 4'ten yaklaşık okunan köşeler. SoC değerleri yüzde, P_D watt.
# Uç MF'ler evrenin kenarına kadar "omuz" yapılmıştır (örn. SoC=%100'de High MF = 1).
# Şekil 4'ten okunan tepe köşeleri korunmuş, sadece kenar boşlukları kapatılmıştır;
# aksi halde SoC=%100 (makalenin başlangıç koşulu) ya da P_D=0 hiçbir MF'ye girmiyor.
B_SOC = {"Düşük": (0, 0, 30, 40), "Orta": (40, 50, 60, 70), "Yüksek": (70, 80, 100, 100)}
SC_SOC = {"Düşük": (0, 0, 40, 60), "Orta": (55, 65, 75, 85), "Yüksek": (80, 87, 100, 100)}
P_D = {"Reje": (-5000, -4000, -2000, -200), "Düşük": (-200, 0, 1500, 2000),
       "Orta": (2000, 3000, 3500, 4000), "Yüksek": (4000, 4500, 5700, 5700)}

B_NAMES, S_NAMES, P_NAMES = list(B_SOC), list(SC_SOC), list(P_D)

# Çıkış: 0..100 üzerinde 11 üçgen MF (makale 11-12 üçgen MF kullanıyor), 10'ar birim aralıklı.
OUT_X = np.linspace(-10, 110, 241)  # kenar üçgenlerin merkezi tam 0 ve 100 olsun diye evren taşırılmış
OUT_CENTERS = np.arange(0, 101, 10)
OUT_MF = [trimf(OUT_X, c - 10, c, c + 10) for c in OUT_CENTERS]


def build_rule_table():
    """36 kural: (B_SoC, SC_SoC, P_D) -> çıkış MF indeksi (0..10, SC payı = 10*indeks %).

    Mantık:
      * Düşük güç: SC devrede değil (batarya yeterli, SC enerjisi korunur).
      * Orta / yüksek güç: SC payı, SC'nin doluluğuna göre ölçeklenir
        (SC düşükse yarısı, orta doluysa 3/4'ü, doluysa tam pay; alt sınırda SC zaten simülasyonda devre dışı).
      * Batarya doluluğu düşükse SC'ye +%10 ek pay verilir (bataryayı rahatlat).
      * Rejenerasyon: enerji SC'ye yönlendirilir (SC doluysa %0, aksi halde yüksek).
    """
    base = {"Düşük": 0, "Orta": 2, "Yüksek": 4}       # tam dolu SC için taban pay (x10 %)
    s_scale = {"Düşük": 0.5, "Orta": 0.75, "Yüksek": 1.0}
    rules = {}
    for b in B_NAMES:
        for s in S_NAMES:
            for p in P_NAMES:
                if p == "Reje":
                    lvl = 0 if s == "Yüksek" else 10
                else:
                    lvl = base[p] * s_scale[s]
                    if p != "Düşük" and b == "Düşük" and s != "Düşük":
                        lvl += 1
                    lvl = int(round(lvl))
                rules[(b, s, p)] = lvl
    return rules


RULES = build_rule_table()  # 3*3*4 = 36


class FLC:
    """Mamdani çıkarımı: min (VE), min (ima), max (birleştirme), ağırlık merkezi (centroid)."""

    def __init__(self, rules=None):
        self.rules = rules or RULES

    @staticmethod
    def fuzzify(b, s, p):
        mb = {k: float(trapmf(b, *v)) for k, v in B_SOC.items()}
        ms = {k: float(trapmf(s, *v)) for k, v in SC_SOC.items()}
        mp = {k: float(trapmf(p, *v)) for k, v in P_D.items()}
        return mb, ms, mp

    def output_percent(self, b_pct, s_pct, p_w):
        """Girişler: B_SoC %, SC_SoC %, P_D W. Dönüş: SC güç payı, %."""
        # girişleri MF evrenine kırp (P_D, makale evreni 5700 W'ı aşabilir: bizim güç talebi tepesi ~6,1 kW)
        b_pct = min(max(b_pct, 0.0), 100.0)
        s_pct = min(max(s_pct, 0.0), 100.0)
        p_w = min(max(p_w, -5000.0), 5700.0)
        mb, ms, mp = self.fuzzify(b_pct, s_pct, p_w)
        agg = np.zeros_like(OUT_X)
        for (b, s, p), lvl in self.rules.items():
            w = min(mb[b], ms[s], mp[p])
            if w > 0:
                agg = np.maximum(agg, np.minimum(w, OUT_MF[lvl]))
        area = agg.sum()
        if area <= 1e-12:
            return 0.0
        return max(0.0, float((agg * OUT_X).sum() / area))

    def controller(self, p_dem, soc_bat, soc_sc):
        """Simülasyon arayüzü: SC güç payı 0..1 döner."""
        return self.output_percent(100 * soc_bat, 100 * soc_sc, p_dem) / 100.0
