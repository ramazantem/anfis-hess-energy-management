"""Önerilen yöntem (özgün katkı): SC enerji REZERVİ yönetimi + yeniden şarj.

Gözlem (Gün 3): FLC/ANFIS süperkapasitörün enerjisini orta güçlerde de harcıyor, SC ~3000 s'de
%30'a iniyor ve sonraki çevrimlerin tepe akımlarını karşılayamıyor. Makalede SC için yeniden
şarj stratejisi yok.

Çözüm, herhangi bir temel denetleyiciyi (FLC veya ANFIS) sarmalar:
  1) Rezerv: SC_SoC < soc_reserve iken yalnızca p_dem >= p_peak (tepe) için SC kullanılır.
  2) Yeniden şarj: p_dem < p_low ve SC_SoC < soc_target iken batarya SC'yi p_rech watt ile şarj eder
     (batarya akımı düşük olduğu anlarda, tepe akımı artırmadan).
"""


class ReserveManaged:
    def __init__(self, base, p_peak=4000.0, soc_reserve=0.60, p_low=1500.0,
                 p_rech=600.0, soc_target=0.95, bat_soc_min=0.30):
        self.base = base
        self.p_peak, self.soc_reserve = p_peak, soc_reserve
        self.p_low, self.p_rech, self.soc_target = p_low, p_rech, soc_target
        self.bat_soc_min = bat_soc_min

    def __call__(self, p_dem, soc_bat, soc_sc):
        if soc_sc < self.soc_reserve and p_dem < self.p_peak:
            return 0.0
        return self.base(p_dem, soc_bat, soc_sc)

    def recharge(self, p_dem, soc_bat, soc_sc):
        if p_dem < self.p_low and soc_sc < self.soc_target and soc_bat > self.bat_soc_min:
            return self.p_rech
        return 0.0
