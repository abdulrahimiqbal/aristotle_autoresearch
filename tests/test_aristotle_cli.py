import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import os
import stat
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import run_one_cycle
from research_orchestrator.providers.aristotle_cli import _classify_failure, _extract_paths
from research_orchestrator.providers.aristotle_cli import AristotleCLIProvider
from research_orchestrator.reporter import build_report
from research_orchestrator.types import ProviderResult


class AristotleCLIProviderTest(unittest.TestCase):
    def test_connectivity_failure_is_classified_as_dns_failure(self):
        blocker_type, note = _classify_failure(
            "",
            "Failed to fetch expected toolchain from API: Request failed: [Errno 8] nodename nor servname provided, or not known",
        )
        self.assertEqual(blocker_type, "dns_failure")
        self.assertIn("dns", note.lower())

    def test_report_includes_artifacts(self):
        tempdir = Path(tempfile.mkdtemp(prefix="aristotle_report_test_"))
        try:
            db = Database(tempdir / "state.sqlite")
            db.initialize()
            root = Path(__file__).resolve().parents[1]
            charter = load_charter(root / "examples" / "project_charter.json")
            conjecture = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")
            db.save_project(charter)
            db.save_conjecture(conjecture)
            db.save_experiment_plan(
                {
                    "experiment_id": "e1",
                    "project_id": charter.project_id,
                    "conjecture_id": conjecture.conjecture_id,
                    "phase": "mapping",
                    "move": "underspecify",
                    "objective": "Expose dependencies.",
                    "expected_signal": "Generated lemmas.",
                    "modification": {"mode": "minimal_context"},
                    "workspace_dir": str(tempdir / "work"),
                    "lean_file": str(tempdir / "work" / "Main.lean"),
                }
            )
            db.complete_experiment(
                experiment_id="e1",
                provider="aristotle-cli",
                result=ProviderResult(
                    status="failed",
                    blocker_type="malformed",
                    notes="Connectivity failure.",
                    artifacts=[str(tempdir / "work" / "aristotle_stdout.txt")],
                ),
                evaluation={"total": 0.0},
            )
            report = build_report(db, charter.project_id)
            self.assertIn("artifacts", report)
            self.assertIn("aristotle_stdout.txt", report)
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)

    def test_extract_paths_resolves_relative_saved_artifact(self):
        tempdir = Path(tempfile.mkdtemp(prefix="aristotle_extract_test_"))
        try:
            artifact = tempdir / "job-output.tar.gz"
            artifact.write_text("ok", encoding="utf-8")
            paths = _extract_paths(
                "Project saved to job-output.tar.gz",
                base_dir=str(tempdir),
            )
            self.assertEqual(paths, [str(artifact.resolve())])
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)

    def test_shell_adapter_captures_stdout_stderr_and_report(self):
        tempdir = Path(tempfile.mkdtemp(prefix="aristotle_shell_test_"))
        try:
            db = Database(tempdir / "state.sqlite")
            db.initialize()
            root = Path(__file__).resolve().parents[1]
            charter = load_charter(root / "examples" / "project_charter.json")
            conjecture = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")
            db.save_project(charter)
            db.save_conjecture(conjecture)

            shim = tempdir / "fake_aristotle.sh"
            shim.write_text(
                "#!/bin/sh\n"
                "echo 'shim stdout: objective=$1'\n"
                "OUT=\"$PWD/lean_output/Main.lean\"\n"
                "echo \"shim stderr: artifact saved at $OUT\" 1>&2\n"
                "mkdir -p ./lean_output\n"
                "printf 'theorem demo : True := by\\n  trivial\\n' > \"$OUT\"\n",
                encoding="utf-8",
            )
            shim.chmod(shim.stat().st_mode | stat.S_IEXEC)

            provider = AristotleCLIProvider(command_template=[str(shim), "{objective}"])
            with patch.dict(os.environ, {"ARISTOTLE_API_KEY": "test-key"}, clear=False):
                with patch("research_orchestrator.orchestrator.get_provider", return_value=provider):
                    result = run_one_cycle(db, charter.project_id, "aristotle-cli", tempdir / "work")

            report = build_report(db, charter.project_id)
            experiment = db.get_experiment(result["brief"].experiment_id)

            self.assertEqual(result["result"].status, "succeeded")
            self.assertEqual(experiment["status"], "succeeded")
            self.assertIn("aristotle_stdout.txt", report)
            self.assertIn("aristotle_stderr.txt", report)
            self.assertIn("Main.lean", report)
            self.assertTrue(result["result"].artifacts)
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
