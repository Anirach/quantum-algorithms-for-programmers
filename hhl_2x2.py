"""Part 4: exact, positive-spectrum 2x2 HHL. Not a general linear solver."""
import math
import numpy as np
from scipy.linalg import expm
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Statevector
from common import inverse_qft, sample

A = np.array([[1.5, 0.5], [0.5, 1.5]])
B = np.array([1., 0.])


def qpe(clock, target):
    qc = QuantumCircuit(clock, target, name="QPE")
    qc.h(clock)
    for j in range(len(clock)):
        gate = UnitaryGate(expm(1j * A * math.pi / 2 * 2 ** j))
        qc.append(gate.control(1), [clock[j], target[0]])
    qc.append(inverse_qft(len(clock)), clock)
    return qc


def hhl_circuit(measure=True):
    anc = QuantumRegister(1, "anc")
    clock = QuantumRegister(2, "clock")
    x = QuantumRegister(1, "x")
    qc = QuantumCircuit(anc, clock, x)
    est = qpe(clock, x)
    qc.append(est, clock[:] + x[:])
    # Only 01 and 10 occur: these two controls implement this spectrum's lookup.
    qc.cry(math.pi, clock[0], anc[0])
    qc.cry(math.pi / 3, clock[1], anc[0])
    qc.append(est.inverse(), clock[:] + x[:])
    if measure:
        m = ClassicalRegister(2, "m")
        qc.add_register(m)
        qc.measure(anc[0], m[0])
        qc.measure(x[0], m[1])
    return qc


def exact_result():
    # Statevector index order: x clock1 clock0 anc. anc is least significant.
    state = np.asarray(Statevector(hhl_circuit(False)).data)
    accepted = state[1::2]
    success = float(np.vdot(accepted, accepted).real)
    # The clock must be 00 after uncomputation; indices 1 and 9 hold x=0,1.
    solution = state[[1, 9]] / math.sqrt(success)
    return success, solution


def main():
    x = np.linalg.solve(A, B)
    success, solution = exact_result()
    counts = sample(hhl_circuit(), 20000, 3)
    kept = np.array([counts.get("01", 0), counts.get("11", 0)])
    print("Classical solution:", x)
    print("Normalized solution amplitudes:", np.round(solution.real, 6))
    print(f"Exact post-selection probability: {success:.6f}")
    print("Exact conditional probabilities:", np.round(abs(solution) ** 2, 6))
    print(f"Sampled conditional probabilities: {np.round(kept/kept.sum(), 4)}; kept={kept.sum()}/20000")
    return {"success": success, "exact": (abs(solution) ** 2).tolist(),
            "sampled": (kept / kept.sum()).tolist(), "counts": counts}


if __name__ == "__main__":
    main()
