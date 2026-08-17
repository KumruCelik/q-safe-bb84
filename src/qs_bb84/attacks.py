import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()

def intercept_resend(devreler: list) -> list:
    yeni_devreler = []
    for qc in devreler:
        eve_baz = np.random.randint(0, 2)
        olcum = qc.copy()
        if eve_baz == 1:
            olcum.h(0)
        olcum.measure(0, 0)
        sonuc = sim.run(olcum, shots=1).result()
        eve_bit = int(list(sonuc.get_counts().keys())[0])
        yeni_qc = QuantumCircuit(1, 1)
        if eve_bit == 1:
            yeni_qc.x(0)
        if eve_baz == 1:
            yeni_qc.h(0)
        yeni_devreler.append(yeni_qc)
    return yeni_devreler


def beam_splitting(devreler: list, kopyalama_orani: float = 0.5) -> list:
    yeni_devreler = []
    for qc in devreler:
        if np.random.random() < kopyalama_orani:
            eve_baz = np.random.randint(0, 2)
            olcum = qc.copy()
            if eve_baz == 1:
                olcum.h(0)
            olcum.measure(0, 0)
            sim.run(olcum, shots=1).result()
            yeni_devreler.append(qc)
        else:
            yeni_devreler.append(qc)
    return yeni_devreler


def saldiri_raporu(saldiri_turu: str, qber: float) -> dict:
    if saldiri_turu == "intercept_resend":
        beklenen_qber = 0.25
        aciklama = "Eve her qubiti ölçtü ve yeniden gönderdi."
    elif saldiri_turu == "beam_splitting":
        beklenen_qber = 0.05
        aciklama = "Eve fotonların bir kısmını çaldı, iz bırakmaya çalıştı."
    else:
        beklenen_qber = 0.0
        aciklama = "Saldırı yok."
    return {
        "saldiri_turu" : saldiri_turu,
        "olculen_qber" : qber,
        "beklenen_qber": beklenen_qber,
        "aciklama"     : aciklama,
        "tespit_edildi": qber > 0.11
    }