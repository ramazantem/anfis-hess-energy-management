"""ANFIS (Sugeno Tip-1, 1. derece), 3 giriş, 3x3x5 = 45 kural. Yalnızca NumPy ile.

Makale: B_SoC 3 MF, SC_SoC 3 MF, P_D 5 MF, 45 kural; MF parametreleri geri yayılımla,
kural (sonuç) parametreleri en küçük kareler (LSE) ile öğreniliyor (hibrit öğrenme).
Makale eğitim verisinin kaynağını BELİRTMİYOR; burada eğitim verisi FLC çıkışından üretilir.

Bu projede Gauss MF + ızgara (grid) bölümleme kullanılır (makalede kümeleme ile kural çıkarımı
ve trapezoidal MF'ler var; bu bir sadeleştirmedir).
Girişler ölçeklenir: B_SoC ve SC_SoC 0..1, P_D kW.
"""
import json
import numpy as np


def _gauss(x, c, s):
    return np.exp(-0.5 * ((x - c) / s) ** 2)


class ANFIS:
    N_MF = (3, 3, 5)

    def __init__(self):
        # başlangıç MF merkezleri / genişlikleri (ölçeklenmiş giriş uzayı)
        self.c = [np.array([0.2, 0.55, 0.9]),
                  np.array([0.3, 0.65, 0.95]),
                  np.array([0.3, 1.3, 2.6, 3.9, 5.2])]
        self.s = [np.array([0.15, 0.15, 0.15]),
                  np.array([0.2, 0.15, 0.1]),
                  np.array([0.5, 0.6, 0.7, 0.6, 0.6])]
        self.theta = None  # (45, 4) sonuç parametreleri
        # kural indeks tablosu
        self.idx = np.array([(i, j, k) for i in range(3) for j in range(3) for k in range(5)])

    # ---- ileri yön ----
    @staticmethod
    def scale(b_pct, s_pct, p_w):
        return np.stack([np.asarray(b_pct) / 100.0, np.asarray(s_pct) / 100.0,
                         np.asarray(p_w) / 1000.0], axis=-1)

    def _firing(self, X, c=None, s=None):
        c = c or self.c
        s = s or self.s
        mu = [_gauss(X[:, d:d + 1], c[d][None, :], s[d][None, :]) for d in range(3)]  # (N, n_d)
        w = mu[0][:, self.idx[:, 0]] * mu[1][:, self.idx[:, 1]] * mu[2][:, self.idx[:, 2]]
        return w / (w.sum(axis=1, keepdims=True) + 1e-12)  # normalize

    def _design(self, X, wn):
        A = np.concatenate([X, np.ones((len(X), 1))], axis=1)  # (N, 4)
        return (wn[:, :, None] * A[:, None, :]).reshape(len(X), -1)  # (N, 180)

    def predict(self, X, c=None, s=None, theta=None):
        wn = self._firing(X, c, s)
        th = self.theta if theta is None else theta
        return self._design(X, wn) @ th.reshape(-1)

    # ---- hibrit öğrenme ----
    def _lse(self, X, y):
        wn = self._firing(X)
        D = self._design(X, wn)
        th, *_ = np.linalg.lstsq(D, y, rcond=None)
        self.theta = th.reshape(-1, 4)

    def _params(self):
        return np.concatenate([*self.c, *self.s])

    def _set_params(self, v):
        o = 0
        for d in range(3):
            n = self.N_MF[d]; self.c[d] = v[o:o + n].copy(); o += n
        for d in range(3):
            n = self.N_MF[d]; self.s[d] = np.maximum(v[o:o + n], 0.03); o += n

    def fit(self, X, y, epochs=60, lr=0.05, verbose=True):
        """Her epoch: (1) LSE ile sonuç parametreleri, (2) gradyan ile MF parametreleri."""
        history = []
        for ep in range(epochs):
            self._lse(X, y)
            rmse = float(np.sqrt(np.mean((self.predict(X) - y) ** 2)))
            history.append(rmse)
            if verbose and (ep % 20 == 0 or ep == epochs - 1):
                print(f"  epoch {ep:3d}  RMSE = {rmse:.4f}")
            v0 = self._params()
            g = np.zeros_like(v0)
            h = 1e-4
            for i in range(len(v0)):  # sayısal gradyan (sonuç parametreleri sabit)
                vp = v0.copy(); vp[i] += h
                vm = v0.copy(); vm[i] -= h
                self._set_params(vp); ep_ = np.mean((self.predict(X) - y) ** 2)
                self._set_params(vm); em_ = np.mean((self.predict(X) - y) ** 2)
                g[i] = (ep_ - em_) / (2 * h)
            self._set_params(v0)
            # geri izlemeli (backtracking) adım
            base = np.mean((self.predict(X) - y) ** 2)
            step = lr
            for _ in range(8):
                self._set_params(v0 - step * g / (np.linalg.norm(g) + 1e-12))
                if np.mean((self.predict(X) - y) ** 2) < base:
                    break
                step *= 0.5
            else:
                self._set_params(v0)
        self._lse(X, y)
        history.append(float(np.sqrt(np.mean((self.predict(X) - y) ** 2))))
        return history

    # ---- simülasyon arayüzü ----
    def controller(self, p_dem, soc_bat, soc_sc):
        X = self.scale([100 * soc_bat], [100 * soc_sc], [min(p_dem, 5700.0)])  # FLC ile aynı evren
        return float(np.clip(self.predict(X)[0], 0.0, 100.0)) / 100.0

    # ---- kaydet / yükle ----
    def save(self, path):
        json.dump({"c": [a.tolist() for a in self.c], "s": [a.tolist() for a in self.s],
                   "theta": self.theta.tolist()}, open(path, "w"), indent=1)

    @classmethod
    def load(cls, path):
        d = json.load(open(path))
        m = cls()
        m.c = [np.array(a) for a in d["c"]]
        m.s = [np.array(a) for a in d["s"]]
        m.theta = np.array(d["theta"])
        return m
