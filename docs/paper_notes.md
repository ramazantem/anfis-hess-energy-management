# Makale Analizi

## Künye
- Başlık: Adaptive neuro fuzzy inference system based optimized energy management strategy for the power integration of battery and supercapacitor in electric vehicle
- Yazarlar: N. Kumaresan, A. Rammohan (Vellore Institute of Technology, Hindistan)
- Dergi: Journal of Energy Storage, Cilt 126, Makale no: 117073 (Elsevier), 2025
- DOI: 10.1016/j.est.2025.117073
- Anahtar kelimeler: energy management strategy, lithium-ion battery, neural network, state of charge, supercapacitor
- Sorumlu yazar: rammohan.a@vit.ac.in
- Veri erişimi: "Data will be made available on request" (açık veri yok)

## 1. Problem
Elektrikli araçlarda menzil sınırlı, batarya yüksek mekanik ve ısıl strese maruz kalıyor.
Batarya + süperkapasitör (HESS) bu sorunu azaltır ama gücü iki kaynak arasında
paylaştıracak bir enerji yönetim stratejisi (EMS) gerekir. Makale, batarya akımını,
enerji tüketimini (ECR) ve batarya yaşlanmasını azaltmak için ANFIS tabanlı bir EMS
öneriyor ve bataryalı-tek sistem ile FLC tabanlı EMS ile karşılaştırıyor.

## 2. Sistem topolojisi
- Aktif kontrollü HESS (pasif ve yarı-aktif değil).
- Batarya: tek yönlü boost dönüştürücü üzerinden DC baraya.
- Süperkapasitör: çift yönlü buck-boost dönüştürücü (ivmelenmede boost, frenlemede buck).
- Dönüştürücüler PID destekli akım kontrol modunda; PWM sinyalleri FLC/ANFIS'in
  ürettiği güç katsayılarından üretiliyor.
- DC bara -> inverter -> PMSM motor. SOC ve SOH tahmini: adaptif Kalman filtresi.
- Frenlemede enerjinin sadece %20'si geri kazanılıp süperkapasitöre şarj ediliyor.
- Test aracı: elektrikli iki tekerlekli (E2W).

## 3. Araç parametreleri (Tablo 3)
| Parametre | Değer |
|---|---|
| Toplam kütle | 200 kg |
| Sürükleme katsayısı Cd | 0,22 |
| Yuvarlanma direnci katsayısı | 0,015 |
| Aktarma verimi | 0,95 |
| Dişli oranı | 7,8:1 |
| Tekerlek yarıçapı | 0,233 m |
| Ön alan | 0,875 m2 |
| Eğim kabiliyeti | 20 derece |
| Ortam sıcaklığı | 22 C |
| PMSM motor tepe gücü / torku | 6,2 kW / 26 N-m |

## 4. Batarya parametreleri
- 3,7 kWh, 52,5 V, 70 Ah. Hücre: 3,1 V, 3,6 Ah. Boşalma derinliği: %80 (100 -> 20).
- Makale 14 seri x 22 paralel diyor, ama 3,1 V ve 3,6 Ah hücreden bu çıkmıyor
  (14 x 3,1 = 43,4 V; 22 x 3,6 = 79,2 Ah). Hesaplarda paket değerlerini (52,5 V / 70 Ah /
  3,7 kWh) kullanacağız.

## 5. Süperkapasitör parametreleri
- 48 V, 406 F, 0,012 ohm. Hücre: 2,7 V, 500 F, 0,01 ohm. 18 seri x 15 paralel.
- Maksimum güç = V^2 / (4R) = 48 kW (teorik). Enerji = 0,5 x C x V^2 = 130 Wh.
- Başlangıç SC_SoC = %100. Pratikte SC'nin verdiği güç en fazla 1,8-2 kW.

## 6. Sürüş çevrimi
- Standart çevrim değil, gerçek ölçülmüş E2W hız verisi (Şekil 8): 900 s, 12,4 km,
  tepe hız 82,9 km/h, ortalama hız 47,5 km/h, ivme -2,655 ile +2,723 m/s2.
