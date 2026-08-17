import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from src.qs_bb84.simulator import BB84
from src.qs_bb84.error_correction import cascade, privacy_amplification, hata_duzeltme_raporu
from src.qs_bb84.utils import rastgele_bitler, rastgele_bazlar, sifting, qber_hesapla

st.set_page_config(page_title="Q-SAFE | BB84", page_icon="🔐", layout="wide")

st.title("🔐 Q-SAFE: BB84 Kuantum Anahtar Dağıtımı Simülasyonu")
st.markdown("Kuantum fiziği ilkelerine dayanan BB84 protokolünü simülasyonda ve gerçek kuantum donanımında deneyimle.")

sekme1, sekme2 = st.tabs(["🖥️ Simülasyon", "⚛️ Gerçek IBM Donanımı"])

# ═══════════════════════════════════════════════════════
# SEKME 1: SİMÜLASYON
# ═══════════════════════════════════════════════════════
with sekme1:
    with st.sidebar:
        st.header("⚙️ Simülasyon Parametreleri")
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
            r = BB84(
                n_bit=n_bit,
                eve_var=eve_var,
                saldiri_turu=saldiri_turu,
                gurultu_var=gurultu_var,
                gurultu_turu=gurultu_turu,
                hata_orani=hata_orani
            ).calistir()

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
            bob_duz = cascade(alice, bob, tur_sayisi=4)
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

# ═══════════════════════════════════════════════════════
# SEKME 2: GERÇEK IBM DONANIMI
# ═══════════════════════════════════════════════════════
with sekme2:
    st.markdown("""
    Bu bölüm protokolü **gerçek bir kuantum bilgisayarda** çalıştırır.
    Devreler IBM Quantum kuyruğuna gönderilir ve sonuç birkaç dakika sürebilir.
    """)

    st.warning("⚠️ Gerçek donanım kullanımı ücretsiz plan kotandan düşer. Bilinçli çalıştır.")

    d1, d2 = st.columns(2)
    with d1:
        ibm_n_bit = st.slider("Qubit sayısı (donanım)", 10, 100, 20, 10)
    with d2:
        gecikme = st.slider("Kanal gecikmesi (identity kapısı)", 0, 200, 0, 25,
                            help="Qubiti ölçmeden önce bekletir. Dekoherans etkisini gösterir.")

    b1, b2 = st.columns(2)
    cihaz_listele = b1.button("📋 Cihazları Listele", use_container_width=True)
    donanim_calistir = b2.button("⚛️ Gerçek Donanımda Çalıştır", use_container_width=True)

    if cihaz_listele:
        try:
            from src.qs_bb84.ibm_backend import ibm_servisi_baglan
            with st.spinner("IBM Quantum'a bağlanılıyor..."):
                service = ibm_servisi_baglan()
                cihazlar = []
                for b in service.backends():
                    durum = b.status()
                    cihazlar.append({
                        "Cihaz": b.name,
                        "Qubit": b.num_qubits,
                        "Kuyruk": durum.pending_jobs,
                        "Durum": "Aktif" if durum.operational else "Kapalı"
                    })
            st.success("Bağlantı başarılı")
            st.dataframe(cihazlar, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")

    if donanim_calistir:
        try:
            from src.qs_bb84.ibm_backend import gercek_donanimda_calistir

            with st.spinner("Devreler hazırlanıyor..."):
                alice_bitler = rastgele_bitler(ibm_n_bit)
                alice_bazlar = rastgele_bazlar(ibm_n_bit)
                bob_bazlar = rastgele_bazlar(ibm_n_bit)

                devreler = []
                for bit, a_baz, b_baz in zip(alice_bitler, alice_bazlar, bob_bazlar):
                    qc = QuantumCircuit(1, 1)
                    if bit == 1:
                        qc.x(0)
                    if a_baz == 1:
                        qc.h(0)
                    qc.barrier()
                    for _ in range(gecikme):
                        qc.id(0)
                    qc.barrier()
                    if b_baz == 1:
                        qc.h(0)
                    qc.measure(0, 0)
                    devreler.append(qc)

            with st.spinner("IBM kuyruğunda bekleniyor... Bu birkaç dakika sürebilir."):
                bob_bitler = np.array(gercek_donanimda_calistir(devreler, shots=1))

            a_key, b_key = sifting(alice_bazlar, bob_bazlar, alice_bitler, bob_bitler)
            qber_d = qber_hesapla(a_key, b_key)
            hata = int(np.sum(a_key != b_key))

            st.success("Gerçek donanımda çalıştırma tamamlandı")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Gönderilen Qubit", ibm_n_bit)
            m2.metric("Sifting Sonrası", len(a_key))
            m3.metric("Hatalı Bit", hata)
            m4.metric("QBER", f"%{qber_d*100:.2f}")

            # Simulasyonla karsilastir
            r_sim = BB84(n_bit=ibm_n_bit).calistir()

            st.subheader("📊 Gerçek Donanım vs İdeal Simülasyon")
            fig3, ax3 = plt.subplots(figsize=(9, 4))
            etiket = ["İdeal Simülasyon", f"Gerçek Donanım\n(gecikme: {gecikme})"]
            deger = [r_sim["qber"]*100, qber_d*100]
            bars3 = ax3.bar(etiket, deger, color=["#4C9BE8", "#FF9800"], alpha=0.85, width=0.45)
            ax3.axhline(y=11, color="red", linestyle="--", linewidth=2, label="Güvenlik eşiği %11")
            for bar, d in zip(bars3, deger):
                ax3.text(bar.get_x() + bar.get_width()/2, d + 0.3,
                         f"%{d:.2f}", ha="center", fontweight="bold")
            ax3.set_ylabel("QBER (%)")
            ax3.set_ylim(0, max(13, max(deger)*1.3))
            ax3.legend()
            ax3.grid(axis="y", alpha=0.3)
            st.pyplot(fig3)
            plt.close()

            st.subheader("🔑 Donanımdan Üretilen Anahtar")
            st.code("".join(map(str, b_key)))

            if gecikme > 0 and qber_d > 0:
                st.info(f"Gecikme {gecikme} kapı iken QBER %{qber_d*100:.2f} ölçüldü. "
                        "Bu, dekoherans nedeniyle qubitlerin zamanla bozulduğunu gösterir.")

        except Exception as e:
            st.error(f"Hata: {e}")
            st.caption("`.env` dosyasında IBM_QUANTUM_TOKEN ve IBM_QUANTUM_CRN tanımlı mı kontrol et.")