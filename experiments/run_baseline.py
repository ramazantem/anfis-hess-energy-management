"""Baseline simülasyonu: sadece batarya ve kural tabanlı HESS.

Çalıştırma (proje ana klasöründen):  python3 -m experiments.run_baseline
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.models.drive_cycle import one_cycle, repeated_cycle, cycle_stats
from src.baseline.rule_based import battery_only, make_rule_based
from src.simulation import simulate

ETA_DRIVE = 1.0    # motor+inverter verimi makalede verilmemiş, ek kayıp yok varsayıldı
P_AUX = 600.0      # KALİBRASYON: sabit yardımcı yük (W); batarya-tek menzili ~89 km'ye yaklaştırır
DOD = 0.80         # makale: boşalma derinliği %80
DT = 1.0

t1, v1 = one_cycle(DT)
print("Tek çevrim özeti (makale hedefi: 12,4 km, tepe 82,9, ort. 47,5 km/h):")
for k, x in cycle_stats(t1, v1).items():
    print(f"  {k}: {x:.2f}")

t, v = repeated_cycle(7, DT)
cases = {
    "Sadece batarya": (battery_only, False),
    "Kural tabanlı HESS": (make_rule_based(), True),
}
res = {}
print("\nSonuçlar (7 çevrim, 6300 s):")
for name, (ctrl, use_sc) in cases.items():
    r = simulate(v, DT, ctrl, use_sc=use_sc, eta_drive=ETA_DRIVE, p_aux=P_AUX)
    r["range_km"] = r["distance_km"] / r["soc_drop"] * DOD
    res[name] = r
    print(f"  {name}")
    print(f"    Maks. batarya akımı : {r['peak_i_bat']:.1f} A")
    print(f"    Maks. batarya gücü  : {r['peak_p_bat']:.0f} W")
    print(f"    Maks. SC gücü       : {r['peak_p_sc']:.0f} W")
    print(f"    ECR                 : {r['ecr_wh_km']:.2f} Wh/km")
    print(f"    Menzil (80% DoD)    : {r['range_km']:.1f} km")
    print(f"    Son SC_SoC          : {r['final_soc_sc']:.2f}")

a, b = res["Sadece batarya"], res["Kural tabanlı HESS"]
print("\nKural tabanlı HESS, sadece bataryaya göre:")
print(f"  Maks. akım azalması : %{100*(1-b['peak_i_bat']/a['peak_i_bat']):.2f}  (makale ANFIS: %25,38)")
print(f"  Menzil artışı       : %{100*(b['range_km']/a['range_km']-1):.2f}  (makale ANFIS: %7,89)")

fig, ax = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
ax[0].plot(t, v * 3.6); ax[0].set_ylabel("Hız (km/h)")
ax[1].plot(t, b["p_dem"], label="Talep", lw=0.8)
ax[1].plot(t, b["p_bat"], label="Batarya", lw=0.8)
ax[1].plot(t, b["p_sc"], label="Süperkap.", lw=0.8)
ax[1].set_ylabel("Güç (W)"); ax[1].legend(ncol=3)
ax[2].plot(t, a["i_bat"], label="Sadece batarya", lw=0.8)
ax[2].plot(t, b["i_bat"], label="Kural tabanlı HESS", lw=0.8)
ax[2].set_ylabel("Batarya akımı (A)"); ax[2].legend()
ax[3].plot(t, 100 * b["soc_bat"], label="Batarya SOC (HESS)")
ax[3].plot(t, 100 * a["soc_bat"], label="Batarya SOC (tek)", ls="--")
ax[3].plot(t, 100 * b["soc_sc"], label="SC SOC")
ax[3].set_ylabel("SOC (%)"); ax[3].set_xlabel("Zaman (s)"); ax[3].legend()
plt.tight_layout()
os.makedirs("results", exist_ok=True)
plt.savefig("results/baseline_simulation.png", dpi=150)
print("\nGrafik kaydedildi: results/baseline_simulation.png")
