"""HESS simülasyon motoru."""
import numpy as np
from src.models.vehicle import power_demand
from src.models.storage import Battery, Supercap

REGEN_FRAC = 0.20  # makale: frenleme enerjisinin sadece %20'si geri kazanılıyor


def simulate(v, dt, controller, use_sc=True, eta_drive=1.0, p_aux=0.0, regen_frac=REGEN_FRAC):
    """Simülasyonu çalıştırır, sonuçları sözlük olarak döner.

    use_sc=False: sadece batarya sistemi (frenleme enerjisinin %20'si bataryaya gider).
    use_sc=True : HESS (frenleme enerjisinin %20'si süperkapasitöre gider).
    """
    p_dem = power_demand(v, dt, eta_drive=eta_drive, p_aux=p_aux)
    bat, sc = Battery(), Supercap()
    n = len(v)
    p_bat = np.zeros(n); p_sc = np.zeros(n)
    i_bat = np.zeros(n); soc_b = np.zeros(n); soc_s = np.zeros(n)

    for k in range(n):
        p = p_dem[k]
        if p >= 0:
            share = controller(p, bat.soc, sc.soc) if use_sc else 0.0
            ps = sc.limit(share * p) if use_sc else 0.0
            rech = getattr(controller, "recharge", None)  # isteğe bağlı: bataryadan SC'yi yeniden şarj
            if use_sc and rech is not None and ps == 0.0:
                ps = sc.limit(-rech(p, bat.soc, sc.soc))  # negatif = SC şarj olur
            pb = p - ps
        else:
            recovered = regen_frac * p  # negatif
            if use_sc:
                ps = sc.limit(recovered)
                pb = recovered - ps
            else:
                ps, pb = 0.0, recovered
        i_bat[k] = bat.step(pb, dt)
        if use_sc:
            sc.step(ps, dt)
        p_bat[k], p_sc[k] = pb, ps
        soc_b[k], soc_s[k] = bat.soc, sc.soc

    dist_km = np.sum(v) * dt / 1000
    e_bat_wh = np.sum(p_bat) * dt / 3600
    return {
        "p_dem": p_dem, "p_bat": p_bat, "p_sc": p_sc, "i_bat": i_bat,
        "soc_bat": soc_b, "soc_sc": soc_s,
        "peak_i_bat": np.max(np.abs(i_bat)),
        "peak_p_bat": p_bat.max(), "peak_p_sc": p_sc.max(),
        "rms_i_bat": np.sqrt(np.mean(i_bat**2)),
        "ecr_wh_km": e_bat_wh / dist_km,
        "soc_drop": 1.0 - soc_b[-1],
        "final_soc_sc": soc_s[-1],
        "distance_km": dist_km,
        "bat_loss_wh": bat.loss_j / 3600,
        "e_total_wh": e_bat_wh,
    }
