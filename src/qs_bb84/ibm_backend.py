import os
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

load_dotenv()


def ibm_servisi_baglan():
    """
    IBM Quantum servisine baglanir.
    Token ve CRN .env dosyasindan okunur.
    """
    token = os.getenv("IBM_QUANTUM_TOKEN")
    crn   = os.getenv("IBM_QUANTUM_CRN")

    if not token:
        raise ValueError(".env dosyasinda IBM_QUANTUM_TOKEN bulunamadi.")
    if not crn:
        raise ValueError(
            ".env dosyasinda IBM_QUANTUM_CRN bulunamadi. "
            "IBM Cloud'da Quantum Compute servisi olusturup CRN'i eklemelisin."
        )

    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance=crn
    )
    return service


def uygun_backend_sec(service, min_qubit=1):
    """Kuyrugu en kisa olan, calisir durumdaki gercek cihazi secer."""
    backend = service.least_busy(
        operational=True,
        simulator=False,
        min_num_qubits=min_qubit
    )
    return backend


def backend_listele():
    """Hesabina tanimli tum cihazlari listeler."""
    service = ibm_servisi_baglan()
    print("Kullanilabilir cihazlar:\n")
    for b in service.backends():
        durum = b.status()
        print(f"  {b.name:25s} | {b.num_qubits:3d} qubit | "
              f"kuyruk: {durum.pending_jobs:3d} | "
              f"{'aktif' if durum.operational else 'kapali'}")


def gercek_donanimda_calistir(devreler: list, shots: int = 1):
    """
    Verilen kuantum devrelerini gercek IBM donaniminda calistirir.

    DIKKAT: Gercek donanim kuyruklu calisir, sonuc dakikalar surebilir.
    Az sayida devre ile test et (orn. 10-20 qubit).
    """
    service = ibm_servisi_baglan()
    backend = uygun_backend_sec(service)
    print(f"Secilen cihaz: {backend.name} ({backend.num_qubits} qubit)")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpile_edilmis = [pm.run(qc) for qc in devreler]

    sampler = SamplerV2(mode=backend)
    job = sampler.run(transpile_edilmis, shots=shots)
    print(f"Is gonderildi. Job ID: {job.job_id()}")
    print("Kuyrukta bekleniyor...")

    result = job.result()

    bitler = []
    for pub_result in result:
        counts = pub_result.data.c.get_counts()
        bit = int(max(counts, key=counts.get))
        bitler.append(bit)

    return bitler