import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.qs_bb84.error_correction import (
    parite_kontrol, cascade, privacy_amplification, hata_duzeltme_raporu
)
from src.qs_bb84.utils import sifting, qber_hesapla
from src.qs_bb84.simulator import BB84


# ── parite_kontrol testleri ────────────────────────────
def test_parite_cift_sayida_bir():
    """İki tane 1 varsa parite çift (0) olmalı."""
    assert parite_kontrol(np.array([1, 1, 0, 0])) == 0

def test_parite_tek_sayida_bir():
    """Üç tane 1 varsa parite tek (1) olmalı."""
    assert parite_kontrol(np.array([1, 1, 1, 0])) == 1

def test_parite_bos_dizi():
    """Hiç 1 yoksa parite 0 olmalı."""
    assert parite_kontrol(np.array([0, 0, 0, 0])) == 0


# ── cascade testleri ────────────────────────────────────
def test_cascade_hatasiz_anahtari_bozmaz():
    """Zaten aynı olan anahtarlar değişmemeli."""
    alice = np.array([1, 0, 1, 1, 0, 0, 1, 0])
    bob   = alice.copy()
    sonuc = cascade(alice, bob)
    assert np.array_equal(sonuc, alice)

def test_cascade_tek_hatayi_duzeltir():
    """Tek bir hatalı bit düzeltilmeli."""
    alice = np.array([1, 0, 1, 1, 0, 0, 1, 0])
    bob   = alice.copy()
    bob[3] = 1 - bob[3]          # 3. biti boz
    sonuc = cascade(alice, bob, tur_sayisi=4)
    assert np.array_equal(sonuc, alice)

def test_cascade_uzunlugu_korur():
    """Düzeltme sonrası anahtar uzunluğu değişmemeli."""
    alice = np.random.randint(0, 2, 32)
    bob   = alice.copy()
    bob[5] = 1 - bob[5]
    sonuc = cascade(alice, bob)
    assert len(sonuc) == len(alice)


# ── privacy_amplification testleri ─────────────────────
def test_privacy_anahtari_kisaltir():
    """Anahtar varsayılan olarak yarıya inmeli."""
    anahtar = np.random.randint(0, 2, 40)
    sonuc = privacy_amplification(anahtar)
    assert len(sonuc) == 20

def test_privacy_hedef_uzunluk():
    """Belirtilen hedef uzunluğa inmeli."""
    anahtar = np.random.randint(0, 2, 40)
    sonuc = privacy_amplification(anahtar, hedef_uzunluk=10)
    assert len(sonuc) == 10

def test_privacy_sadece_bit_uretir():
    """Çıktı sadece 0 ve 1 içermeli."""
    anahtar = np.random.randint(0, 2, 40)
    sonuc = privacy_amplification(anahtar)
    assert set(np.unique(sonuc)).issubset({0, 1})


# ── hata_duzeltme_raporu testleri ──────────────────────
def test_rapor_hata_sayar():
    """Rapor hata sayısını doğru saymalı."""
    alice   = np.array([1, 0, 1, 0])
    bob     = np.array([1, 1, 1, 1])   # 2 hata var
    sonrasi = alice.copy()             # tamamen düzeltilmiş
    r = hata_duzeltme_raporu(alice, bob, sonrasi)
    assert r["onceki_hata_sayisi"] == 2
    assert r["sonraki_hata_sayisi"] == 0
    assert r["duzeltilen"] == 2
    assert r["basari"] is True


# ── qber testleri ───────────────────────────────────────
def test_qber_hatasiz_sifir():
    """Aynı anahtarlarda QBER 0 olmalı."""
    a = np.array([1, 0, 1, 1])
    assert qber_hesapla(a, a.copy()) == 0.0

def test_qber_tamamen_farkli_bir():
    """Tamamen ters anahtarlarda QBER 1 olmalı."""
    a = np.array([1, 0, 1, 0])
    b = np.array([0, 1, 0, 1])
    assert qber_hesapla(a, b) == 1.0

def test_qber_yarim():
    """Yarısı hatalıysa QBER 0.5 olmalı."""
    a = np.array([1, 0, 1, 0])
    b = np.array([1, 0, 0, 1])
    assert qber_hesapla(a, b) == 0.5


# ── sifting testleri ────────────────────────────────────
def test_sifting_ayni_bazlari_tutar():
    """Sadece bazların eşleştiği bitler kalmalı."""
    a_baz = np.array([0, 1, 0, 1])
    b_baz = np.array([0, 0, 0, 1])     # 0. ve 2. ve 3. eşleşiyor
    a_bit = np.array([1, 1, 0, 1])
    b_bit = np.array([1, 0, 0, 1])
    a_key, b_key = sifting(a_baz, b_baz, a_bit, b_bit)
    assert len(a_key) == 3
    assert np.array_equal(a_key, np.array([1, 0, 1]))


# ── entegrasyon testleri ───────────────────────────────
def test_eve_yoksa_qber_dusuk():
    """Eve ve gürültü yoksa QBER sıfıra yakın olmalı."""
    r = BB84(n_bit=100).calistir()
    assert r["qber"] < 0.02
    assert r["guvenli"] is True

def test_eve_varsa_qber_yuksek():
    """Intercept-resend saldırısı QBER'i %11 üstüne çıkarmalı."""
    r = BB84(n_bit=150, eve_var=True, saldiri_turu="intercept_resend").calistir()
    assert r["qber"] > 0.11
    assert r["guvenli"] is False

def test_sifting_yaklasik_yari():
    """Sifting sonrası anahtar kabaca gönderilenin yarısı olmalı."""
    n = 200
    r = BB84(n_bit=n).calistir()
    assert 0.3 * n < r["anahtar_uzunlugu"] < 0.7 * n