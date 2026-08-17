import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.qs_bb84.simulator import BB84
from src.qs_bb84.utils import sonuc_yazdir
from src.qs_bb84.error_correction import cascade, privacy_amplification, hata_duzeltme_raporu

print("=" * 45)
print("  SENARYO: Gürültülü kanal, hata düzeltme")
print("=" * 45)

sim = BB84(n_bit=300, gurultu_var=True, gurultu_turu="depolarizasyon", hata_orani=0.05)
r = sim.calistir()
sonuc_yazdir(r)

alice = r["alice_anahtar"]
bob   = r["bob_anahtar"]

print(f"Hata düzeltme ÖNCESİ hata sayısı : {np.sum(alice != bob)}")

# Cascade ile düzelt
bob_duzeltilmis = cascade(alice, bob, tur_sayisi=3)
rapor = hata_duzeltme_raporu(alice, bob, bob_duzeltilmis)

print(f"Hata düzeltme SONRASI hata sayısı : {rapor['sonraki_hata_sayisi']}")
print(f"Düzeltilen bit sayısı              : {rapor['duzeltilen']}")
print(f"Tam eşleşme sağlandı mı?           : {'EVET ✓' if rapor['basari'] else 'HAYIR ✗'}")

# Privacy amplification
nihai_anahtar = privacy_amplification(bob_duzeltilmis)
print(f"\nPrivacy amplification sonrası anahtar uzunluğu: {len(nihai_anahtar)} bit")
print(f"Nihai anahtar (ilk 20 bit): {''.join(map(str, nihai_anahtar[:20]))}")