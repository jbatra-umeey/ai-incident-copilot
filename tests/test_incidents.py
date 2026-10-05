import tempfile
import unittest
from pathlib import Path
from app import Event, compare, investigate, load_events, percentile
from model import ModelError


def cohort(window, duration, count=30, tier="budget", failed=False):
    return [Event(f"{window}-{tier}-{i}", window, "editor", tier, duration, failed) for i in range(count)]


class IncidentTests(unittest.TestCase):
    def test_latency_regression(self):
        result = investigate(cohort("baseline", 100) + cohort("current", 140))
        self.assertEqual(result["evidence"][0]["p95_change_pct"], 40)
        self.assertEqual(result["status"], "review_required")
        self.assertEqual(result["executed_actions"], [])

    def test_sample_mix_shift_does_not_become_latency_regression(self):
        events = (cohort("baseline", 100, 100, "fast") + cohort("current", 100, 30, "fast")
                  + cohort("baseline", 1000, 30) + cohort("current", 1000, 100))
        self.assertFalse(any(e["regression"] for e in compare(events)["evidence"]))

    def test_insufficient_samples_are_skipped(self):
        result = compare(cohort("baseline", 100) + cohort("current", 300, 2))
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["skipped"][0]["current_n"], 2)

    def test_error_regression_independent_of_latency(self):
        evidence = compare(cohort("baseline", 100) + cohort("current", 100, failed=True))["evidence"][0]
        self.assertTrue(evidence["regression"])
        self.assertEqual(evidence["error_rate_change_pp"], 100)

    def test_zero_baseline_has_no_infinite_ratio(self):
        evidence = compare(cohort("baseline", 0) + cohort("current", 100))["evidence"][0]
        self.assertIsNone(evidence["p95_change_pct"])

    def test_percentile_interpolation(self):
        self.assertAlmostEqual(percentile([10, 20], .95), 19.5)

    def test_duplicate_event_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text("session,window,workflow,tier,duration_ms,failed\na,current,editor,budget,10,0\na,current,editor,budget,10,0\n")
            with self.assertRaises(ValueError):
                load_events(path)

    def test_invented_model_evidence_rejected(self):
        class Fake:
            def json(self, *args, **kwargs):
                return {"hypotheses": [{"hypothesis": "Maybe", "next_check": "Check", "evidence_ids": ["E99"]}]}
        with self.assertRaises(ModelError):
            investigate(cohort("baseline", 100) + cohort("current", 140), Fake())


if __name__ == "__main__":
    unittest.main()
