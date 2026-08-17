import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from qiskit import QuantumCircuit
from src.qs_bb84.ibm_backend import gercek_donanimda_calistir
from src.qs_bb84.utils import rastgele_bitler, rastgele_bazlar, sifting, qber_hesapla

# Gercek donanim yavas ve kuyruklu, az qubit ile test et
N = 20

print(f"Gercek IBM donaniminda BB84 testi ({N} qubit)\n")

# 1. Alice bit ve baz uretir
alice_bitler = rastgele_bitler(N)
alice_bazlar = rastgele_bazlar(N)

# 2. Bob bazlarini onceden secer
bob_bazlar = rastgele_bazlar(N)

# 3. Alice kodlar + Bob'un olcum bazi ayni devreye eklenir
devreler = []
for bit, a_baz, b_baz in zip(alice_bitler, alice_bazlar, bob_bazlar):
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if a_baz == 1:
        qc.h(0)      # Alice X bazinda hazirliyor
    qc.barrier()
    if b_baz == 1:
        qc.h(0)      # Bob X bazinda olcuyor
    qc.measure(0, 0)
    devreler.append(qc)

print("Devreler hazirlandi, IBM'e gonderiliyor...")
print("Bu islem birkac dakika surebilir, bekle.\n")

# 4. Gercek donanimda calistir
bob_bitler = np.array(gercek_donanimda_calistir(devreler, shots=1))

# 5. Sifting
alice_anahtar, bob_anahtar = sifting(alice_bazlar, bob_bazlar, alice_bitler, bob_bitler)

# 6. QBER
qber = qber_hesapla(alice_anahtar, bob_anahtar)

print("\n" + "="*50)
print("   GERCEK DONANIM SONUCLARI")
print("="*50)
print(f"  Gonderilen qubit    : {N}")
print(f"  Sifting sonrasi     : {len(alice_anahtar)} bit")
print(f"  QBER                : %{qber*100:.1f}")
print(f"  Alice anahtari      : {''.join(map(str, alice_anahtar))}")
print(f"  Bob anahtari        : {''.join(map(str, bob_anahtar))}")
print("="*50)
print("\nNot: Gercek donanimda QBER simulasyondan yuksek cikar.")
print("Bunun sebebi donanim gurultusu, dekoherans ve olcum hatalaridir.")