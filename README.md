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
mekanik ve ısıl olarak zorlar. Batarya ile süperkapasitörü (SC) birlikte kullanan
hibrit enerji depolama sisteminde (HESS), gücün iki kaynak arasında nasıl
paylaştırılacağı bir enerji yönetimi problemidir. Bu projede referans makaledeki
bulanık mantık (FLC) ve ANFIS tabanlı enerji yönetimi yeniden gerçekleştirilmiş,
kural tabanlı bir baseline ile karşılaştırılmış ve makalenin eksik bıraktığı
süperkapasitör enerji rezervi/yeniden şarj konusunda bir geliştirme önerilmiştir.

## Kullanılan Yöntem
- **Sistem modeli:** Elektrikli iki tekerlekli araç (makale Tablo 3 parametreleri), yol yükü
  tabanlı güç talebi, coulomb sayımlı Li-ion batarya (52,5 V, 70 Ah), SC (48 V, 406 F).
  Frenlemede enerjinin yalnızca %20'si geri kazanılıp SC'ye yönlendirilir (makaleyle aynı).
- **Baseline:** Sadece batarya ve eşik tabanlı kural (talep 3,5 kW'ı aşarsa fazlasını SC karşılar).
- **FLC (Mamdani):** Makaledeki yapı yeniden kurulmuştur (aşağıda).
- **ANFIS (Sugeno):** Hibrit öğrenme: sonuç parametreleri en küçük kareler (LSE), üyelik
  fonksiyonu parametreleri gradyan inişi ile öğrenilir. NumPy ile sıfırdan yazılmıştır.
- **Önerilen yöntem:** Herhangi bir denetleyiciyi sarmalayan SC rezerv yönetimi (aşağıda).

## Bulanık Sistem Yapısı
| | FLC (Mamdani Tip-1) | ANFIS (Sugeno Tip-1) |
|---|---|---|
| Girişler | B_SoC, SC_SoC, P_D | B_SoC, SC_SoC, P_D |
| Üyelik fonksiyonu (MF) | B_SoC 3, SC_SoC 3, P_D 4 (trapezoidal, makale Şekil 4'ten) | 3, 3, 5 (Gauss, öğrenilir) |
| Kural sayısı | 36 (3x3x4) | 45 (3x3x5) |
| Çıkış | SC güç payı (%), 11 üçgen MF | SC güç payı (%), 1. derece Sugeno |
| Çıkarım | min-min-max, ağırlık merkezi | ağırlıklı ortalama |

Girişler: B_SoC (batarya doluluğu), SC_SoC (süperkapasitör doluluğu), P_D (motorun güç talebi).
Çıkış: gücün ne kadarını SC'nin karşılayacağı, kalanı batarya karşılar.

## Veri Seti
Makalenin gerçek E2W hız verisi paylaşılmadığı için (Data available on request), makale
Şekil 8'e benzer yaklaşık bir sürüş çevrimi kodla üretilmiştir (`src/models/drive_cycle.py`).
900 s, 12,05 km, tepe hız 81 km/h, ortalama hız 48,1 km/h; 7 kez tekrarlanır (6300 s).
ANFIS eğitim verisi 3000 rastgele (B_SoC, SC_SoC, P_D) örneği ve FLC'nin çıkışından oluşur
(makale eğitim verisinin kaynağını belirtmiyor). Yazara veri istemek için e-posta gönderilmiştir.

## Kurulum
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Çalıştırma
Depo kökünden, sırayla:

    python3 -m experiments.run_baseline      # Gün 2: sadece batarya ve kural tabanlı baseline
    python3 -m experiments.run_flc_anfis     # Gün 3: FLC + ANFIS (results/anfis_model.json üretir)
    python3 -m experiments.run_proposed      # Gün 4: önerilen yöntem ve parametre taraması

Her betik terminale özet tablo yazar ve `results/` klasörüne grafik/CSV kaydeder.

## Reproduction Deneyleri
Makale sonuçları ile bu projenin simülasyonu (7 x 900 s, %80 boşalma derinliği menzili):

| Yöntem | Maks. akım (A) | Azalma | Menzil (km) |
|---|---|---|---|
| Makale: sadece batarya | 130 | - | 88,95 |
| Makale: FLC | 98 | %24,61 | 94,34 |
| Makale: ANFIS | 97 | %25,38 | 95,975 |
| Bu proje: sadece batarya | 133,7 | - | 88,42 |
| Bu proje: kural tabanlı HESS | 85,6 | %36,0 | 88,54 |
| Bu proje: FLC | 133,7 | %0 | 92,81 |
| Bu proje: ANFIS | 133,7 | %0 | 92,80 |

- Sadece batarya sistemi makaleyle uyumlu (kalibrasyonla: 133,7 A / 88,42 km, makale 130 A / 88,95 km).
- Menzil artışı makaleye yakın (+%5, makale +%6/+%7,89) ve SC_SoC makaledeki gibi ~3000 s'de %30'a iniyor.
- ANFIS, FLC'yi iyi taklit eder (doğrulama RMSE ≈ 2 yüzde puan, simülasyonda SC gücü farkı ort. 23 W).
- Makalenin %25'lik tepe akım azalması bu verilerle **yeniden üretilemedi** (aşağıda neden).

## Özgün Katkı: SC Enerji Rezervi Yönetimi ve Yeniden Şarj
**Gözlem:** FLC/ANFIS, SC enerjisini orta güçlerde de harcar. SC ~3000 s'de %30'a iner ve sonraki
çevrimlerin tepe akımlarını karşılayamaz. Makalede SC için yeniden şarj stratejisi de yoktur.

**Öneri** (`src/proposed/reserve.py`, herhangi bir denetleyiciyi sarmalar):
1. **Rezerv:** SC_SoC < %60 iken SC yalnızca tepe taleplerde (P_D >= 4000 W) kullanılır.
2. **Yeniden şarj:** Talep düşükken (< 1500 W) ve SC_SoC < %95 iken batarya SC'yi şarj eder.

## Deneysel Sonuçlar
| Yöntem | Maks. akım | Azalma | RMS akım | Menzil | SC_SoC min |
|---|---|---|---|---|---|
| Sadece batarya | 133,7 A | 0 | 36,25 A | 88,42 km | - |
| Kural tabanlı HESS | 85,6 A | %36,0 | 35,44 A | 88,54 km | 0,99 |
| FLC | 133,7 A | %0 | 33,65 A | 92,81 km | 0,30 |
| ANFIS | 133,7 A | %0 | 33,68 A | 92,80 km | 0,30 |
| **ANFIS + rezerv (önerilen)** | **89,8 A** | **%32,9** | 32,56 A | 91,38 km | 0,63 |
| FLC + rezerv (önerilen) | 90,0 A | %32,7 | 33,32 A | 91,64 km | 0,59 |

Yeniden şarj gücü taraması (ANFIS + rezerv):

| Şarj gücü | 0 W | 400 W | 600 W | 800 W | 1000 W |
|---|---|---|---|---|---|
| Akım azalması | %31,8 | %33,2 | %32,9 | %44,4 | %44,4 |
| Menzil (km) | 91,54 | 91,75 | 91,38 | 90,62 | 90,48 |

Yorum: Tepe akım azalmasının büyük kısmı rezerv kuralından gelir. Şarj gücü arttıkça
tepe akım daha da düşer ama menzil azalır, yani bir ödünleşim vardır. Önerilen yöntem,
kural tabanlı baseline'ın tepe akım azalmasına yaklaşırken menzili sadece batarya
sistemine göre ~%3 artırır; baseline menzil kazanmaz.

Grafikler: `results/baseline_simulation.png`, `membership_functions.png`, `anfis_training.png`,
`flc_anfis_simulation.png`, `proposed_simulation.png`, `proposed_tradeoff.png`.

## Sınırlılıklar
- Makalenin gerçek sürüş verisi yok; kullanılan çevrim yaklaşıktır ve makaledekinden daha yumuşaktır
  (en yüksek ivme 0,94 m/s2, makalede 2,72).
- Makale kural tablosunu yayımlamıyor; 36 FLC kuralı bu projede mühendislik mantığıyla yazılmıştır,
  makaledekiyle aynı olduğu iddia edilmez. ANFIS eğitim verisi de FLC çıkışıdır (varsayım).
- ANFIS'te Gauss MF ve ızgara bölümleme kullanıldı (makale trapezoidal MF ve kümeleme kullanıyor).
- 600 W sabit yardımcı yük, 0,05 ohm batarya iç direnci ve SC alt sınırı %30 varsayımdır (makalede yok).
- Makalenin %25'lik tepe akım