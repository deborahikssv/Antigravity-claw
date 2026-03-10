"""tests/test_server.py — unit tests for antigravity-claw core logic"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest
from server import compute_antigravity, levitate, antigravity_poem


class TestComputeAntigravity(unittest.TestCase):
    def test_inverted_force_is_negative(self):
        r = compute_antigravity(10, 100, invert=True)
        self.assertLess(r["force_newtons"], 0)

    def test_normal_force_is_positive(self):
        r = compute_antigravity(10, 100, invert=False)
        self.assertGreater(r["force_newtons"], 0)

    def test_zero_altitude_escape_velocity(self):
        r = compute_antigravity(1, 0)
        self.assertEqual(r["escape_velocity_ms"], 0.0)

    def test_energy_is_always_positive(self):
        r = compute_antigravity(5, 200, invert=True)
        self.assertGreater(r["energy_joules"], 0)


class TestLevitate(unittest.TestCase):
    def test_trajectory_has_11_steps(self):
        r = levitate("apple", 0.18, 42)
        self.assertEqual(len(r["trajectory"]), 11)

    def test_first_altitude_is_zero(self):
        r = levitate("apple", 0.18, 42)
        self.assertAlmostEqual(r["trajectory"][0]["altitude_m"], 0)

    def test_last_altitude_equals_target(self):
        r = levitate("apple", 0.18, 42)
        self.assertAlmostEqual(r["trajectory"][-1]["altitude_m"], 42, places=1)

    def test_status_contains_levitating(self):
        r = levitate("rock", 2, 10)
        self.assertIn("levitat", r["status"])


class TestPoem(unittest.TestCase):
    def test_returns_non_empty_string(self):
        p = antigravity_poem()
        self.assertIsInstance(p, str)
        self.assertGreater(len(p), 5)


if __name__ == "__main__":
    unittest.main()
