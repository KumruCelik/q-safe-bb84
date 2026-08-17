import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from src.qs_bb84.ibm_backend import gercek_donanimda_calistir
from src.qs_bb84.simulator import BB84
from src.qs_bb84.utils import rastgele_bitler, rastgele_bazlar, sifting, qber_hesapla

N = 100

print(f"Gercek IBM donaniminda BB84 testi ({N} qubit)")
print("Bu islem 10-20 dakika surebilir.\n")

# ── 1. Gercek donanim ──────────────────────────────────
alice_bitler = rastgele_bitler(N)
alice_bazlar = rastgele_bazlar(N)
bob_bazlar   = rastgele_bazlar(N)

devreler = []
for bit, a_baz, b_baz in zip(alice_bitler, alice_bazlar, bob_bazlar):
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if a_baz == 1:
        qc.h(0)
    qc.barrier()
    if b_baz == 1:
        qc.h(0)
    qc.measure(0, 0)
    devreler.append(qc)

print("Devreler hazirlandi, IBM'e gonderiliyor...\n")
bob_bitler = np.array(gercek_donanimda_calistir(devreler, shots=1))

a_key, b_key = sifting(alice_bazlar, bob_bazlar, alice_bitler, bob_bitler)
qber_donanim = qber_hesapla(a_key, b_key)
hata_sayisi  = int(np.sum(a_key != b_key))

# ── 2. Ayni kosullarda simulasyon ──────────────────────
print("\nAyni kosullarda ideal simulasyon calistiriliyor...")
r_sim = BB84(n_bit=N).calistir()
qber_sim = r_sim["qber"]

# ── 3. Karsilastirma ───────────────────────────────────
print("\n" + "="*55)
print("   GERCEK DONANIM vs IDEAL SIMULASYON")
print("="*55)
print(f"  Gonderilen qubit           : {N}")
print(f"  Sifting sonrasi (donanim)  : {len(a_key)} bit")
print(f"  Sifting sonrasi (simulasyon): {r_sim['anahtar_uzunlugu']} bit")
print(f"  Hatali bit (donanim)       : {hata_sayisi}")
print("-"*55)
print(f"  QBER - Gercek donanim      : %{qber_donanim*100:.2f}")
print(f"  QBER - Ideal simulasyon    : %{qber_sim*100:.2f}")
print(f"  Fark (donanim gurultusu)   : %{(qber_donanim - qber_sim)*100:.2f}")
print("="*55)

if qber_donanim < 0.11:
    print("\n  Sonuc: Anahtar GUVENLI (QBER < %11)")
else:
    print("\n  Sonuc: QBER esigin uzerinde")

# ── 4. Grafik ──────────────────────────────────────────
os.makedirs("sonuclar", exist_ok=True)

plt.figure(figsize=(8, 5))
etiketler = ["Ideal\nSimulasyon", "Gercek\nDonanim\n(ibm_marrakesh)"]
degerler  = [qber_sim*100, qber_donanim*100]
renkler   = ["#4C9BE8", "#FF9800"]

bars = plt.bar(etiketler, degerler, color=renkler, alpha=0.85, width=0.5)
plt.axhline(y=11, color="red", linestyle="--", linewidth=2, label="Guvenlik esigi (%11)")

for bar, d in zip(bars, degerler):
    plt.text(bar.get_x() + bar.get_width()/2, d + 0.3,
             f"%{d:.2f}", ha="center", fontweight="bold")

plt.ylabel("QBER (%)")
plt.title(f"Ideal Simulasyon ve Gercek Kuantum Donanimi Karsilastirmasi ({N} qubit)")
plt.ylim(0, max(12, max(degerler)*1.4))
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("sonuclar/deney4_donanim_karsilastirma.png", dpi=150)
plt.close()

print("\n  Grafik kaydedildi: sonuclar/deney4_donanim_karsilastirma.png")

# ── 5. Uclu karsilastirma ──────────────────────────────
print("\nEve saldirisi altinda simulasyon calistiriliyor...")
r_eve = BB84(n_bit=N, eve_var=True, saldiri_turu="intercept_resend").calistir()
qber_eve = r_eve["qber"]
print(f"  QBER - Eve saldirisi : %{qber_eve*100:.2f}")

plt.figure(figsize=(9, 5))
etiketler3 = ["Ideal\nSimulasyon", "Gercek Donanim\n(ibm_marrakesh)", "Eve Saldirisi\n(simulasyon)"]
degerler3  = [qber_sim*100, qber_donanim*100, qber_eve*100]
renkler3   = ["#4C9BE8", "#4CAF50", "#F44336"]

bars3 = plt.bar(etiketler3, degerler3, color=renkler3, alpha=0.85, width=0.5)
plt.axhline(y=11, color="red", linestyle="--", linewidth=2, label="Guvenlik esigi (%11)")

for bar, d in zip(bars3, degerler3):
    plt.text(bar.get_x() + bar.get_width()/2, d + 0.6,
             f"%{d:.2f}", ha="center", fontweight="bold")

plt.ylabel("QBER (%)")
plt.title(f"BB84 Protokolu: Simulasyon, Gercek Donanim ve Saldiri Senaryosu ({N} qubit)")
plt.ylim(0, max(35, max(degerler3)*1.3))
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("sonuclar/deney5_uclu_karsilastirma.png", dpi=150)
plt.close()

print("  Grafik kaydedildi: sonuclar/deney5_uclu_karsilastirma.png")