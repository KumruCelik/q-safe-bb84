import numpy as np

def rastgele_bitler(n: int) -> np.ndarray:
    return np.random.randint(0, 2, n)

def rastgele_bazlar(n: int) -> np.ndarray:
    return np.random.randint(0, 2, n)

def baz_sembol(b: int) -> str:
    return "+" if b == 0 else "×"

def sifting(alice_bazlar, bob_bazlar, alice_bitler, bob_bitler):
    eslesme = alice_bazlar == bob_bazlar
    return alice_bitler[eslesme], bob_bitler[eslesme]

def qber_hesapla(alice_anahtar, bob_anahtar) -> float:
    if len(alice_anahtar) == 0:
        return 0.0
    hatalar = np.sum(alice_anahtar != bob_anahtar)
    return float(hatalar / len(alice_anahtar))

def sonuc_yazdir(sonuc: dict):
    print("\n" + "="*45)
    print("       BB84 SİMÜLASYON SONUÇLARI")
    print("="*45)
    print(f"  Gönderilen qubit sayısı : {sonuc['toplam_bit']}")
    print(f"  Sifting sonrası anahtar : {sonuc['anahtar_uzunlugu']} bit")
    print(f"  QBER                    : %{sonuc['qber']*100:.1f}")
    print(f"  Eve müdahalesi          : {'VAR' if sonuc['eve_var'] else 'YOK'}")
    print(f"  Güvenli mi?             : {'EVET' if sonuc['guvenli'] else 'HAYIR'}")
    print("="*45 + "\n")