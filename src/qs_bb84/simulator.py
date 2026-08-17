import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from .utils import rastgele_bitler, rastgele_bazlar, sifting, qber_hesapla
from .attacks import intercept_resend, beam_splitting, saldiri_raporu
from .noise import gurultulu_simulator

class BB84:
    def __init__(
        self,
        n_bit=100,
        eve_var=False,
        saldiri_turu="intercept_resend",
        gurultu_var=False,
        gurultu_turu="depolarizasyon",
        hata_orani=0.01
    ):
        self.n_bit        = n_bit
        self.eve_var      = eve_var
        self.saldiri_turu = saldiri_turu
        self.gurultu_var  = gurultu_var
        self.gurultu_turu = gurultu_turu
        self.hata_orani   = hata_orani

        if gurultu_var:
            self.sim = gurultulu_simulator(gurultu_turu, hata_orani)
        else:
            self.sim = AerSimulator()

    def _qubit_olustur(self, bit, baz) -> QuantumCircuit:
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if baz == 1:
            qc.h(0)
        return qc

    def _bob_olcum(self, devreler, bob_bazlar) -> list:
        sonuclar = []
        for qc, baz in zip(devreler, bob_bazlar):
            olcum = qc.copy()
            if baz == 1:
                olcum.h(0)
            olcum.measure(0, 0)
            r = self.sim.run(olcum, shots=1).result()
            bit = int(list(r.get_counts().keys())[0])
            sonuclar.append(bit)
        return sonuclar

    def calistir(self) -> dict:
        alice_bitler = rastgele_bitler(self.n_bit)
        alice_bazlar = rastgele_bazlar(self.n_bit)

        devreler = [
            self._qubit_olustur(b, bz)
            for b, bz in zip(alice_bitler, alice_bazlar)
        ]

        if self.eve_var:
            if self.saldiri_turu == "intercept_resend":
                devreler = intercept_resend(devreler)
            elif self.saldiri_turu == "beam_splitting":
                devreler = beam_splitting(devreler)

        bob_bazlar = rastgele_bazlar(self.n_bit)
        bob_bitler = np.array(self._bob_olcum(devreler, bob_bazlar))

        alice_anahtar, bob_anahtar = sifting(
            alice_bazlar, bob_bazlar,
            alice_bitler, bob_bitler
        )

        qber = qber_hesapla(alice_anahtar, bob_anahtar)

        rapor = saldiri_raporu(
            self.saldiri_turu if self.eve_var else "yok",
            qber
        )

        return {
            "toplam_bit"      : self.n_bit,
            "anahtar_uzunlugu": len(alice_anahtar),
            "alice_anahtar"   : alice_anahtar,
            "bob_anahtar"     : bob_anahtar,
            "qber"            : qber,
            "eve_var"         : self.eve_var,
            "guvenli"         : qber < 0.11,
            "gurultu_var"     : self.gurultu_var,
            "gurultu_turu"    : self.gurultu_turu if self.gurultu_var else "yok",
            "saldiri_raporu"  : rapor
        }