import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.dashboard_loader import DashboardLoader
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import manager_tick
from research_orchestrator.types import ProviderResult


class AsyncProviderStub:
    name = "aristotle-cli"
    supports_async = True

    def __init__(self):
        self.submissions = 0

    def submit(self, charter, conjecture, brief, worker_prompt):
        self.submissions += 1
        return ProviderResult(
            status="submitted",
            blocker_type="unknown",
            notes="submitted",
            external_id=f"job-{self.submissions}",
            external_status="QUEUED",
        )

    def poll(self, charter, conjecture, brief, worker_prompt, external_id, submitted_at=""):
        return ProviderResult(
            status="succeeded",
            blocker_type="unknown",
            notes="completed",
            external_id=external_id,
            external_status="COMPLETE",
            artifacts=[str(Path(brief.workspace_dir) / "result.lean")],
        )


class NonCompletingAsyncProviderStub(AsyncProviderStub):
    def poll(self, charter, conjecture, brief, worker_prompt, external_id, submitted_at=""):
        return ProviderResult(
            status="in_progress",
            blocker_type="unknown",
            notes="still running",
            external_id=external_id,
            external_status="IN_PROGRESS",
        )


class FailingAsyncProviderStub(AsyncProviderStub):
    def submit(self, charter, conjecture, brief, worker_prompt):
        return ProviderResult(
            status="failed",
            blocker_type="malformed",
            notes="ARISTOTLE_API_KEY is not set.",
        )


class ManagerTickTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="manager_tick_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.db.save_project(charter)
        for name in (
            "erdos_123_d_complete_sequences.json",
            "erdos_181_hypercube_ramsey.json",
            "erdos_44_sidon_extension.json",
        ):
            conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / name)
            self.db.save_conjecture(conjecture)
        self.project_id = charter.project_id
        self.report_path = self.tempdir / "report.md"
        self.snapshot_path = self.tempdir / "report.manager_snapshot.json"

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)
            os.environ.pop("RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND", None)

    def test_manager_tick_submits_up_to_capacity(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=5,
                max_submit_per_tick=5,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["jobs_submitted"], 3)
        self.assertTrue(self.report_path.exists())
        self.assertTrue(self.snapshot_path.exists())

    def test_manager_tick_with_five_active_jobs_submits_nothing(self):
        provider = NonCompletingAsyncProviderStub()
        now = datetime.now(timezone.utc).isoformat()
        for idx in range(5):
            self.db.save_experiment_plan(
                {
                    "experiment_id": f"seed-{idx}",
                    "project_id": self.project_id,
                    "conjecture_id": "erdos-123",
                    "phase": "mapping",
                    "move": "underspecify",
                    "objective": "seed active capacity",
                    "expected_signal": "seed",
                    "modification": {"mode": f"seed-{idx}"},
                    "workspace_dir": str(self.tempdir / f"seed_work_{idx}"),
                    "lean_file": str(self.tempdir / f"seed_work_{idx}" / "Main.lean"),
                    "external_id": f"seed-job-{idx}",
                    "external_status": "QUEUED",
                    "submitted_at": now,
                    "last_synced_at": now,
                }
            )
            self.db.update_experiment_result(
                experiment_id=f"seed-{idx}",
                provider="aristotle-cli",
                result=ProviderResult(
                    status="submitted",
                    blocker_type="unknown",
                    notes="seeded active run",
                    external_id=f"seed-job-{idx}",
                    external_status="QUEUED",
                ),
                evaluation=None,
            )
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=5,
                max_submit_per_tick=5,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["jobs_submitted"], 0)

    def test_completed_jobs_are_ingested(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=3,
                max_submit_per_tick=3,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=3,
                max_submit_per_tick=0,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["jobs_synced"], 3)
        completed = self.db.list_completed_experiments(self.project_id)
        self.assertEqual(len(completed), 3)

    def test_invalid_llm_output_falls_back(self):
        script = self.tempdir / "bad_manager.py"
        script.write_text("print('not json')\n", encoding="utf-8")
        os.environ["RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND"] = f"{sys.executable} {script}"
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=3,
                max_submit_per_tick=3,
                llm_manager_mode="on",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["policy_path"], "fallback")

    def test_duplicate_active_candidate_is_rejected_even_if_llm_recommends_it(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            first = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=1,
                max_submit_per_tick=1,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        active_experiment = self.db.list_active_experiments(self.project_id, provider="aristotle-cli")[0]
        script = self.tempdir / "choose_duplicate.py"
        script.write_text(
            "import json\n"
            f"print(json.dumps({{'ranked_experiment_ids': ['{active_experiment['experiment_id']}'], 'rationale': 'duplicate'}}))\n",
            encoding="utf-8",
        )
        os.environ["RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND"] = f"{sys.executable} {script}"
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work2",
                max_active=2,
                max_submit_per_tick=2,
                llm_manager_mode="on",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["policy_path"], "fallback")

    def test_cross_conjecture_diversity_is_preferred(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=3,
                max_submit_per_tick=3,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        conjecture_ids = {item["conjecture_id"] for item in result["submitted"]}
        self.assertEqual(len(conjecture_ids), 3)

    def test_async_submit_failure_is_not_counted_as_submission(self):
        provider = FailingAsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            result = manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=1,
                max_submit_per_tick=1,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )
        self.assertEqual(result["jobs_submitted"], 0)
        completed = self.db.list_completed_experiments(self.project_id)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]["blocker_type"], "malformed")

    def test_db_only_dashboard_exposes_manager_reasoning_after_tick(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            manager_tick(
                db=self.db,
                project_id=self.project_id,
                provider_name="aristotle-cli",
                workspace_root=self.tempdir / "work",
                max_active=3,
                max_submit_per_tick=3,
                llm_manager_mode="off",
                report_output=self.report_path,
                snapshot_output=self.snapshot_path,
            )

        state = DashboardLoader(state_dir=None, db_path=self.tempdir / "state.sqlite", project_id=self.project_id).load()
        self.assertTrue(state.manager_reasoning)
        self.assertEqual(state.manager_reasoning[0]["kind"], "manager_tick")
        self.assertIn("Fallback policy ranked candidates", state.manager_reasoning[0]["summary"])
        self.assertIn("Research Manager", state.manager_reasoning[0]["prompt"])


if __name__ == "__main__":
    unittest.main()
