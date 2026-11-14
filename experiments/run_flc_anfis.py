"""Gün 3: FLC (Mamdani) ve ANFIS (Sugeno) denetleyicilerini kur, eğit, simüle et, karşılaştır.

Çalıştırma (depo kökünden):  python3 -m experiments.run_flc_anfis
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.drive_cycle import repeated_cycle
from src.simulation import simulate
from src.baseline.rule_based import make_rule_based
from src.fuzzy import flc as F
from src.fuzzy.flc import FLC
from src.fuzzy.anfis import ANFIS, _gauss
from src.fuzzy.dataset import make_training_data

P_AUX, DOD, DT = 600.0, 0.80, 1.0   # run_baseline.py ile aynı kalibrasyon


def range_km(res):
    """%80 boşalma derinliğine kadar menzil (7 çevrimlik koşunun SOC düşüşünden)."""
    return res["distance_km"] * DOD / res["soc_drop"]


def main():
    t, v = repeated_cycle(7, DT)

    print("1) ANFIS eğitim verisi (FLC çıkışından)")
    b, s, p, y = make_training_data(3000, seed=0)
    X = ANFIS.scale(b, s, p)
    print("2) ANFIS eğitimi (hibrit: LSE + gradyan)")
    anfis = ANFIS()
    hist = anfis.fit(X, y, epochs=40, lr=0.2)
    anfis.save("results/anfis_model.json")

    # doğrulama verisi (farklı tohum)
    bv, sv, pv, yv = make_training_data(1000, seed=1)
    rmse_val = float(np.sqrt(np.mean((anfis.predict(ANFIS.scale(bv, sv, pv)) - yv) ** 2)))
    print(f"   eğitim RMSE {hist[-1]:.3f}  |  doğrulama RMSE {rmse_val:.3f}  (SC payı, % puan)")

    flc = FLC()
    ctrls = {
        "Sadece batarya": (None, False),
        "Kural tabanlı HESS": (make_rule_based(), True),
        "FLC (Mamdani)": (flc.controller, True),
        "ANFIS (Sugeno)": (anfis.controller, True),
    }
    print("3) Simülasyon (7 x 900 s)")
    out = {}
    for name, (c, use_sc) in ctrls.items():
        out[name] = simulate(v, DT, c or (lambda *a: 0.0), use_sc=use_sc, p_aux=P_AUX)

    ref = out["Sadece batarya"]
    print(f"\n{'Yöntem':22s} {'Maks akım':>10s} {'Azalma':>8s} {'Maks P_bat':>11s} {'Maks P_SC':>10s} {'Menzil':>8s} {'SC_SoC son':>11s}")
    rows = []
    for name, r in out.items():
        red = 100 * (1 - r["peak_i_bat"] / ref["peak_i_bat"])
        rk = range_km(r)
        print(f"{name:22s} {r['peak_i_bat']:8.1f} A {red:7.2f}% {r['peak_p_bat']:9.0f} W {r['peak_p_sc']:8.0f} W {rk:6.2f} km {r['final_soc_sc']:10.2f}")
        rows.append((name, r["peak_i_bat"], red, r["peak_p_bat"], r["peak_p_sc"], rk, r["final_soc_sc"]))
    print("\nİlk çevrimde (SC dolu iken) maks batarya akımı ve SC_SoC'nin %30'a indiği an:")
    for name, r in out.items():
        i1 = np.max(np.abs(r["i_bat"][:900]))
        hit = np.where(r["soc_sc"] <= 0.301)[0]
        when = f"{hit[0]} s" if len(hit) and name != "Sadece batarya" else "-"
        print(f"  {name:22s} ilk çevrim maks {i1:6.1f} A (azalma {100*(1-i1/np.max(np.abs(ref['i_bat'][:900]))):5.2f}%)  SC %30'a: {when}")
    print("\nMakale: sadece batarya 130 A / 88,95 km | FLC 98 A (-24,61%) / 94,34 km | ANFIS 97 A (-25,38%) / 95,975 km")

    # ANFIS-FLC uyumu simülasyon boyunca
    d = np.abs(out["ANFIS (Sugeno)"]["p_sc"] - out["FLC (Mamdani)"]["p_sc"])
    print(f"ANFIS ile FLC SC gücü farkı: ort {d.mean():.1f} W, maks {d.max():.0f} W")

    np.savetxt("results/flc_anfis_table.csv", [r[1:] for r in rows], delimiter=",",
               header="maks_akim_A,azalma_yuzde,maks_Pbat_W,maks_Psc_W,menzil_km,SC_SoC_son", fmt="%.3f")

    # ---- Şekil 1: üyelik fonksiyonları ----
    fig, ax = plt.subplots(2, 3, figsize=(14, 7))
    for j, (title, mfs, xr) in enumerate([("B_SoC (%)", F.B_SOC, (0, 100)),
                                          ("SC_SoC (%)", F.SC_SOC, (0, 100)),
                                          ("P_D (W)", F.P_D, (-5000, 5700))]):
        x = np.linspace(*xr, 600)
        for k, tpl in mfs.items():
            ax[0, j].plot(x, F.trapmf(x, *tpl), label=k)
        ax[0, j].set_title("FLC giriş MF: " + title); ax[0, j].legend(fontsize=7)
    scale = [100, 100, 1000]
    xr_ = [(0, 100), (0, 100), (0, 5700)]
    for j, title in enumerate(["B_SoC (%)", "SC_SoC (%)", "P_D (W)"]):
        x = np.linspace(*xr_[j], 600)
        for k in range(ANFIS.N_MF[j]):
            ax[1, j].plot(x, _gauss(x / scale[j], anfis.c[j][k], anfis.s[j][k]), label=f"MF{k+1}")
        ax[1, j].set_title("ANFIS öğrenilmiş MF: " + title); ax[1, j].legend(fontsize=7)
    fig.tight_layout(); fig.savefig("results/membership_functions.png", dpi=130); plt.close(fig)

    # ---- Şekil 2: eğitim eğrisi ----
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(hist); ax.set_xlabel("epoch"); ax.set_ylabel("RMSE (SC payı, % puan)")
    ax.set_title("ANFIS eğitim hatası"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("results/anfis_training.png", dpi=130); plt.close(fig)

    # ---- Şekil 3: simülasyon karşılaştırması ----
    fig, ax = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    col = dict(zip(out, ["tab:blue", "tab:orange", "tab:green", "tab:red"]))
    for name, r in out.items():
        ax[0].plot(t, r["i_bat"], label=name, lw=.8, color=col[name])
        ax[1].plot(t, r["soc_bat"] * 100, label=name, lw=.8, color=col[name])
        if name != "Sadece batarya":
            ax[2].plot(t, r["soc_sc"] * 100, label=name, lw=.8, color=col[name])
    ax[0].set_ylabel("Batarya akımı (A)"); ax[1].set_ylabel("B_SoC (%)"); ax[2].set_ylabel("SC_SoC (%)")
    ax[2].set_xlabel("Zaman (s)")
    for a in ax: a.legend(fontsize=8); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("results/flc_anfis_simulation.png", dpi=130); plt.close(fig)
    print("\nKaydedildi: results/anfis_model.json, flc_anfis_table.csv, membership_functions.png, anfis_training.png, flc_anfis_simulation.png")


if __name__ == "__main__":
    main()
