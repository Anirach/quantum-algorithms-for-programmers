"""Part 2: one marked state among 16. The oracle is a teaching fixture."""
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from common import sample


def phase_oracle(n, marked):
    if n < 2 or len(marked) != n or set(marked) - {"0", "1"}:
        raise ValueError("Use n >= 2 and an n-bit marked string")
    qc = QuantumCircuit(n, name="Oracle")
    zeros = [q for q, bit in enumerate(reversed(marked)) if bit == "0"]
    for q in zeros:
        qc.x(q)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for q in zeros:
        qc.x(q)
    return qc


def diffuser(n):
    qc = QuantumCircuit(n, name="Diffuser")
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def grover_circuit(n=4, marked="1011", iterations=3, measure=True):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iterations):
        qc.compose(phase_oracle(n, marked), inplace=True)
        qc.compose(diffuser(n), inplace=True)
    if measure:
        qc.measure_all()
    return qc


def theoretical_probability(n, k):
    theta = math.asin(1 / math.sqrt(2 ** n))
    return math.sin((2 * k + 1) * theta) ** 2


def main():
    counts = sample(grover_circuit(), 4096, 7)
    exact = Statevector(grover_circuit(measure=False)).probabilities()[11]
    print("N=16; marked=1011; iterations=3")
    print(f"Theory={theoretical_probability(4, 3):.6f}; statevector={exact:.6f}")
    print(f"Sampled hits={counts.get('1011', 0)}/4096")
    print("Success by iterations 0..5:", [round(theoretical_probability(4, k), 4) for k in range(6)])
    return {"counts": counts, "shots": 4096, "exact": float(exact)}


if __name__ == "__main__":
    main()
