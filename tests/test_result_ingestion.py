import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.result_ingestion import ingest_provider_result
from research_orchestrator.types import ProviderResult


class ResultIngestionTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="result_ingestion_test_"))

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_proved_output_is_classified_as_proved(self):
        result = ingest_provider_result(
            ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                raw_stdout="Proof complete. All goals solved.",
            )
        )
        self.assertEqual(result.proof_outcome, "proved")
        self.assertEqual(result.status, "succeeded")

    def test_partial_lean_artifact_extracts_candidate_lemmas_and_subgoals(self):
        lean_file = self.tempdir / "Main.lean"
        lean_file.write_text(
            "lemma bridge_helper (n : Nat) : True := by\n  trivial\n"
            "have bridge_mid : True := by\n  trivial\n"
            "theorem final_target : True := by\n  trivial\n",
            encoding="utf-8",
        )
        log_file = self.tempdir / "solver.log"
        log_file.write_text(
            "Need: prove the bridge_helper first.\n"
            "unsolved goal: show P n\n"
            "suffices: show Q n\n"
            "blocked on: transfer density\n",
            encoding="utf-8",
        )
        result = ingest_provider_result(
            ProviderResult(
                status="succeeded",
                blocker_type="formalization",
                artifacts=[str(lean_file), str(log_file)],
            )
        )
        self.assertEqual(result.proof_outcome, "partial")
        self.assertEqual(result.status, "stalled")
        self.assertTrue(any("bridge_helper" in item for item in result.candidate_lemmas))
        self.assertIn("show P n", result.unresolved_goals)
        self.assertTrue(result.proof_trace_fragments)
        self.assertTrue(result.normalized_candidate_lemmas)
        self.assertTrue(result.normalized_unresolved_goals)
        self.assertGreater(result.new_signal_count, 0)
        self.assertTrue(result.artifact_inventory)

    def test_counterexample_signal_is_classified_as_disproved(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="structural",
                raw_stderr="Counterexample: n = 7 breaks the weakened variant.\n",
            )
        )
        self.assertEqual(result.proof_outcome, "disproved")
        self.assertEqual(result.status, "failed")
        self.assertTrue(result.counterexample_witnesses)

    def test_timeout_signal_is_classified_as_stalled(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="search",
                raw_stderr="Search budget exhausted after timeout while exploring tactics.",
            )
        )
        self.assertEqual(result.proof_outcome, "stalled")
        self.assertEqual(result.status, "stalled")

    def test_invalid_api_key_is_classified_as_auth_failure(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="malformed",
                raw_stderr="ERROR - Invalid API key. Please check your API key and try again.",
            )
        )
        self.assertEqual(result.proof_outcome, "auth_failure")
        self.assertEqual(result.status, "failed")

    def test_dns_failure_is_classified_as_infra_failure(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="dns_failure",
                raw_stderr="Request failed: [Errno 8] nodename nor servname provided, or not known",
            )
        )
        self.assertEqual(result.proof_outcome, "infra_failure")

    def test_path_failure_is_classified_as_malformed(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="malformed",
                raw_stderr="The `aristotle` CLI executable was not found on PATH.",
            )
        )
        self.assertEqual(result.proof_outcome, "malformed")

    def test_traceback_without_signal_is_unknown(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="unknown",
                raw_stderr="Traceback (most recent call last):\nValueError: boom",
            )
        )
        self.assertEqual(result.proof_outcome, "unknown")


if __name__ == "__main__":
    unittest.main()
