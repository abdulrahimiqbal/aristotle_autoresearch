import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.llm_manager import BridgeHypothesis, CandidateAnnotation, EvidenceRef, build_campaign_brief
from research_orchestrator.manager import generate_frontier
from research_orchestrator.manager_policy import choose_candidates_for_submission
from research_orchestrator.replay import manager_llm_report
from research_orchestrator.types import CampaignInterpretation


def _candidate(experiment_id: str, *, llm_delta: float = 0.0, campaign_priority: float = 0.0):
    annotation = asdict(
        CandidateAnnotation(
            experiment_id=experiment_id,
            phase_alignment=1.0 if llm_delta else 0.0,
            failure_value=1.0 if llm_delta else 0.0,
            llm_delta=llm_delta,
        )
    )
    return {
        "experiment_id": experiment_id,
        "conjecture_id": "c1" if experiment_id.endswith("1") else "c2",
        "move": "reformulate",
        "move_family": "equivalent_view",
        "phase": "mapping",
        "objective": "probe structure",
        "expected_signal": "gain signal",
        "modification": {"form": f"alt-{experiment_id}"},
        "workspace_dir": f"/tmp/{experiment_id}",
        "lean_file": f"/tmp/{experiment_id}/Main.lean",
        "rationale": "",
        "candidate_metadata": {"campaign_priority": campaign_priority, "llm_annotation": annotation if llm_delta else {}},
        "llm_annotation": annotation if llm_delta else {},
        "existing_experiments": 0,
        "active_count_for_conjecture": 0,
        "duplicate_active_signature": False,
        "targets_recurring_structure": False,
        "signal_priority": 0,
        "no_signal_penalty": 0,
        "semantic_novelty": 0,
        "reuse_potential": 0,
        "obstruction_targeting": 0,
        "transfer_opportunity": 0,
        "campaign_priority": campaign_priority,
        "motif_id": "",
        "motif_reuse_count": 0,
        "signal_support": 0,
        "blocker_support": 0,
        "witness_support": 0,
        "assumption_boundary_support": 0,
        "recent_signal_velocity": 0,
        "discovery_priority": 0,
    }


class LLMManagerTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="llm_manager_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.db.save_project(charter)
        for name in (
            "erdos_123_d_complete_sequences.json",
            "erdos_181_hypercube_ramsey.json",
        ):
            self.db.save_conjecture(load_conjecture(root / "examples" / "conjectures" / "erdos" / name))
        self.project_id = charter.project_id

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_campaign_brief_covers_empty_small_and_large_state(self):
        empty_brief = build_campaign_brief(self.db, self.project_id)
        self.assertEqual(empty_brief.phase_estimate, "mapping")
        self.assertEqual(empty_brief.evidence_pack["frontier_summary"]["candidate_count"], 0)

        for idx in range(5):
            self.db.save_experiment_plan(
                {
                    "experiment_id": f"seed-{idx}",
                    "project_id": self.project_id,
                    "conjecture_id": "erdos-123" if idx % 2 == 0 else "erdos-181",
                    "phase": "mapping",
                    "move": "underspecify",
                    "objective": "seed",
                    "expected_signal": "seed",
                    "modification": {"mode": f"seed-{idx}"},
                    "workspace_dir": str(self.tempdir / f"seed-{idx}"),
                    "lean_file": str(self.tempdir / f"seed-{idx}" / "Main.lean"),
                    "candidate_metadata": {},
                }
            )
        large_brief = build_campaign_brief(self.db, self.project_id)
        self.assertEqual(large_brief.phase_estimate, "consolidation")
        titles = {section.title for section in large_brief.narrative_summary}
        self.assertIn("boundary map / witness signals", titles)
        self.assertIn("cross-conjecture transfer opportunities", titles)

    def test_bounded_llm_annotation_changes_ranking_without_bypassing_policy(self):
        frontier = [
            _candidate("exp-1", llm_delta=0.0, campaign_priority=1.0),
            _candidate("exp-2", llm_delta=2.0, campaign_priority=0.0),
        ]
        decision = choose_candidates_for_submission(
            db=self.db,
            project_id=self.project_id,
            frontier=frontier,
            max_count=1,
            llm_manager_mode="on",
        )
        self.assertEqual(decision.policy_path, "llm_assisted")
        self.assertEqual(decision.chosen[0].experiment_id, "exp-2")
        audit = next(item for item in decision.candidate_audits if item["experiment_id"] == "exp-2")
        self.assertGreater(audit["score_breakdown"]["llm_adjustments"]["total"], 0)

    def test_bridge_hypotheses_are_stored_and_surface_in_frontier(self):
        bridge = BridgeHypothesis(
            source_conjecture_id="erdos-123",
            target_conjecture_id="erdos-181",
            shared_structure="transfer bridge lemma",
            transfer_rationale="A reusable witness pattern appears to transfer.",
            suggested_move_family="transfer_reformulation",
            confidence=0.8,
            source_evidence=[
                EvidenceRef(
                    ref_type="lemma",
                    ref_id="lemma-1",
                    label="transfer bridge lemma",
                    conjecture_id="erdos-123",
                    metadata={"source_domain": "erdos_problem"},
                )
            ],
            evidence_refs=[EvidenceRef(ref_type="conjecture", ref_id="erdos-181", conjecture_id="erdos-181")],
        )
        with patch(
            "research_orchestrator.manager.feature_flags",
            return_value={
                "brief_generation": True,
                "interpretation": True,
                "annotation": False,
                "parameter_synthesis": False,
                "bridge_hypotheses": True,
            },
        ), patch(
            "research_orchestrator.manager.interpret_campaign",
            return_value=(
                CampaignInterpretation(
                    phase_assessment="mapping",
                    cross_conjecture_bridges=[bridge],
                    confidence=0.8,
                    observed_vs_inferred="inferred",
                ),
                {
                    "prompt_version": "test",
                    "model_version": "test-model",
                    "raw_response": "{}",
                    "parsed": {},
                    "validation_status": "valid",
                },
            ),
        ):
            frontier = generate_frontier(self.db, self.project_id, self.tempdir / "work")
        self.assertTrue(self.db.list_bridge_hypotheses(self.project_id))
        self.assertTrue(any(item["candidate_metadata"].get("bridge_hypothesis") for item in frontier))

    def test_manager_llm_report_aggregates_divergence(self):
        run_id = self.db.save_manager_run(
            project_id=self.project_id,
            provider="mock",
            policy_path="llm_assisted",
            jobs_synced=0,
            jobs_submitted=1,
            active_before=0,
            active_after=1,
            report_path=None,
            snapshot_path=None,
            summary={"submitted_experiments": []},
        )
        self.db.save_manager_candidate_audits(
            run_id,
            self.project_id,
            [
                {
                    "experiment_id": "exp-2",
                    "conjecture_id": "erdos-181",
                    "rank_position": 1,
                    "selected": True,
                    "selection_reason": "selected",
                    "policy_score": 3.0,
                    "score_breakdown": {"llm_adjustments": {"llm_delta": 1.5, "total": 1.5}},
                    "candidate": {"candidate_metadata": {"llm_parameter_synthesis": {"move_family": "equivalent_view"}}},
                }
            ],
        )
        self.db.save_campaign_interpretation(
            project_id=self.project_id,
            prompt_version="test",
            model_version="test-model",
            raw_response="{}",
            parsed={},
            validation_status="valid",
        )
        report = manager_llm_report(self.db, self.project_id)
        self.assertEqual(report["manager_runs"], 1)
        self.assertEqual(report["divergence_frequency"], 1.0)
        self.assertGreater(report["average_accepted_llm_delta"], 0.0)


if __name__ == "__main__":
    unittest.main()
