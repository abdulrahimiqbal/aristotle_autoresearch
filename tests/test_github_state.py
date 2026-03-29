import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import base64
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research_orchestrator.github_state import _decode_github_contents, sync_github_state


class GitHubStateTest(unittest.TestCase):
    def test_decode_github_contents(self):
        payload = json.dumps(
            {
                "encoding": "base64",
                "content": base64.b64encode(b"hello world").decode("ascii"),
            }
        )
        self.assertEqual(_decode_github_contents(payload), b"hello world")

    def test_sync_github_state_writes_canonical_files(self):
        tempdir = Path(tempfile.mkdtemp(prefix="github_state_test_"))
        try:
            responses = {
                "state.sqlite": b"sqlite-bytes",
                "report.md": b"# Report\n",
                "report.manager_snapshot.json": b'{"ok": true}\n',
            }

            def fake_runner(command):
                filename = command[-1].split("/")[-1].split("?")[0]
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
            self.assertEqual(len(written), 3)
            for filename, expected in responses.items():
                self.assertEqual((tempdir / "outputs" / "erdos_live_async" / filename).read_bytes(), expected)
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
