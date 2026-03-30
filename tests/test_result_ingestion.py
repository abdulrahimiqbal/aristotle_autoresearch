import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from dataclasses import replace

from research_orchestrator.result_ingestion import ingest_provider_result, prepare_ingested_result, validate_verification_record
from research_orchestrator.types import (
    ArtifactProvenance,
    ProviderMetadata,
    ProviderResult,
    VerificationArtifactKind,
    VerificationObservation,
    VerificationRecord,
    VerificationRunMetadata,
    VerificationSchemaVersion,
    VerificationStatus,
)


class ResultIngestionTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="result_ingestion_test_"))

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_validation_success_for_fully_populated_structured_record(self):
        record = VerificationRecord(
            schema_version=VerificationSchemaVersion.V1.value,
            provider=ProviderMetadata(
                provider_name="mock",
                adapter_name="test-adapter",
                adapter_version="1",
                provider_status="succeeded",
            ),
            run=VerificationRunMetadata(
                parser_version="1",
                evaluator_version="1",
                semantic_memory_version="1",
                schema_version=VerificationSchemaVersion.V1.value,
            ),
            verification_status=VerificationStatus.PROVED.value,
            theorem_status="verified",
            proved_lemmas=[
                VerificationObservation(
                    text="lemma bridge : True",
                    artifact_kind=VerificationArtifactKind.LEMMA.value,
                    provenance=[ArtifactProvenance(kind="artifact", path="/tmp/demo.lean", source="lean")],
                )
            ],
        )
        self.assertEqual(validate_verification_record(record), [])

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
        self.assertIsNotNone(result.verification_record)

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

    def test_counterexample_hint_can_remain_partial_when_artifacts_show_ongoing_formalization(self):
        lean_file = self.tempdir / "PartialMain.lean"
        lean_file.write_text(
            "lemma coverage_bridge (n : Nat) : True := by\n"
            "  trivial\n"
            "have density_step : True := by\n"
            "  trivial\n"
            "theorem main_target : True := by\n"
            "  sorry\n",
            encoding="utf-8",
        )
        log_file = self.tempdir / "partial_solver.log"
        log_file.write_text(
            "unsolved goal: show coverage_bound for all n\n"
            "blocked on: transfer density argument\n"
            "missing assumption: finite_support\n"
            "suffices: prove density_step first\n"
            "counterexample: n = 42 breaks the weakened variant\n",
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
        self.assertTrue(result.counterexample_witnesses)
        self.assertTrue(result.candidate_lemmas)
        self.assertTrue(result.unresolved_goals)

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

    def test_partial_provider_output_uses_fallback_parsing(self):
        prepared = prepare_ingested_result(
            ProviderResult(
                status="succeeded",
                blocker_type="formalization",
                raw_stdout="generated lemma: bridge helper\nunsolved goal: show Q n",
                metadata={"provider_name": "mock"},
            )
        )
        self.assertEqual(prepared.provider_result.proof_outcome, "partial")
        self.assertTrue(prepared.verification_record.generated_lemmas)
        self.assertTrue(prepared.verification_record.unsolved_goals)

    def test_malformed_structured_record_creates_validation_issue(self):
        record = VerificationRecord(
            schema_version="999",
            provider=ProviderMetadata(provider_name="mock"),
            run=VerificationRunMetadata(),
            verification_status="definitely_not_valid",
        )
        prepared = prepare_ingested_result(
            ProviderResult(
                status="failed",
                blocker_type="unknown",
                metadata={"provider_name": "mock"},
                verification_record=record,
            )
        )
        self.assertGreaterEqual(len(prepared.validation_issues), 2)
        self.assertIn("validation_issues", prepared.provider_result.metadata)

    def test_backward_compatibility_when_only_raw_text_fields_are_available(self):
        result = ingest_provider_result(
            ProviderResult(
                status="failed",
                blocker_type="unknown",
                raw_stdout="Need: prove bridge lemma\nblocked on: missing density estimate",
            )
        )
        self.assertTrue(result.unresolved_goals)
        self.assertTrue(result.blocked_on)
        self.assertIsNotNone(result.verification_record)


if __name__ == "__main__":
    unittest.main()
