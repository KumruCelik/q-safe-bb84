from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error
from qiskit_aer import AerSimulator

def gurultu_modeli_olustur(gurultu_turu: str, hata_orani: float = 0.01):
    """
    Gerçek kuantum donanımında oluşan gürültüyü simüle eder.

    gurultu_turu seçenekleri:
      'depolarizasyon' — en yaygın, qubit rastgele bozulur
      'bit_flip'       — 0→1 veya 1→0 hatası
      'phase_flip'     — fazı bozar, X bazında hata yapar
    """
    gurultu = NoiseModel()

    if gurultu_turu == "depolarizasyon":
        hata = depolarizing_error(hata_orani, 1)
        gurultu.add_all_qubit_quantum_error(hata, ["h", "x", "measure"])

    elif gurultu_turu == "bit_flip":
        hata = pauli_error([("X", hata_orani), ("I", 1 - hata_orani)])
        gurultu.add_all_qubit_quantum_error(hata, ["h", "x", "measure"])

    elif gurultu_turu == "phase_flip":
        hata = pauli_error([("Z", hata_orani), ("I", 1 - hata_orani)])
        gurultu.add_all_qubit_quantum_error(hata, ["h", "x", "measure"])

    return gurultu


def gurultulu_simulator(gurultu_turu: str, hata_orani: float = 0.01) -> AerSimulator:
    """Gürültü modeli eklenmiş bir AerSimulator döndürür."""
    model = gurultu_modeli_olustur(gurultu_turu, hata_orani)
    return AerSimulator(noise_model=model)