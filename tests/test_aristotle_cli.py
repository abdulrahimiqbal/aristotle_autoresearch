import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import os
import stat
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import run_one_cycle
from research_orchestrator.providers.aristotle_cli import _classify_failure, _extract_paths
from research_orchestrator.providers.aristotle_cli import AristotleCLIProvider
from research_orchestrator.reporter import build_report
from research_orchestrator.types import ProviderResult


class AristotleCLIProviderTest(unittest.TestCase):
    def test_invalid_api_key_is_classified_as_malformed(self):
        blocker_type, note = _classify_failure(
            "",
            "ERROR - Invalid API key. Please check your API key and try again.",
        )
        self.assertEqual(blocker_type, "malformed")
        self.assertIn("api key", note.lower())

    def test_connectivity_failure_is_classified_as_dns_failure(self):
        blocker_type, note = _classify_failure(
            "",
            "Failed to fetch expected toolchain from API: Request failed: [Errno 8] nodename nor servname provided, or not known",
        )
        self.assertEqual(blocker_type, "dns_failure")
        self.assertIn("dns", note.lower())

    def test_result_destination_traceback_is_classified_as_malformed(self):
        blocker_type, note = _classify_failure(
            "",
            "Traceback (most recent call last):\nIsADirectoryError: [Errno 21] Is a directory: '/tmp/result'",
        )
        self.assertEqual(blocker_type, "malformed")
        self.assertIn("result retrieval", note.lower())

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
                "echo 'Proof complete. All goals solved.'\n"
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

    def test_poll_downloads_result_to_file_destination(self):
        tempdir = Path(tempfile.mkdtemp(prefix="aristotle_poll_test_"))
        try:
            root = Path(__file__).resolve().parents[1]
            charter = load_charter(root / "examples" / "project_charter.json")
            conjecture = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")
            provider = AristotleCLIProvider()
            brief = type(
                "Brief",
                (),
                {
                    "workspace_dir": str(tempdir),
                    "objective": "Test objective",
                    "experiment_id": "exp-1",
                },
            )()

            calls = []

            def fake_run(command, cwd):
                calls.append(command)
                if command[:3] == ["aristotle", "list", "--limit"]:
                    return CompletedProcess(
                        command,
                        0,
                        stdout="12345678-1234-1234-1234-123456789abc COMPLETE 100%\n",
                        stderr="",
                    )
                if command[:2] == ["aristotle", "result"]:
                    destination = Path(command[-1])
                    destination.write_text("theorem demo : True := by\n  trivial\n", encoding="utf-8")
                    return CompletedProcess(command, 0, stdout="Downloaded result.\n", stderr="")
                raise AssertionError(f"Unexpected command: {command}")

            with patch.object(provider, "_run_command", side_effect=fake_run):
                result = provider.poll(
                    charter=charter,
                    conjecture=conjecture,
                    brief=brief,
                    worker_prompt="",
                    external_id="12345678-1234-1234-1234-123456789abc",
                )

            self.assertEqual(result.status, "stalled")
            self.assertEqual(result.external_status, "COMPLETE")
            self.assertTrue(any(path.endswith(".bin") for path in result.artifacts))
            self.assertTrue(
                (tempdir / "aristotle_result_12345678-1234-1234-1234-123456789abc.bin").exists()
            )
            self.assertIn("--destination", calls[1])
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)

    def test_unsafe_archive_member_is_not_extracted(self):
        tempdir = Path(tempfile.mkdtemp(prefix="aristotle_archive_test_"))
        try:
            provider = AristotleCLIProvider()
            archive_path = tempdir / "payload.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape.txt", "bad")
            artifacts = provider._collect_result_artifacts(archive_path)
            self.assertEqual(artifacts, [str(archive_path)])
            self.assertFalse((tempdir / "escape.txt").exists())
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
