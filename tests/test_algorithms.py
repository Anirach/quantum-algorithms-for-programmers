"""Independent small-instance oracles, phase-sensitive checks and accounting."""
import math
import unittest
import numpy as np
from scipy.linalg import expm
from qiskit.quantum_info import Operator, Statevector
import foundations as f
import grover_search as g
import shor_factor15 as s
import hhl_2x2 as h
import qaoa_maxcut as q
import quantum_simulation as sim
from common import inverse_qft, sample
from engineering_scorecard import Budget


class FoundationsTests(unittest.TestCase):
    def test_phase_requires_interference(self):
        a, out_a = f.interference(False)
        b, out_b = f.interference(True)
        np.testing.assert_allclose(a, b)
        np.testing.assert_allclose(out_a, [1, 0], atol=1e-12)
        np.testing.assert_allclose(out_b, [0, 1], atol=1e-12)

    def test_bell_joint_distribution(self):
        np.testing.assert_allclose(f.bell(), [.5, 0, 0, .5], atol=1e-12)


class GroverTests(unittest.TestCase):
    def test_oracle_flips_only_marked_state(self):
        diagonal = np.ones(16); diagonal[11] = -1
        np.testing.assert_allclose(Operator(g.phase_oracle(4, "1011")).data,
                                   np.diag(diagonal), atol=1e-12)

    def test_diffuser_up_to_global_phase(self):
        expected = 2 * np.ones((16, 16)) / 16 - np.eye(16)
        np.testing.assert_allclose(Operator(g.diffuser(4)).data, -expected, atol=1e-12)

    def test_probability_matches_rotation(self):
        for k in range(6):
            p = Statevector(g.grover_circuit(iterations=k, measure=False)).probabilities()[11]
            self.assertAlmostEqual(p, g.theoretical_probability(4, k))

    def test_overrotation_and_bit_order(self):
        self.assertLess(g.theoretical_probability(4, 5), g.theoretical_probability(4, 3))
        for target in ("0000", "0010", "1011", "1111"):
            p = Statevector(g.grover_circuit(marked=target, measure=False)).probabilities()
            self.assertEqual(int(np.argmax(p)), int(target, 2))

    def test_invalid_marked_string(self):
        with self.assertRaises(ValueError): g.phase_oracle(4, "xyz")

    def test_sampling_close_to_theory(self):
        counts = sample(g.grover_circuit(), 4096, 7)
        self.assertLess(abs(counts.get("1011", 0)/4096 - g.theoretical_probability(4, 3)), .025)


class ShorTests(unittest.TestCase):
    def test_inverse_qft_equals_inverse_dft(self):
        j, k = np.meshgrid(np.arange(16), np.arange(16), indexing="ij")
        expected = np.exp(-2j * np.pi * j * k / 16) / 4
        np.testing.assert_allclose(Operator(inverse_qft(4)).data, expected, atol=1e-12)

    def test_modular_permutation_and_padding(self):
        for multiplier in (7, 4, 1):
            u = Operator(s.modmul_gate(multiplier)).data
            np.testing.assert_allclose(u.conj().T @ u, np.eye(16), atol=1e-12)
            for y in range(16):
                self.assertEqual(np.argmax(abs(u[:, y])), multiplier*y % 15 if y < 15 else y)

    def test_noninvertible_multiplier_rejected(self):
        with self.assertRaises(ValueError): s.modmul_gate(3)

    def test_reduced_fraction_needs_retry(self):
        self.assertEqual(s.factors_from_measurement(0), (1, None))
        self.assertEqual(s.factors_from_measurement(128), (2, None))
        self.assertEqual(s.factors_from_measurement(64), (4, (3, 5)))
        self.assertEqual(s.factors_from_measurement(192), (4, (3, 5)))

    def test_period_finding_peaks(self):
        qc = s.period_finding_circuit().remove_final_measurements(inplace=False)
        probabilities = Statevector(qc).probabilities(qargs=list(range(8)))
        expected = np.zeros(256); expected[[0, 64, 128, 192]] = .25
        np.testing.assert_allclose(probabilities, expected, atol=1e-10)


