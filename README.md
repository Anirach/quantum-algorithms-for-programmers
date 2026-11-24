# Quantum Algorithms for Programmers

Seven runnable lessons for the [Thai–English tutorial series](https://anirach.com/blog/#series-quantum-programmers) by Anirach Mingkhwan. Adapted from the author's *Quantum Algorithms for Programmers, Technical Guide, Edition 1.0* (November 2026). The original four examples are adapted into shared, tested modules; parts 1, 6 and 7 add new experiments.

Learn what interference does, why Grover is quadratic, how Shor extracts a period, what HHL returns, how QAOA trains, and how to judge a speedup claim. These are local educational simulations. No account, API key, network connection after installation, or quantum hardware is needed. No result here demonstrates a practical quantum advantage.

## Install and run

Use Python 3.11–3.13 with pip and Git. Verified locally with Python 3.13, Qiskit 2.6.2, Aer 0.18.4, NumPy 2.5.5 and SciPy 1.18.1 on 24 November 2026. The direct dependencies are pinned in `requirements.txt`; `requirements-lock.txt` records the full locally tested environment. Platform-specific wheels and later transitive dependencies may produce small numerical differences. Use a virtual environment rather than changing a system Python.

```bash
git clone https://github.com/Anirach/quantum-algorithms-for-programmers.git
cd quantum-algorithms-for-programmers
git checkout v1.0.0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python foundations.py
python grover_search.py
python shor_factor15.py
python hhl_2x2.py
python qaoa_maxcut.py
python quantum_simulation.py
python engineering_scorecard.py
```

Windows activation: `.venv\Scripts\activate`. `python -m pip install -r requirements-lock.txt` installs the full tested dependency set where wheels are supported. Tests take seconds; the QAOA lesson performs 20 optimizer restarts at each of three depths and takes longer. No payment or remote hardware job is involved.

## Lesson map

Each post contains a shorter excerpt; the file below is the complete executable program. All checks live in [tests/test_algorithms.py](tests/test_algorithms.py).

| Part | Website | Run | Test class | Exercise |
|---|---|---|---|---|
| 1 | [Amplitudes and interference](https://anirach.com/blog/quantum-programmers-foundations.html) | `python foundations.py` | `FoundationsTests` | [1](exercises/01.md) |
| 2 | [Grover search](https://anirach.com/blog/quantum-programmers-grover.html) | `python grover_search.py` | `GroverTests` | [2](exercises/02.md) |
| 3 | [Shor period finding](https://anirach.com/blog/quantum-programmers-shor.html) | `python shor_factor15.py` | `ShorTests` | [3](exercises/03.md) |
| 4 | [HHL linear systems](https://anirach.com/blog/quantum-programmers-hhl.html) | `python hhl_2x2.py` | `HHLTests` | [4](exercises/04.md) |
| 5 | [QAOA MaxCut](https://anirach.com/blog/quantum-programmers-qaoa.html) | `python qaoa_maxcut.py` | `QAOATests` | [5](exercises/05.md) |
| 6 | [Quantum simulation](https://anirach.com/blog/quantum-programmers-simulation.html) | `python quantum_simulation.py` | `SimulationTests` | [6](exercises/06.md) |
| 7 | [Engineering scorecard](https://anirach.com/blog/quantum-programmers-scorecard.html) | `python engineering_scorecard.py` | `ScorecardTests` | [7](exercises/07.md) |

Run one class, for example: `python -m unittest discover -s tests -p test_algorithms.py -k HHLTests -v`.

## Expected results

- Foundations: both intermediate probability distributions are `[0.5, 0.5]`; final H distinguishes phase, giving `[1, 0]` versus `[0, 1]`. Bell probabilities are `[0.5, 0, 0, 0.5]`.
- Grover: marked string `1011`; three iterations; exact success `0.961319`; 3,928 hits in 4,096 shots. Five iterations reduce theoretical success to `0.1255`.
- Shor: counting values 0, 64, 128 and 192; phases 1/4 and 3/4 yield factors `(3, 5)`. Phase 1/2 yields denominator 2 and requires a retry. Our seeded counts are 488, 500, 511 and 549.
- HHL: classical solution `[0.75, -0.25]`; normalized amplitudes `[0.948683, -0.316228]` up to global phase; exact post-selection `0.625`; conditional probabilities `[0.9, 0.1]`. Seeded shots retain 12,597/20,000.
- QAOA: exhaustive optimum 7 of 9 edges; six optimal bitstrings out of 64. Expected cuts for p=1,2,3 are approximately 5.939, 6.603, 6.878; objective call totals 762, 3,137, 9,157; p=3 produces 3,791 optimal samples out of 4,096 in this run. Optimization results can differ across numerical-library versions.
- Simulation: exact `<ZZ>` at t=1 is `0.352560`. With 1,2,4,8,16 first-order product steps, infidelity is approximately .351853, .064421, .014434, .003487, .000862.
- Scorecard: a hypothetical 0.1-second quantum kernel becomes a 1.5-second workflow after preparation, five attempts and postprocessing; against a 1-second baseline the speedup is `0.667x`. These times are illustrative inputs, not measurements.

Fixed simulator and transpiler seeds make the recorded run repeatable in the tested environment, not universally identical across versions. Statevector probabilities and invariants are the correctness criteria; shot counts are statistical samples. Tests use tolerances and independent analytic or classical references instead of requiring one lucky histogram.

## Important implementation boundaries

`common.py` supplies the inverse QFT and seeded ideal sampling. Qiskit integer indices and count strings use qubit 0 as the least significant bit; the string's rightmost character is qubit 0 when measuring in the order used here. See [IBM's bit-ordering documentation](https://quantum.cloud.ibm.com/docs/en/qiskit/bit-ordering).

- **Grover:** the known marked string constructs a phase-oracle fixture, allowing us to test interference. A real search requires a reversible predicate supplied independently of its unknown answer. Query counts exclude oracle construction, data access, compilation and error correction.
- **Shor:** a 16×16 permutation matrix implements modular multiplication for N=15. Dense matrices scale exponentially in register width; increasing `N` does not produce a scalable factoring implementation. Continued-fraction postprocessing handles the illustrated samples, not all recovery strategies.
- **HHL:** the two-clock-bit rotation lookup is valid only for this exact positive spectrum {1,2}. Changing the matrix requires redesigning phase scaling, eigenvalue precision, sign handling and reciprocal rotations. Dense `expm` is a tiny-example construction, not a scalable Hamiltonian oracle. The tests verify the relative sign and clock reset, which probabilities alone cannot establish.
- **QAOA:** all objective evaluations inspect exact statevector probabilities on a classical computer. Hardware training would need repeated shot-based estimates, noise management and a new accounting budget. The optimization result on one graph is not a worst-case guarantee or benchmark against an industrial solver.
- **Simulation:** the two-qubit model illustrates product-formula error. The terms do not commute. More steps reduce approximation error here while increasing gate count; hardware noise can reverse the benefit. Classical exact `expm` is the verification reference, and is preferable at this toy size.
- **Scorecard:** explicit hypothetical times teach whole-workflow accounting. This ledger is not a production scheduler, resource estimator or forecast.

## Troubleshooting

| Problem | What to check |
|---|---|
| `No module named qiskit` | Activate the virtual environment and use its `python -m pip`. |
| Aer installation cannot find a wheel | Use a supported 64-bit Python 3.11–3.13 platform; inspect pip's platform error before trying a source build. |
| A count string looks reversed | Read qubit 0 from the right and check the explicit measurement-to-classical-bit mapping. |
| Counts differ slightly | Compare probabilities and shot uncertainty; check dependency versions and seeds. |
| QAOA takes longer | Training includes 60 optimization runs. For exploration call `optimize(p, restarts=2)`; this changes the experiment and may lower quality. |
| HHL loses a minus sign | Counts expose squared magnitudes; inspect interference or the conditional statevector. |
| More qubits exhaust RAM | Dense statevectors need about `16 * 2**n` bytes for complex128, before workspaces. Keep the examples small. |

## Sources

The blog posts cite the relevant primary papers. Core references: [Grover](https://arxiv.org/abs/quant-ph/9605043), [Shor](https://arxiv.org/abs/quant-ph/9508027), [HHL](https://arxiv.org/abs/0811.3171), [QAOA](https://arxiv.org/abs/1411.4028), and [quadratic speedup overheads](https://arxiv.org/abs/2011.04149). The original PDF is kept by the author; it is not bundled here. Website illustrations retain attribution in their captions.

MIT licensed. Code is for learning and small-instance verification.