- Bu çevrim, batarya %80 boşalana kadar tekrarlanıyor (grafikler ~7000 s'ye uzanıyor).
- Motor güç talebi: en fazla 5600 W, en fazla geri kazanım 1100 W.
- Veri açık değil. Yazara e-posta atıldı, beklemeden Şekil 8'e benzeyen çevrim kuruldu.

## 7. Karşılaştırılan yöntemler
(a) Sadece batarya, (b) FLC tabanlı EMS (Mamdani), (c) ANFIS tabanlı EMS (Sugeno).
Karşılaştırma hem simülasyonda hem laboratuvar düzeneğinde (motor + yük, Şekil 7).

## 8. FLC ve ANFIS yapısı
Giriş değişkenleri (ikisi için de): B_SoC, SC_SoC, P_D (motorun güç talebi).
Üyelik fonksiyonları: giriş MF'leri kullanıcı tanımlı, trapezoidal.
| | FLC (Mamdani Tip 1) | ANFIS (Sugeno Tip 1) |
|---|---|---|
| B_SoC | 3 MF (düşük, orta, yüksek) | 3 MF |
| SC_SoC | 3 MF | 3 MF |
| P_D | 4 MF (düşük, orta, yüksek, rejenerasyon) | 5 MF (düşük, orta, yüksek, yüksek ve düşük rejenerasyon) |
| Kural sayısı | 36 (3x3x4) | 45 (3x3x5) |
- Çıkış: batarya güç katsayısı ve süperkapasitör güç katsayısı (0-100 arası, yaklaşık
  11-12 üçgen MF). Katsayının güce nasıl çevrildiği makalede açıklanmamış.
- Kurallar ve yapı: Subtractive Clustering (SC) ile belirleniyor. Kural ağırlığı 1,
  bağlayıcılar AND/OR.
- ANFIS mimarisi 6 katman: bulanıklaştırma, bilgi tabanı, çıkarım, öğrenme/eğitim,
  durulaştırma, çıkış. Geri bildirim: sapma küçükse çıkışa verilir, büyükse çıkarım
  parametreleri güncellenir.
- Öğrenme: MF'ler geri yayılım (backpropagation) ile, kurallar en küçük kareler (LSE) ile.
- Eğitim verisi nereden geldi: BELİRTİLMEMİŞ.

Şekil 4'ten (PDF sayfa 6) okunan yaklaşık trapez köşeleri (grafikten okundu, yaklaşık):
- B_SoC (%): Düşük (0,0)-(20,1)-(30,1)-(40,0); Orta (40,0)-(50,1)-(60,1)-(70,0);
  Yüksek (70,0)-(80,1)-(90,1)-(100,0)
- SC_SoC (%): Düşük (0,0)-(20,1)-(40,1)-(60,0); Orta (55,0)-(65,1)-(75,1)-(85,0);
  Yüksek (80,0)-(87,1)-(92,1)-(100,0)
- P_D (W): Rejenerasyon (-5000,0)-(-4000,1)-(-2000,1)-(0,0); Düşük (0,0)-(1000,1)-(1500,1)-(2000,0);
  Orta (2000,0)-(3000,1)-(3500,1)-(4000,0); Yüksek (4000,0)-(4500,1)-(5000,1)-(5700,0)

## 9. Optimizasyon kısmı
Başlıktaki "optimized" kelimesi ANFIS'in öğrenmesini (MF ve kural parametrelerinin
eğitimle ayarlanması) ifade ediyor. PSO, GA, DP gibi ayrı bir optimizasyon algoritması YOK.

## 10. Raporlanan metrikler
Batarya maksimum akımı, hücre sıcaklığı, B_SoC düşüş hızı, SoH, SC_SoC davranışı,
menzil, enerji tüketim oranı (ECR), batarya ve SC güç profilleri.

## 11. Ana sonuçlar
| Metrik | Sadece batarya | FLC | ANFIS |
|---|---|---|---|
| Maks. batarya akımı | 130 A | 98 A (-%24,61) | 97 A (-%25,38) |
| Hücre sıcaklığı artışı | 22 -> 24 C | +1,95 C (-%2,5) | +1,90 C (-%5) |
| B_SoC boşalma hızı azalması | referans | %6,76 | %8,73 |
| Menzil | 88,95 km | 94,34 km (+%6) | 95,975 km (+%7,89) |
| ECR | 41,59 | 39,21 (%6) | 38,55 (%7,89) |
| Maks. batarya gücü | | 4200 W | 4200 W |
| Maks. SC gücü | | 2000 W | 1800 W |
- SoH tüm yapılarda %99,98'in üstünde, ANFIS en az bozulma.
- SC_SoC: %100'den başlıyor, ~3000-4000 s'de yaklaşık %30'a düşüyor ve orada kalıyor.

## 12. Sınırlılıklar ve tutarsızlıklar (kritik okuma)
- ANFIS eğitim verisinin kaynağı belirtilmemiş, veri sadece istek üzerine paylaşılıyor.
- Tek sürüş çevrimi (tekrarlı), genelleme testi yok.
- DP, MPC gibi optimizasyon tabanlı yöntemlerle karşılaştırma yok.
- SC enerjisi ~4000 s sonra tükeniyor ve yeniden şarj stratejisi yok (özgün katkı fırsatı).
- ECR yüzdeleri tutarsız görünüyor: 41,59 -> 38,55 gerçekte %7,31 azalma (%7,89 menzil
  artışının aynısı yazılmış). FLC için 41,59 -> 39,21 = %5,72 (makale %6 diyor).
- ECR birimi metinde kWh/km, Şekil 19'da Wh/km. Doğrusu Wh/km (3,7 kWh / 41,59 Wh/km = 89 km).
- Şekil 2 ve 3'ün başlıkları yer değiştirmiş: Şekil 2 çıkış MF'lerini (batarya ve SC
  katsayısı), Şekil 3 ise giriş MF'lerini ve Mamdani yapısını gösteriyor. Giriş MF'lerinin
  asıl grafikleri Şekil 4'te (başlığı "FLC system using Mamdani Type 1 fuzzifier").
- ANFIS katman diyagramı (Şekil 5) "Fuzzy rules (36 Rules)" yazıyor, metin ise ANFIS için
  45 kural diyor. Tutarsızlık; metindeki 45'i esas alacağız.
- FLC'den ANFIS'e geçişte kural sayısı 36'dan 45'e çıkıyor (P_D için 4'ten 5 MF), yani
  karşılaştırma tam adil değil.
- Batarya paket hesabı (14s22p) tablo değerleriyle uyuşmuyor (bölüm 4).

## Gün 2: Modelleme Varsayımları ve Sınırlılıklar
- Sürüş çevrimi: Makalenin hız verisi paylaşılmadığı için Şekil 8'e bakılarak yaklaşık
  bir profil kuruldu (12,05 km, tepe 81 km/h, ort.