class HHLTests(unittest.TestCase):
    def test_solution_including_relative_sign(self):
        success, state = h.exact_result()
        expected = np.linalg.solve(h.A, h.B)
        expected = expected / np.linalg.norm(expected)
        self.assertAlmostEqual(success, .625)
        self.assertTrue(Statevector(state).equiv(Statevector(expected)))
        np.testing.assert_allclose(abs(state) ** 2, [.9, .1], atol=1e-10)

    def test_clock_is_uncomputed(self):
        state = Statevector(h.hhl_circuit(False)).data
        forbidden = [i for i in range(16) if ((i >> 1) & 3) != 0]
        self.assertLess(np.sum(abs(state[forbidden]) ** 2), 1e-12)

    def test_postselection_uses_correct_classical_bits(self):
        counts = sample(h.hhl_circuit(), 5000, 3)
        accepted = counts.get("01", 0) + counts.get("11", 0)
        self.assertLess(abs(accepted/5000 - .625), .04)
        self.assertLess(abs(counts.get("01", 0)/accepted - .9), .04)


class QAOATests(unittest.TestCase):
    def test_exhaustive_classical_baseline(self):
        self.assertEqual(q.CUTS.max(), 7)
        self.assertEqual(sum(q.CUTS == 7), 6)
        self.assertAlmostEqual(q.CUTS.mean(), 4.5)
        for i in range(64):
            self.assertEqual(q.CUTS[i], q.CUTS[i ^ 63])

    def test_zero_angles_are_uniform(self):
        self.assertAlmostEqual(q.expected_cut(np.zeros(2)), 4.5)

    def test_known_p1_angles_improve_random_baseline(self):
        # Fixed validation point, independent of the optimization procedure.
        self.assertGreater(q.expected_cut(np.array([.3, -.3])), 5.5)

    def test_optimized_p1_and_accounting(self):
        params, value, calls = q.optimize(1, restarts=2)
        self.assertGreater(value, 5.8)
        self.assertLessEqual(value, 7 + 1e-9)
        self.assertGreater(calls, 2)
        self.assertAlmostEqual(q.expected_cut(params), value)


class SimulationTests(unittest.TestCase):
    def test_zero_time_is_identity(self):
        np.testing.assert_allclose(Operator(sim.trotter(3, 0)).data, np.eye(4), atol=1e-12)

    def test_trotter_converges_in_full_unitary(self):
        exact = expm(-1j * sim.H)
        errors = [np.linalg.norm(Operator(sim.trotter(m)).data - exact) for m in (2, 4, 8, 16)]
        self.assertTrue(all(a > b for a, b in zip(errors, errors[1:])))

    def test_observable_and_fidelity(self):
        exact = expm(-1j * sim.H) @ np.array([1., 0, 0, 0])
        approximate = Statevector(sim.trotter(16)).data
        self.assertGreater(abs(np.vdot(exact, approximate)) ** 2, .995)
        self.assertLess(abs(np.vdot(exact, sim.ZZ @ exact).real), 1)

    def test_invalid_step_count(self):
        with self.assertRaises(ValueError): sim.trotter(0)


class ScorecardTests(unittest.TestCase):
    def test_whole_workflow_cost(self):
        b = Budget(1, .8, .1, 5, .2)
        self.assertAlmostEqual(b.total(), 1.5)
        self.assertLess(b.classical_seconds/b.total(), 1)

    def test_invalid_times_and_attempts(self):
        for b in (Budget(1, -1, 1, 1, 0), Budget(1, 0, math.nan, 1, 0), Budget(1, 0, 1, 0, 0)):
            with self.assertRaises(ValueError): b.total()


if __name__ == "__main__":
    unittest.main()
