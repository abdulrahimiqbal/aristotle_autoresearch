import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate
from research_orchestrator.manager import generate_frontier
from research_orchestrator.reporter import build_report


class Erdos123CampaignTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="erdos123_campaign_test_"))
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_seeded_richer_move_families_and_discovery_question_are_available(self):
        candidates = generate_move_candidates(
            charter=self.charter,
            conjecture=self.conjecture,
            experiments=[],
            recurring_lemmas=[],
            recurring_subgoals=[],
            recurring_proof_traces=[],
            no_signal_branches=[],
            discovery_questions=[],
            all_conjectures=[self.conjecture],
        )
        move_families = {item.move_family for item in candidates}
        self.assertIn("invariant_mining", move_families)
        self.assertIn("extremal_case", move_families)
        self.assertIn("decompose_subclaim", move_families)
        self.assertIn("adversarial_counterexample", move_families)
        self.assertIn("witness_minimization", move_families)
        self.assertIn("transfer_reformulation", move_families)

        candidate = next(item for item in candidates if item.move_family == "invariant_mining")
        brief = materialize_candidate(
            charter=self.charter,
            conjecture=self.conjecture,
            workspace_root=str(self.tempdir / "work"),
            experiments=[],
            candidate=candidate,
            discovery_questions=[],
        )
        text = Path(brief.lean_file).read_text(encoding="utf-8")
        self.assertEqual(brief.theorem_family_id, "erdos_problem")
        self.assertEqual(brief.discovery_question_id, "erdos-123-dq-boundary")
        self.assertIn("d-completeness boundary cases", brief.candidate_metadata["campaign_focus"])
        self.assertIn("erdos-123 focus", text)
        self.assertIn("invariant target", text)

    def test_frontier_tracks_campaign_priority_without_overpreferring_legacy_counterexample(self):
        db = Database(self.tempdir / "state.sqlite")
        db.initialize()
        db.save_project(self.charter)
        db.save_conjecture(self.conjecture)

        frontier = generate_frontier(db, self.charter.project_id, self.tempdir / "frontier_work")
        by_family = {item["move_family"]: item for item in frontier}

        self.assertIn("legacy.counterexample_mode", by_family)
        self.assertIn("adversarial_counterexample", by_family)
        self.assertIn("witness_minimization", by_family)
        self.assertGreater(by_family["adversarial_counterexample"]["campaign_priority"], 0)
        self.assertGreater(by_family["witness_minimization"]["campaign_priority"], 0)
        self.assertLess(by_family["legacy.counterexample_mode"]["campaign_priority"], 0)

        db.close()

    def test_report_and_health_surface_campaign_tuning(self):
        db = Database(self.tempdir / "report_state.sqlite")
        db.initialize()
        db.save_project(self.charter)
        db.save_conjecture(self.conjecture)

        frontier = generate_frontier(db, self.charter.project_id, self.tempdir / "report_work")
        health = db.campaign_health(self.charter.project_id, frontier=frontier)
        report = build_report(db, self.charter.project_id)

        self.assertIn("high_priority_frontier_share", health["signals"])
        self.assertGreater(health["signals"]["high_priority_frontier_share"], 0.0)
        self.assertIn("Conjecture Tuning", report)
        self.assertIn("preferred move families", report)
        self.assertIn("seed question [boundary_case]", report)

        db.close()


if __name__ == "__main__":
    unittest.main()
