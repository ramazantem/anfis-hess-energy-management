"""Gün 4: özgün katkı. ANFIS + SC enerji rezervi yönetimi ve yeniden şarj.

Çalıştırma (depo kökünden):  python3 -m experiments.run_proposed
Gereken: önce  python3 -m experiments.run_flc_anfis  (results/anfis_model.json üretir).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.drive_cycle import repeated_cycle
from src.simulation import simulate
from src.baseline.rule_based import make_rule_based
from src.fuzzy.flc import FLC
from src.fuzzy.anfis import ANFIS
from src.proposed.reserve import ReserveManaged

P_AUX, DOD, DT = 600.0, 0.80, 1.0


def main():
    t, v = repeated_cycle(7, DT)
    anfis = ANFIS.load("results/anfis_model.json")
    flc = FLC()
    ref = simulate(v, DT, lambda *a: 0.0, use_sc=False, p_aux=P_AUX)

    def run(c):
        return simulate(v, DT, c, p_aux=P_AUX)

    def rng(r):
        return r["distance_km"] * DOD / r["soc_drop"]

    methods = {
        "Sadece batarya": ref,
        "Kural tabanlı HESS": run(make_rule_based()),
        "FLC (Mamdani)": run(flc.controller),
        "ANFIS (Sugeno)": run(anfis.controller),
        "ANFIS + rezerv (önerilen)": run(ReserveManaged(anfis.controller)),
        "FLC + rezerv (önerilen)": run(ReserveManaged(flc.controller)),
    }
    print(f"{'Yöntem':28s} {'Maks akım':>10s} {'Azalma':>8s} {'RMS akım':>9s} {'Menzil':>9s} {'SC min':>7s}")
    lines = []
    for n, r in methods.items():
        red = 100 * (1 - r["peak_i_bat"] / ref["peak_i_bat"])
        smin = r["soc_sc"].min() if n != "Sadece batarya" else float("nan")
        print(f"{n:28s} {r['peak_i_bat']:8.1f} A {red:7.1f}% {r['rms_i_bat']:7.2f} A {rng(r):7.2f} km {smin:7.2f}")
        lines.append([r["peak_i_bat"], red, r["rms_i_bat"], rng(r), smin])
    np.savetxt("results/proposed_table.csv", lines, delimiter=",", fmt="%.3f",
               header="maks_akim_A,azalma_yuzde,rms_akim_A,menzil_km,SC_SoC_min (satirlar: " + " | ".join(methods) + ")")

    # yeniden şarj gücü taraması: tepe akım azalması ve menzil arasındaki ödünleşim
    print("\nYeniden şarj gücü taraması (ANFIS + rezerv):")
    prs = [0, 200, 400, 600, 800, 1000, 1500]
    sweep = []
    for pr in prs:
        r = run(ReserveManaged(anfis.controller, p_rech=pr))
        red = 100 * (1 - r["peak_i_bat"] / ref["peak_i_bat"])
        sweep.append((pr, red, rng(r), r["soc_sc"].min()))
        print(f"  p_rech {pr:5d} W: akım azalması {red:5.1f}%  menzil {rng(r):6.2f} km  SC min {r['soc_sc'].min():.2f}")
    np.savetxt("results/proposed_sweep.csv", sweep, delimiter=",", fmt="%.3f",
               header="p_rech_W,azalma_yuzde,menzil_km,SC_SoC_min")

    col = dict(zip(methods, ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]))
    fig, ax = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    for n in ["Sadece batarya", "ANFIS (Sugeno)", "ANFIS + rezerv (önerilen)"]:
        r = methods[n]
        ax[0].plot(t, r["i_bat"], lw=.8, label=n, color=col[n])
        ax[1].plot(t, r["soc_bat"] * 100, lw=.8, label=n, color=col[n])
        if n != "Sadece batarya":
            ax[2].plot(t, r["soc_sc"] * 100, lw=.8, label=n, color=col[n])
    ax[0].set_ylabel("Batarya akımı (A)"); ax[1].set_ylabel("B_SoC (%)"); ax[2].set_ylabel("SC_SoC (%)")
    ax[2].set_xlabel("Zaman (s)")
    for a in ax:
        a.legend(fontsize=8); a.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("results/proposed_simulation.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.plot([s[2] for s in sweep], [s[1] for s in sweep], "o-")
    for s in sweep:
        ax.annotate(f"{s[0]} W", (s[2], s[1]), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax.set_xlabel("Menzil (km)"); ax.set_ylabel("Tepe akım azalması (%)")
    ax.set_title("Yeniden şarj gücü: tepe akım / menzil ödünleşimi"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig("results/proposed_tradeoff.png", dpi=130); plt.close(fig)
    print("\nKaydedildi: results/proposed_table.csv, proposed_sweep.csv, proposed_simulation.png, proposed_tradeoff.png")


if __name__ == "__main__":
    main()
