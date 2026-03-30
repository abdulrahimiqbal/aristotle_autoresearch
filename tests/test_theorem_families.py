import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.experiment_generator import materialize_candidate
from research_orchestrator.move_registry import MoveCandidate
from research_orchestrator.theorem_families import resolve_theorem_family_adapter


class TheoremFamilyAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="family_adapter_test_"))
        root = Path(__file__).resolve().parents[1]
        self.weighted_charter = load_charter(root / "examples" / "project_charter.json")
        self.weighted = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")
        self.erdos_charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.erdos = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_44_sidon_extension.json")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_current_family_resolves_through_adapter(self):
        adapter = resolve_theorem_family_adapter(self.weighted)
        self.assertEqual(adapter.family_id, "weighted_monotone")

        brief = materialize_candidate(
            charter=self.weighted_charter,
            conjecture=self.weighted,
            workspace_root=str(self.tempdir / "weighted"),
            experiments=[],
            candidate=MoveCandidate(
                move_family="invariant_mining",
                legacy_move="promote_lemma",
                parameters={"invariant_hint": "chain monotonicity"},
                objective="obj",
                expected_signal="sig",
                rationale="why",
            ),
        )
        text = Path(brief.lean_file).read_text(encoding="utf-8")
        self.assertEqual(brief.theorem_family_id, "weighted_monotone")
        self.assertIn("weighted-monotone family workspace", text)

    def test_second_family_uses_same_interface_with_different_materialization(self):
        adapter = resolve_theorem_family_adapter(self.erdos)
        self.assertEqual(adapter.family_id, "erdos_problem")

        brief = materialize_candidate(
            charter=self.erdos_charter,
            conjecture=self.erdos,
            workspace_root=str(self.tempdir / "erdos"),
            experiments=[],
            candidate=MoveCandidate(
                move_family="extremal_case",
                legacy_move="reformulate",
                parameters={"extremal_target": "maximal density boundary"},
                objective="obj",
                expected_signal="sig",
                rationale="why",
            ),
        )
        text = Path(brief.lean_file).read_text(encoding="utf-8")
        self.assertEqual(brief.theorem_family_id, "erdos_problem")
        self.assertIn("erdos family workspace", text)
        self.assertIn("extremal sweep", text)


if __name__ == "__main__":
    unittest.main()
