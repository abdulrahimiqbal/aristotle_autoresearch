import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import base64
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.github_state import _decode_github_contents, sync_github_state, sync_state_bundle


class GitHubStateTest(unittest.TestCase):
    def test_decode_github_contents(self):
        payload = json.dumps(
            {
                "encoding": "base64",
                "content": base64.b64encode(b"hello world").decode("ascii"),
            }
        )
        self.assertEqual(_decode_github_contents(payload), b"hello world")

    def test_sync_github_state_writes_readable_bundle_files(self):
        tempdir = Path(tempfile.mkdtemp(prefix="github_state_test_"))
        try:
            responses = {
                "report.md": b"# Report\n",
                "report.manager_snapshot.json": b'{"ok": true}\n',
                "campaign_summary.json": b'{"project_id": "p1"}\n',
                "conjecture_scoreboard.json": b"[]\n",
                "recurring_structures.json": b"[]\n",
                "active_queue.json": b"[]\n",
                "experiments.csv": b"experiment_id\n",
                "incidents.json": b"[]\n",
                "integrity.json": json.dumps(
                    {
                        "files": {
                            "report.md": {"sha256": __import__("hashlib").sha256(b"# Report\n").hexdigest()},
                            "report.manager_snapshot.json": {"sha256": __import__("hashlib").sha256(b'{"ok": true}\n').hexdigest()},
                            "campaign_summary.json": {"sha256": __import__("hashlib").sha256(b'{"project_id": "p1"}\n').hexdigest()},
                            "conjecture_scoreboard.json": {"sha256": __import__("hashlib").sha256(b"[]\n").hexdigest()},
                            "recurring_structures.json": {"sha256": __import__("hashlib").sha256(b"[]\n").hexdigest()},
                            "active_queue.json": {"sha256": __import__("hashlib").sha256(b"[]\n").hexdigest()},
                            "experiments.csv": {"sha256": __import__("hashlib").sha256(b"experiment_id\n").hexdigest()},
                            "incidents.json": {"sha256": __import__("hashlib").sha256(b"[]\n").hexdigest()},
                        }
                    }
                ).encode("utf-8"),
            }

            def fake_runner(command):
                filename = command[-1].split("/")[-1].split("?")[0]
                if filename not in responses:
                    class Missing:
                        returncode = 1
                        stdout = ""
                        stderr = "404 Not Found"

                    return Missing()
                payload = json.dumps(
                    {
                        "encoding": "base64",
                        "content": base64.b64encode(responses[filename]).decode("ascii"),
                    }
                )

                class Result:
                    returncode = 0
                    stdout = payload
                    stderr = ""

                return Result()

            written = sync_github_state(
                repo="example/repo",
                ref="campaign-state",
                state_dir=tempdir / "outputs" / "erdos_live_async",
                runner=fake_runner,
            )
            self.assertGreaterEqual(len(written), 8)
            for filename, expected in responses.items():
                self.assertEqual((tempdir / "outputs" / "erdos_live_async" / filename).read_bytes(), expected)
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)

    def test_sync_state_bundle_tolerates_corrupt_sqlite(self):
        tempdir = Path(tempfile.mkdtemp(prefix="github_state_corrupt_sqlite_test_"))
        try:
            readable_responses = {
                "report.md": b"# Report\n",
                "report.manager_snapshot.json": b'{"ok": true}\n',
                "campaign_summary.json": b'{"project_id": "p1"}\n',
                "conjecture_scoreboard.json": b"[]\n",
                "recurring_structures.json": b"[]\n",
                "active_queue.json": b"[]\n",
                "experiments.csv": b"experiment_id\n",
                "incidents.json": b"[]\n",
            }
            integrity = {
                "files": {
                    **{name: {"sha256": __import__("hashlib").sha256(payload).hexdigest()} for name, payload in readable_responses.items()},
                    "state.snapshot.sqlite": {"sha256": __import__("hashlib").sha256(b"not-a-real-sqlite").hexdigest()},
                }
            }
            responses = {
                **readable_responses,
                "integrity.json": json.dumps(integrity).encode("utf-8"),
                "state.snapshot.sqlite": b"not-a-real-sqlite",
            }

            def fake_runner(command):
                filename = command[-1].split("/")[-1].split("?")[0]
                if filename not in responses:
                    class Missing:
                        returncode = 1
                        stdout = ""
                        stderr = "404 Not Found"

                    return Missing()
                payload = json.dumps(
                    {
                        "encoding": "base64",
                        "content": base64.b64encode(responses[filename]).decode("ascii"),
                    }
                )

                class Result:
                    returncode = 0
                    stdout = payload
                    stderr = ""

                return Result()

            result = sync_state_bundle(
                repo="example/repo",
                ref="campaign-state",
                state_dir=tempdir / "outputs" / "erdos_live_async",
                include_sqlite_snapshot=True,
                runner=fake_runner,
            )
            self.assertEqual(result.sqlite_status, "rejected_corrupt")
            self.assertTrue((tempdir / "outputs" / "erdos_live_async" / "campaign_summary.json").exists())
            self.assertFalse((tempdir / "outputs" / "erdos_live_async" / "state.snapshot.sqlite").exists())
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
