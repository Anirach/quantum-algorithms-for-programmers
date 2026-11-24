"""Part 7: hypothetical cost ledger. These are NOT hardware measurements."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Budget:
    classical_seconds: float
    prepare_seconds: float
    quantum_seconds_per_attempt: float
    attempts: int
    postprocess_seconds: float

    def total(self):
        values = (self.classical_seconds, self.prepare_seconds,
                  self.quantum_seconds_per_attempt, self.postprocess_seconds)
        if any(not math.isfinite(v) or v < 0 for v in values):
            raise ValueError("Times must be finite and nonnegative")
        if not isinstance(self.attempts, int) or self.attempts < 1:
            raise ValueError("Include at least one attempt")
        return self.prepare_seconds + self.attempts * self.quantum_seconds_per_attempt + self.postprocess_seconds


def main():
    fast_kernel = Budget(1.0, 0.8, 0.1, 5, 0.2)
    print("Hypothetical seconds; no hardware benchmark")
    print(f"Classical baseline: {fast_kernel.classical_seconds:.2f}")
    print(f"Quantum workflow total: {fast_kernel.total():.2f}")
    print(f"End-to-end speedup: {fast_kernel.classical_seconds/fast_kernel.total():.3f}x")
    print("30-qubit complex128 statevector bytes:", 16 * 2 ** 30)


if __name__ == "__main__":
    main()
