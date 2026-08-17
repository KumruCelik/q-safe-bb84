# Q-SAFE: BB84 Kuantum Anahtar Dağıtımı Simülasyonu

Kuantum fiziği ilkelerine dayanan BB84 protokolünün Python ve Qiskit tabanlı
simülasyonu. Alice-Bob anahtar değişimi, Eve saldırıları, kanal gürültüsü ve
hata düzeltme mekanizmalarını uçtan uca modeller.

> TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı
> kapsamında geliştirilmektedir.

---

## İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Modüller](#modüller)
- [Deney Sonuçları](#deney-sonuçları)
- [Teknolojiler](#teknolojiler)

---

## Proje Hakkında

Klasik kriptografik sistemler matematiksel varsayımlara dayanır. Shor ve Grover
gibi kuantum algoritmalarının gelişmesiyle RSA ve AES gibi standartların
gelecekte kırılabilir hale gelme riski doğmuştur.

BB84 protokolü bu soruna farklı bir cevap verir: güvenliği matematiksel zorluğa
değil, doğa kanunlarına dayandırır. No-cloning teoremi ve Heisenberg belirsizlik
ilkesi sayesinde herhangi bir dinleme girişimi fiziksel olarak iz bırakır ve
tespit edilebilir.

Bu proje, o mekanizmayı gerçek kuantum donanımı gerektirmeden çalıştırılabilir,
görselleştirilebilir bir simülasyona dönüştürür.

---

## Kurulum

```bash
# Depoyu klonla
git clone <repo-adresi>
cd kuantum_kriptografi

# Sanal ortam oluştur ve aktifleştir
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## Kullanım

### Streamlit arayüzü

```bash
streamlit run app/streamlit_app.py
```

Tarayıcıda `http://localhost:8501` adresinden açılır. Sol panelden qubit sayısı,
Eve saldırısı, gürültü türü ve hata düzeltme seçenekleri ayarlanabilir.

### Terminal üzerinden

```python
from src.qs_bb84.simulator import BB84
from src.qs_bb84.utils import sonuc_yazdir

sim = BB84(n_bit=200, eve_var=True, saldiri_turu="intercept_resend")
sonuc_yazdir(sim.calistir())
```

### Deneyleri çalıştırma

```bash
python notebooks/experiments.py
```

Üç deney çalışır, grafikler `sonuclar/` klasörüne kaydedilir.

---

## Modüller

| Dosya | Görev |
|---|---|
| `src/qs_bb84/utils.py` | Rastgele bit/baz üretimi, sifting, QBER hesaplama |
| `src/qs_bb84/simulator.py` | BB84 protokolünün tam akışı |
| `src/qs_bb84/attacks.py` | Intercept-resend ve beam-splitting saldırıları |
| `src/qs_bb84/noise.py` | Depolarizasyon, bit-flip, phase-flip gürültü modelleri |
| `src/qs_bb84/error_correction.py` | Cascade hata düzeltme, privacy amplification |
| `app/streamlit_app.py` | Etkileşimli görsel arayüz |
| `notebooks/experiments.py` | Batch deneyler ve grafik üretimi |

---

## Deney Sonuçları

### Saldırı türlerinin QBER üzerindeki etkisi

| Senaryo | Ölçülen QBER | Tespit |
|---|---|---|
| Saldırı yok | %0.0 | — |
| Intercept-Resend | %26.0 | Tespit edildi |
| Beam-Splitting | ~%0 | Tespit edilemedi |

Intercept-resend saldırısında Eve her qubiti rastgele bir bazda ölçüp yeniden
gönderir. Bazların yarısında yanlış seçim yaptığı için teorik olarak %25
civarında hata bırakır; ölçüm bu değeri doğrular.

Beam-splitting saldırısında Eve qubitleri bozmadan foton çaldığı için QBER'de
iz bırakmaz. Bu, gerçek donanımda decoy-state gibi ek önlemlerin neden gerekli
olduğunu gösterir.

### Cascade hata düzeltme başarısı

| Gürültü | Düzeltme öncesi | Düzeltme sonrası |
|---|---|---|
| %2 | 4 hata | 0 hata |
| %4 | 4 hata | 0 hata |
| %6 | 4 hata | 0 hata |
| %8 | 2 hata | 0 hata |
| %10 | 16 hata | 4 hata |

Cascade %8'e kadar tüm hataları temizler. %10'da kalan hatalar, bir blokta çift
sayıda hata bulunduğunda parite kontrolünün değişmemesinden kaynaklanır —
protokolün bilinen sınırıdır ve tur sayısı artırılarak azaltılabilir.

---

## Teknolojiler

- **Python 3.12**
- **Qiskit** — kuantum devre modelleme
- **Qiskit Aer** — kuantum simülatörü ve gürültü modelleri
- **NumPy** — sayısal işlemler
- **Streamlit** — etkileşimli arayüz
- **Matplotlib** — görselleştirme

---

## Kaynaklar

1. Bennett, C. H., & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing.*
2. Scarani, V. et al. (2009). *The security of practical quantum key distribution.* Reviews of Modern Physics, 81(3).
3. Pirandola, S. et al. (2020). *Advances in quantum cryptography.* Advances in Optics and Photonics, 12(4).
4. Adu-Kyere, A., Nigussie, E., & Isoaho, J. (2022). *Quantum key distribution: Modeling and simulation through BB84 protocol using Python3.* Sensors, 22(16).

---

## Geliştirici

**Kumru ÇELİK** — Fırat Üniversitesi
Danışman: Doç. Dr. Nida KATI