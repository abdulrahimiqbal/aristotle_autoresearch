import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import unittest

from research_orchestrator.prompt_linter import lint_manager_prompt, lint_worker_prompt
from research_orchestrator.prompts import build_manager_prompt, build_worker_prompt
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter


class PromptContractTest(unittest.TestCase):
    def setUp(self):
        self.charter = ProjectCharter(
            project_id="p1",
            title="Test",
            overarching_problem="Map hidden dependencies.",
            success_criteria=["find recurring lemmas"],
            non_goals=["do not drift"],
            allowed_moves=["underspecify"],
            phase_order=["mapping"],
        )
        self.conjecture = Conjecture(
            conjecture_id="c1",
            project_id="p1",
            name="Conjecture",
            domain="combinatorics",
            natural_language="Test theorem.",
            lean_statement="theorem t : True := by\n  sorry\n",
            assumptions=["A1"],
        )
        self.brief = ExperimentBrief(
            experiment_id="e1",
            project_id="p1",
            conjecture_id="c1",
            phase="mapping",
            move="underspecify",
            objective="Expose dependencies.",
            expected_signal="Generated lemmas.",
            modification={"mode": "minimal_context"},
            workspace_dir=".",
            lean_file="./Main.lean",
        )

    def test_manager_prompt_lints(self):
        prompt = build_manager_prompt(self.charter, {"num_experiments": 0}, [{"move": "underspecify"}])
        result = lint_manager_prompt(prompt)
        self.assertTrue(result.ok, result.missing)

    def test_worker_prompt_lints(self):
        prompt = build_worker_prompt(self.charter, self.conjecture, self.brief, [], [])
        result = lint_worker_prompt(prompt)
        self.assertTrue(result.ok, result.missing)


if __name__ == "__main__":
    unittest.main()
