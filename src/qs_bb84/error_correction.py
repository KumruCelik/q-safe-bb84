import numpy as np

def parite_kontrol(blok: np.ndarray) -> int:
    return int(np.sum(blok) % 2)

def ikili_arama(alice: np.ndarray, bob: np.ndarray, sol: int, sag: int):
    if sag - sol == 1:
        return sol if alice[sol] != bob[sol] else None
    orta = (sol + sag) // 2
    if parite_kontrol(alice[sol:orta]) != parite_kontrol(bob[sol:orta]):
        return ikili_arama(alice, bob, sol, orta)
    else:
        return ikili_arama(alice, bob, orta, sag)

def cascade(alice_anahtar: np.ndarray, bob_anahtar: np.ndarray, tur_sayisi: int = 3) -> np.ndarray:
    duzeltilmis = bob_anahtar.copy()
    for tur in range(tur_sayisi):
        blok_boyu = 2 ** (tur + 1)
        for i in range(0, len(duzeltilmis), blok_boyu):
            alice_blok = alice_anahtar[i:i + blok_boyu]
            bob_blok   = duzeltilmis[i:i + blok_boyu]
            if len(alice_blok) < 2:
                continue
            if parite_kontrol(alice_blok) != parite_kontrol(bob_blok):
                hata_idx = ikili_arama(alice_anahtar, duzeltilmis, i, i + len(alice_blok))
                if hata_idx is not None:
                    duzeltilmis[hata_idx] = 1 - duzeltilmis[hata_idx]
    return duzeltilmis

def privacy_amplification(anahtar: np.ndarray, hedef_uzunluk: int = None) -> np.ndarray:
    if hedef_uzunluk is None:
        hedef_uzunluk = len(anahtar) // 2
    if hedef_uzunluk >= len(anahtar):
        return anahtar
    yeni_anahtar = []
    for i in range(hedef_uzunluk):
        bit = int(anahtar[i]) ^ int(anahtar[-(i + 1)])
        yeni_anahtar.append(bit)
    return np.array(yeni_anahtar)

def hata_duzeltme_raporu(alice_oncesi, bob_oncesi, bob_sonrasi) -> dict:
    onceki_hatalar  = int(np.sum(alice_oncesi != bob_oncesi))
    sonraki_hatalar = int(np.sum(alice_oncesi != bob_sonrasi))
    return {
        "onceki_hata_sayisi" : onceki_hatalar,
        "sonraki_hata_sayisi": sonraki_hatalar,
        "duzeltilen"         : onceki_hatalar - sonraki_hatalar,
        "basari"             : sonraki_hatalar == 0
    }