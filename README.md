# ANFIS Tabanlı Batarya/Süperkapasitör Enerji Yönetimi

**Ders:** Bulanık Mantık  
**Öğrenci:** Ramazan Temel (1306220093)

## Referans Makale
Kumaresan, N. ve Rammohan, A. (2025). Adaptive neuro fuzzy inference system based
optimized energy management strategy for the power integration of battery and
supercapacitor in electric vehicle. Journal of Energy Storage, 126, 117073.
https://doi.org/10.1016/j.est.2025.117073

## Problem Tanımı
Elektrikli araçlarda yalnızca batarya kullanmak, ani güç taleplerinde bataryayı
mekanik ve ısıl olarak zorlar. Batarya ile süperkapasitörü birlikte kullanan
hibrit enerji depolama sisteminde (HESS), gücün iki kaynak arasında nasıl
paylaştırılacağı bir enerji yönetimi problemidir. Bu projede referans makaledeki
ANFIS tabanlı enerji yönetimi yeniden gerçekleştirilecek, kural tabanlı bir
baseline ile karşılaştırılacak ve geliştirilecektir.

## Proje Durumu
- [x] Gün 1: İskelet, literatür, makale analizi
- [x] Gün 2: Veri, sistem modeli, baseline
- [ ] Gün 3: ANFIS reproduction
- [ ] Gün 4: Özgün katkı ve deneyler
- [ ] Gün 5: Sonuçlar, rapor, sunum

## Klasör Yapısı
- `data/` sürüş çevrimleri
- `src/` modeller, baseline, ANFIS, önerilen yöntem
- `experiments/` deney betikleri
- `results/` grafikler ve tablolar
- `docs/` makale notları ve literatür
- `report/` rapor

## Kurulum
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Çalıştırma
    python3 -m experiments.run_baseline

Çıktı: terminalde özet tablo, `results/baseline_simulation.png` grafiği.

## Veri Seti
Makalenin gerçek E2W hız verisi paylaşılmadığı için (Data available on request) Şekil 8'e
benzer yaklaşık bir sürüş çevrimi kodla üretilmiştir (`src/models/drive_cycle.py`).
900 s, 12,05 km, tepe hız 81 km/h, ortalama hız 48,1 km/h; 7 kez tekrarlanır.

## Baseline Sonuçları (Gün 2)
| Metrik | Sadece batarya | Kural tabanlı HESS | Makale (sadece batarya / ANFIS) |
|---|---|---|---|
| Maks. batarya akımı | 133,7 A | 85,6 A | 130 A / 97 A |
| Menzil (%80 DoD) | 88,4 km | 88,5 km | 88,95 km / 95,975 km |

## Yapılacaklar
- Kullanılan yöntem ve Bulanık Mantık sistem yapısı
- Reproduction deneyleri (ANFIS)
- Özgün katkı
- Deneysel sonuçlar
- Sınırlılıklar
- Kaynaklar