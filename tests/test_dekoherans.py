import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from src.qs_bb84.ibm_backend import gercek_donanimda_calistir
from src.qs_bb84.utils import rastgele_bitler, rastgele_bazlar, sifting, qber_hesapla

N = 40                          # her gecikme seviyesi icin qubit sayisi
gecikmeler = [0, 20, 50, 100]   # eklenecek identity kapisi sayisi

print("DEKOHERANS DENEYI")
print("Qubitler olculmeden once bekletilerek gurultu olculuyor.\n")
print(f"Her seviye {N} qubit, toplam {N*len(gecikmeler)} devre.")
print("Bu islem uzun surebilir.\n")

qber_sonuclari = []

for gecikme in gecikmeler:
    print(f"[{gecikmeler.index(gecikme)+1}/{len(gecikmeler)}] Gecikme seviyesi: {gecikme} kapi")

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

        # Kuantum kanalinda gecen sureyi taklit et
        for _ in range(gecikme):
            qc.id(0)

        qc.barrier()
        if b_baz == 1:
            qc.h(0)
        qc.measure(0, 0)
        devreler.append(qc)

    bob_bitler = np.array(gercek_donanimda_calistir(devreler, shots=1))
    a_key, b_key = sifting(alice_bazlar, bob_bazlar, alice_bitler, bob_bitler)
    qber = qber_hesapla(a_key, b_key)
    qber_sonuclari.append(qber)

    print(f"    Sifted key: {len(a_key)} bit | Hata: {int(np.sum(a_key != b_key))} | QBER: %{qber*100:.2f}\n")

# ── Sonuclar ───────────────────────────────────────────
print("="*55)
print("   DEKOHERANS SONUCLARI")
print("="*55)
for g, q in zip(gecikmeler, qber_sonuclari):
    durum = "GUVENLI" if q < 0.11 else "ESIK USTU"
    print(f"  {g:4d} kapi gecikme -> QBER %{q*100:5.2f}  [{durum}]")
print("="*55)

os.makedirs("sonuclar", exist_ok=True)

plt.figure(figsize=(9, 5))
plt.plot(gecikmeler, np.array(qber_sonuclari)*100,
         "o-", color="#FF9800", linewidth=2.5, markersize=9, label="Olculen QBER")
plt.axhline(y=11, color="red", linestyle="--", linewidth=2, label="Guvenlik esigi (%11)")
plt.xlabel("Kanal Gecikmesi (identity kapisi sayisi)")
plt.ylabel("QBER (%)")
plt.title("Gercek Donanimda Dekoheransin QBER Uzerindeki Etkisi (ibm_marrakesh)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("sonuclar/deney6_dekoherans.png", dpi=150)
plt.close()

print("\n  Grafik kaydedildi: sonuclar/deney6_dekoherans.png")