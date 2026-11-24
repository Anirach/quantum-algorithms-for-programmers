"""Part 3: dense 16x16 permutation gates are ONLY for this tiny demo."""
import math
from fractions import Fraction
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
from common import inverse_qft, sample

N, A, N_COUNT, N_WORK = 15, 7, 8, 4


def modmul_gate(multiplier):
    if math.gcd(multiplier, N) != 1:
        raise ValueError("Multiplication must be a reversible permutation")
    matrix = np.zeros((16, 16))
    for y in range(16):
        matrix[(multiplier * y) % N if y < N else y, y] = 1
    return UnitaryGate(matrix, label=f"x{multiplier} mod 15")


def period_finding_circuit():
    qc = QuantumCircuit(N_COUNT + N_WORK, N_COUNT)
    work = list(range(N_COUNT, N_COUNT + N_WORK))
    qc.h(range(N_COUNT))
    qc.x(work[0])
    for j in range(N_COUNT):
        multiplier = pow(A, 2 ** j, N)
        qc.append(modmul_gate(multiplier).control(1), [j] + work)
    qc.append(inverse_qft(N_COUNT), range(N_COUNT))
    qc.measure(range(N_COUNT), range(N_COUNT))
    return qc


def factors_from_measurement(measured):
    r = Fraction(measured, 2 ** N_COUNT).limit_denominator(N).denominator
    if r % 2 or pow(A, r, N) != 1:
        return r, None
    half = pow(A, r // 2, N)
    factors = tuple(sorted((math.gcd(half - 1, N), math.gcd(half + 1, N))))
    if any(f in (1, N) for f in factors) or math.prod(factors) != N:
        return r, None
    return r, factors


def main():
    counts = sample(period_finding_circuit(), 2048, 11)
    print("N=15; a=7; counting=8; work=4; shots=2048")
    for bits, count in sorted(counts.items()):
        y = int(bits, 2)
        r, factors = factors_from_measurement(y)
        print(f"y={y:3d}; shots={count:4d}; phase={y/256:.2f}; candidate r={r}; factors={factors}")
    return {"counts": counts, "shots": 2048}


if __name__ == "__main__":
    main()
