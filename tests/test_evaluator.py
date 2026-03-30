import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from research_orchestrator.charter import load_charter
from research_orchestrator.evaluator import score_result
from research_orchestrator.result_ingestion import prepare_ingested_result
from research_orchestrator.types import ProviderResult


class EvaluatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.charter = load_charter(root / "examples" / "project_charter.json")

    def test_novelty_is_reduced_for_duplicates(self):
        unique = prepare_ingested_result(
            ProviderResult(
                status="stalled",
                blocker_type="formalization",
                generated_lemmas=["lemma bridge : True"],
                raw_stdout="unsolved goal: show P n",
                metadata={"provider_name": "mock"},
            )
        )
        duplicate = prepare_ingested_result(
            ProviderResult(
                status="stalled",
                blocker_type="formalization",
                generated_lemmas=["lemma bridge (n : Nat) : P n", "lemma bridge (m : Nat) : P m"],
                raw_stdout="unsolved goal: show P n",
                metadata={"provider_name": "mock"},
            )
        )
        unique_score = score_result(self.charter, unique.provider_result, verification_record=unique.verification_record, semantic_summary=unique.semantic_summary)
        duplicate_score = score_result(self.charter, duplicate.provider_result, verification_record=duplicate.verification_record, semantic_summary=duplicate.semantic_summary)
        self.assertGreater(unique_score.novelty, duplicate_score.novelty)

    def test_reusable_discoveries_score_above_shallow_churn(self):
        shallow = prepare_ingested_result(
            ProviderResult(
                status="stalled",
                blocker_type="unknown",
                raw_stdout="unsolved goal: show P n",
                metadata={"provider_name": "mock"},
            )
        )
        reusable = prepare_ingested_result(
            ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                proved_lemmas=["lemma reusable_bridge : True"],
                raw_stdout="Proof complete. All goals solved.",
                metadata={"provider_name": "mock"},
            )
        )
        shallow_score = score_result(self.charter, shallow.provider_result, verification_record=shallow.verification_record, semantic_summary=shallow.semantic_summary)
        reusable_score = score_result(self.charter, reusable.provider_result, verification_record=reusable.verification_record, semantic_summary=reusable.semantic_summary)
        self.assertGreater(reusable_score.total, shallow_score.total)

    def test_obstruction_and_boundary_discovery_change_score(self):
        boundary = prepare_ingested_result(
            ProviderResult(
                status="failed",
                blocker_type="structural",
                raw_stderr="counterexample: n = 5\nmissing assumption: monotonicity",
                metadata={"provider_name": "mock"},
            )
        )
        baseline = prepare_ingested_result(
            ProviderResult(
                status="stalled",
                blocker_type="unknown",
                raw_stdout="still exploring",
                metadata={"provider_name": "mock"},
            )
        )
        boundary_score = score_result(self.charter, boundary.provider_result, verification_record=boundary.verification_record, semantic_summary=boundary.semantic_summary)
        baseline_score = score_result(self.charter, baseline.provider_result, verification_record=baseline.verification_record, semantic_summary=baseline.semantic_summary)
        self.assertGreater(boundary_score.boundary_sharpness, baseline_score.boundary_sharpness)
        self.assertGreater(boundary_score.obstruction_discovery, baseline_score.obstruction_discovery)

    def test_simple_legacy_case_still_produces_stable_output(self):
        score = score_result(
            self.charter,
            ProviderResult(status="failed", blocker_type="unknown", raw_stderr="Traceback: boom"),
        )
        self.assertIsInstance(score.total, float)
        self.assertTrue(score.notes)


if __name__ == "__main__":
    unittest.main()
