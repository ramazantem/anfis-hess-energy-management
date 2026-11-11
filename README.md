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
- [x] Gün 3: ANFIS reproduction
- [x] Gün 4: Özgün katkı ve deneyler
- [x] Gün 5: Sonuçlar, rapor, sunum

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

