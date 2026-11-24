"""Part 6: noncommuting two-qubit dynamics; compare Trotter to exact expm."""
import numpy as np
from scipy.linalg import expm
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

X = np.array([[0, 1], [1, 0]])
Z = np.diag([1., -1.])
I = np.eye(2)
ZZ = np.kron(Z, Z)
# Matrix order is q1 tensor q0, matching Qiskit statevector indexing.
H = ZZ + 0.7 * (np.kron(I, X) + np.kron(X, I))


def trotter(steps, t=1.0):
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be a positive integer")
    dt = t / steps
    qc = QuantumCircuit(2)
    for _ in range(steps):
        qc.rzz(2 * dt, 0, 1)
        qc.rx(1.4 * dt, [0, 1])
    return qc


def main():
    exact = expm(-1j * H) @ np.array([1., 0, 0, 0])
    exact_zz = float(np.vdot(exact, ZZ @ exact).real)
    print(f"Exact <ZZ> at t=1: {exact_zz:.6f}")
    rows = []
    for steps in (1, 2, 4, 8, 16):
        state = Statevector(trotter(steps)).data
        zz = float(np.vdot(state, ZZ @ state).real)
        infidelity = float(1 - abs(np.vdot(exact, state)) ** 2)
        rows.append({"steps": steps, "zz": zz, "infidelity": infidelity})
        print(f"steps={steps:2d}; <ZZ>={zz:.6f}; infidelity={infidelity:.6f}")
    return {"exact_zz": exact_zz, "rows": rows}


if __name__ == "__main__":
    main()
