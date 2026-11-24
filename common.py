"""Shared QFT and reproducible ideal simulator; never connects to a QPU."""
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def inverse_qft(n):
    qc = QuantumCircuit(n, name="QFT†")
    for q in range(n // 2):
        qc.swap(q, n - 1 - q)
    for j in range(n):
        for k in range(j):
            qc.cp(-math.pi / 2 ** (j - k), k, j)
        qc.h(j)
    return qc


def sample(qc, shots, seed):
    sim = AerSimulator(seed_simulator=seed)
    compiled = transpile(qc, sim, seed_transpiler=seed)
    return sim.run(compiled, shots=shots).result().get_counts()
