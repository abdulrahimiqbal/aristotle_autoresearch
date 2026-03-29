import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import submit_one_cycle, sync_provider_results
from research_orchestrator.types import ProviderResult


class AsyncProviderStub:
    name = "aristotle-cli"
    supports_async = True

    def submit(self, charter, conjecture, brief, worker_prompt):
        return ProviderResult(
            status="submitted",
            blocker_type="unknown",
            notes="submitted",
            external_id="job-123",
            external_status="QUEUED",
        )

    def poll(self, charter, conjecture, brief, worker_prompt, external_id):
        return ProviderResult(
            status="succeeded",
            blocker_type="unknown",
            notes="done",
            raw_stdout="Proof complete. All goals solved.",
            proved_lemmas=["async_demo_lemma : True"],
            external_id=external_id,
            external_status="COMPLETE",
            artifacts=[str(Path(brief.workspace_dir) / "result.lean")],
        )


class AsyncOrchestrationTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="async_orchestration_test_"))
        self.db = Database(self.tempdir / "state.sqlite")
        self.db.initialize()
        root = Path(__file__).resolve().parents[1]
        charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        conjecture = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_123_d_complete_sequences.json")
        self.db.save_project(charter)
        self.db.save_conjecture(conjecture)
        self.project_id = charter.project_id

    def tearDown(self):
        try:
            self.db.close()
        finally:
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_submit_then_sync_lifecycle(self):
        provider = AsyncProviderStub()
        with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
            submitted = submit_one_cycle(self.db, self.project_id, "aristotle-cli", self.tempdir / "work")
            self.assertEqual(submitted["result"].status, "submitted")
            experiment = self.db.get_experiment(submitted["brief"].experiment_id)
            self.assertEqual(experiment["status"], "submitted")
            self.assertEqual(experiment["external_id"], "job-123")

            synced = sync_provider_results(self.db, self.project_id, "aristotle-cli")
            self.assertEqual(len(synced), 1)
            final_experiment = self.db.get_experiment(submitted["brief"].experiment_id)
            self.assertEqual(final_experiment["status"], "succeeded")
            self.assertEqual(final_experiment["external_status"], "COMPLETE")


if __name__ == "__main__":
    unittest.main()
