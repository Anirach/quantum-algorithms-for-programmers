"""Part 1: phase becomes observable only through interference."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def interference(phase_flip=False):
    qc = QuantumCircuit(1)
    qc.h(0)
    if phase_flip:
        qc.z(0)
    before = Statevector(qc).probabilities()
    qc.h(0)
    return before, Statevector(qc).probabilities()


def bell():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return Statevector(qc).probabilities()


def main():
    for flip in (False, True):
        before, after = interference(flip)
        print(f"Z={flip}: before final H {np.round(before, 3)}; after {np.round(after, 3)}")
    print("Bell probabilities [00,01,10,11]:", np.round(bell(), 3))


if __name__ == "__main__":
    main()
