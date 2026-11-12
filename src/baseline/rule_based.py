"""Basit denetleyiciler (baseline).

Arayüz: controller(p_dem, soc_bat, soc_sc) -> süperkapasitörün karşılayacağı güç payı (0..1).
Frenlemede (p_dem < 0) bu değer kullanılmaz: geri kazanılan enerji simülasyonda
sadece süperkapasitöre (HESS) gider.
"""


def battery_only(p_dem, soc_bat, soc_sc):
    """Süperkapasitör yok: tüm güç bataryadan."""
    return 0.0


def make_rule_based(p_thresh=3500.0, soc_min=0.30, p_sc_max=2000.0):
    """Eşik tabanlı kural: talep p_thresh'i aşarsa fazlasını süperkapasitör karşılar.

    Kurallar:
      1) p_dem <= p_thresh: batarya karşılar.
      2) p_dem >  p_thresh: batarya p_thresh'e kadar, fazlası süperkapasitör
         (SC_SoC > soc_min ise). SC gücü en fazla p_sc_max (makalede SC en fazla
         ~1,8-2 kW veriyor).
    """
    def controller(p_dem, soc_bat, soc_sc):
        if p_dem > p_thresh and soc_sc > soc_min:
            return min(p_dem - p_thresh, p_sc_max) / p_dem
        return 0.0
    return controller
