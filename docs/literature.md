# Literatür Taraması

Konu: Batarya/süperkapasitör (HESS) enerji yönetimi, bulanık mantık ve ANFIS.

| # | Makale | Yıl | Yöntem | Bu projeyle ilişkisi |
|---|--------|-----|--------|----------------------|
| 1 | Gunjal - Performance Enhancement of Hybrid Energy Storage System for Electric Vehicle Using Intelligent-Based Controller (Int. J. Energy Research) | 2025 | ANN ve ANFIS, kural tabanlı denetleyici verisiyle eğitilmiş | Baseline -> ANFIS yapısının doğrudan örneği; yöntemimiz buna benziyor |
| 2 | Li, Zhang, Yang, Wang - A Power Split Strategy for a Vehicular HESS Using ANFIS (IEEE ICARM) | 2023 | ANFIS, çevrimdışı optimizasyon sonuçlarından öğreniyor; düşük geçiren filtreyle karşılaştırma | Optimizasyon verisiyle ANFIS eğitimi ve bilinmeyen sürüş çevrimlerinde genelleme |
| 3 | Jbari, Haidoury, Askour, Idrissi - Fuzzy Logic Controller for an EV's Dual-Source Hybridization (E3S Web of Conf.) | 2021 | Bulanık mantık + güç filtreleme, NEDC | Klasik bulanık baseline için referans |
| 4 | Jbari, Askour, Idrissi - Fuzzy logic-based EMS on dual-source hybridization for a pure EV (IJECE) | 2022 | Bulanık mantık + güç filtreleme, aktif paralel topoloji, NEDC | Sistem topolojisi ve bulanık kural tasarımı |
| 5 | Mounica, Obulesu - Hybrid Power Management Strategy with Fuel Cell, Battery, and Supercapacitor (Energies) | 2022 | ANFIS + ECMS, HWFET ve WLTP çevrimleri | ANFIS'in başka bir HESS yapısında kullanımı, farklı sürüş çevrimleri |
| 6 | Lin - A Control Strategy for Capacity Allocation of Hybrid Energy Storage System Based on Hierarchical Processing of Demand Power (arXiv 2010.01277) | 2020 | Bulanık denetleyici + Savitzky-Golay filtresi | Metrik örneği: batarya tepe akımı ve çevrim ömrü |
| 7 | Wangsupphaphol, Idris, Jusoh, Muhamad, Phichaisawat - A Systematic Review of Energy Management System for Battery/Supercapacitor Electric Vehicle Applications (Sustainability 15(14), 11200) | 2023 | Derleme | Genel arka plan, HESS topolojileri ve kural/optimizasyon tabanlı EMS sınıflandırması |


## Referans Makale
   Kumaresan, N. ve Rammohan, A. (2025). Adaptive neuro fuzzy inference system based
   optimized energy management strategy for the power integration of battery and
   supercapacitor in electric vehicle. Journal of Energy Storage, 126, 117073.
   https://doi.org/10.1016/j.est.2025.117073

## Notlar
- Ortak metrikler: batarya tepe akımı, RMS akım, kapasite kaybı, SOC.
- Sık kullanılan sürüş çevrimleri: NEDC, UDDS, WLTP, HWFET.