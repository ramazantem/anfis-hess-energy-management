"""ANFIS eğitim verisi: FLC'nin çıkışı (makale veri kaynağını belirtmiyor, bu bir varsayımdır)."""
import numpy as np
from src.fuzzy.flc import FLC


def make_training_data(n=4000, seed=0):
    """Rastgele (B_SoC %, SC_SoC %, P_D W) örnekleri; etiket = FLC çıkışı (SC payı, %)."""
    rng = np.random.default_rng(seed)
    b = rng.uniform(20, 100, n)
    s = rng.uniform(20, 100, n)
    p = rng.uniform(0, 5700, n)  # yalnızca çekiş: frenlemede denetleyici çağrılmıyor (simülasyon geri kazanımı doğrudan SC yapıyor)
    flc = FLC()
    y = np.array([flc.output_percent(bi, si, pi) for bi, si, pi in zip(b, s, p)])
    return b, s, p, y
