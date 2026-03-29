from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path
from typing import Callable


DEFAULT_STATE_FILES = (
    "state.sqlite",
    "report.md",
    "report.manager_snapshot.json",
)


def _decode_github_contents(payload: str) -> bytes:
    data = json.loads(payload)
    encoded = data.get("content", "")
    encoding = data.get("encoding", "")
    if encoding != "base64" or not isinstance(encoded, str):
        raise ValueError("GitHub contents payload did not include base64-encoded content.")
    normalized = encoded.replace("\n", "")
    return base64.b64decode(normalized)


def sync_github_state(
    *,
    repo: str,
    ref: str,
    state_dir: str | Path,
    files: tuple[str, ...] = DEFAULT_STATE_FILES,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> list[str]:
    state_root = Path(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    run = runner or (
        lambda command: subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    )

    written: list[str] = []
    for filename in files:
        api_path = f"repos/{repo}/contents/{state_root.as_posix()}/{filename}?ref={ref}"
        completed = run(["gh", "api", api_path])
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Failed to download {filename} from GitHub: {stderr}")
        destination = state_root / filename
        destination.write_bytes(_decode_github_contents(completed.stdout))
        written.append(str(destination))
    return written
