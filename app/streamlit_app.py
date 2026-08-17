import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from src.qs_bb84.simulator import BB84
from src.qs_bb84.error_correction import cascade, privacy_amplification, hata_duzeltme_raporu

st.set_page_config(page_title="Q-SAFE | BB84", page_icon="🔐", layout="wide")

st.title("🔐 Q-SAFE: BB84 Kuantum Anahtar Dağıtımı Simülasyonu")
st.markdown("Kuantum fiziği ilkelerine dayanan BB84 protokolünü adım adım deneyimle.")

with st.sidebar:
    st.header("⚙️ Parametreler")
    n_bit = st.slider("Qubit sayısı", 50, 400, 150, 50)

    st.subheader("👁️ Eve (Dinleyici)")
    eve_var = st.toggle("Eve aktif")
    saldiri_turu = st.selectbox(
        "Saldırı türü",
        ["intercept_resend", "beam_splitting"],
        disabled=not eve_var
    )

    st.subheader("📡 Kanal Gürültüsü")
    gurultu_var = st.toggle("Gürültü aktif")
    gurultu_turu = st.selectbox(
        "Gürültü türü",
        ["depolarizasyon", "bit_flip", "phase_flip"],
        disabled=not gurultu_var
    )
    hata_orani = st.slider("Hata oranı", 0.01, 0.15, 0.03, disabled=not gurultu_var)

    st.subheader("🔧 Son İşlemler")
    hata_duzeltme = st.toggle("Cascade hata düzeltme")
    priv_amp = st.toggle("Privacy amplification")

    calistir = st.button("🚀 Simülasyonu Başlat", use_container_width=True)

if calistir:
    with st.spinner("Simülasyon çalışıyor..."):
        sim = BB84(
            n_bit=n_bit,
            eve_var=eve_var,
            saldiri_turu=saldiri_turu,
            gurultu_var=gurultu_var,
            gurultu_turu=gurultu_turu,
            hata_orani=hata_orani
        )
        r = sim.calistir()

    alice = r["alice_anahtar"]
    bob = r["bob_anahtar"]

    st.subheader("📊 Sonuçlar")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Gönderilen Qubit", r["toplam_bit"])
    k2.metric("Sifting Sonrası", r["anahtar_uzunlugu"])
    k3.metric("QBER", f"%{r['qber']*100:.1f}")
    k4.metric("Durum", "✅ Güvenli" if r["guvenli"] else "🚨 Güvensiz")

    st.divider()

    if hata_duzeltme:
        bob_duz = cascade(alice, bob, tur_sayisi=3)
        rapor = hata_duzeltme_raporu(alice, bob, bob_duz)
        st.subheader("🔧 Hata Düzeltme (Cascade)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Önceki Hata", rapor["onceki_hata_sayisi"])
        c2.metric("Sonraki Hata", rapor["sonraki_hata_sayisi"])
        c3.metric("Tam Eşleşme", "EVET" if rapor["basari"] else "HAYIR")
        bob = bob_duz

    if priv_amp:
        bob = privacy_amplification(bob)
        alice = alice[:len(bob)]
        st.subheader("🔒 Privacy Amplification")
        st.info(f"Anahtar {r['anahtar_uzunlugu']} bitten {len(bob)} bite düşürüldü.")

    st.divider()
    st.subheader("📈 Görselleştirme")
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("**Alice ve Bob Anahtarı (ilk 40 bit)**")
        n_goster = min(40, len(alice), len(bob))
        fig, ax = plt.subplots(figsize=(8, 2.5))
        x = np.arange(n_goster)
        ax.bar(x - 0.2, alice[:n_goster], 0.4, label="Alice", color="#4C9BE8")
        ax.bar(x + 0.2, bob[:n_goster], 0.4, label="Bob", color="#E8854C")
        ax.set_yticks([0, 1])
        ax.set_xlabel("Bit indeksi")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close()

    with g2:
        st.markdown("**QBER ve Güvenlik Eşiği**")
        fig2, ax2 = plt.subplots(figsize=(8, 2.5))
        ax2.bar(["Mevcut QBER"], [r["qber"]],
                color="#F44336" if not r["guvenli"] else "#4CAF50", width=0.4)
        ax2.axhline(y=0.11, color="red", linestyle="--", label="Güvenlik eşiği %11")
        ax2.set_ylabel("QBER")
        ax2.set_ylim(0, max(0.35, r["qber"] * 1.2))
        ax2.legend(fontsize=8)
        ax2.grid(axis="y", alpha=0.3)
        st.pyplot(fig2)
        plt.close()

    if eve_var:
        st.divider()
        st.subheader("⚠️ Saldırı Raporu")
        rs = r["saldiri_raporu"]
        st.error(f"**{rs['aciklama']}**")
        col1, col2 = st.columns(2)
        col1.metric("Ölçülen QBER", f"%{rs['olculen_qber']*100:.1f}")
        col2.metric("Tespit Edildi", "EVET 🚨" if rs["tespit_edildi"] else "HAYIR")

    st.divider()
    st.subheader("🔑 Nihai Anahtar")
    st.code("".join(map(str, bob[:64])) + ("..." if len(bob) > 64 else ""))

else:
    st.info("👈 Sol panelden parametreleri ayarla ve **Simülasyonu Başlat** butonuna tıkla.")