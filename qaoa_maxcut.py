"""Part 5: ideal statevector training on one triangular-prism graph."""
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from common import sample

EDGES = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]


def cut_value(bits):
    side = bits[::-1]
    return sum(side[i] != side[j] for i, j in EDGES)


CUTS = np.array([cut_value(format(z, "06b")) for z in range(64)])


def qaoa_circuit(gammas, betas):
    if len(gammas) != len(betas):
        raise ValueError("One gamma and beta per layer")
    qc = QuantumCircuit(6)
    qc.h(range(6))
    for gamma, beta in zip(gammas, betas):
        for i, j in EDGES:
            qc.rzz(2 * gamma, i, j)
        qc.rx(2 * beta, range(6))
    return qc


def expected_cut(params):
    p = len(params) // 2
    probs = Statevector(qaoa_circuit(params[:p], params[p:])).probabilities()
    return float(probs @ CUTS)


def optimize(p, restarts=20, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    evaluations = 0
    for _ in range(restarts):
        result = minimize(lambda v: -expected_cut(v), rng.uniform(0, np.pi, 2 * p),
                          method="COBYLA", options={"maxiter": 500})
        evaluations += result.nfev
        if best is None or result.fun < best.fun:
            best = result
    return best.x, -best.fun, evaluations


def main():
    print(f"Classical exhaustive optimum: {CUTS.max()}; optimal strings: {sum(CUTS == CUTS.max())}/64")
    print(f"Random expected cut: {CUTS.mean():.3f}")
    rows = []
    for p in (1, 2, 3):
        params, value, evaluations = optimize(p)
        rows.append({"p": p, "value": value, "evaluations": evaluations, "params": params.tolist()})
        print(f"p={p}; expected cut={value:.3f}; ratio={value/7:.3f}; objective calls={evaluations}")
    qc = qaoa_circuit(params[:3], params[3:])
    qc.measure_all()
    counts = sample(qc, 4096, 5)
    hits = sum(count for bits, count in counts.items() if cut_value(bits) == 7)
    print(f"Optimal samples: {hits}/4096; random probability=6/64")
    return {"rows": rows, "counts": counts, "hits": hits}


if __name__ == "__main__":
    main()
