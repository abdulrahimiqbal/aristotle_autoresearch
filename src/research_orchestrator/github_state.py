from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from research_orchestrator.db import Database


# Key files to sync (minimal set for external inspection)
KEY_STATE_FILES = (
    "report.md",
    "campaign_summary.json",
    "experiments.csv",
)


@dataclass
class StateSyncResult:
    written_files: list[str] = field(default_factory=list)


def _decode_github_contents(payload: str) -> bytes:
    data = json.loads(payload)
    encoded = data.get("content", "")
    encoding = data.get("encoding", "")
    if encoding != "base64" or not isinstance(encoded, str):
        raise ValueError("GitHub contents payload did not include base64-encoded content.")
    normalized = encoded.replace("\n", "")
    return base64.b64decode(normalized)


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=path.name, suffix=".tmp", delete=False, dir=path.parent) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _github_download(
    *,
    repo: str,
    ref: str,
    state_dir: str | Path,
    filename: str,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]],
) -> bytes | None:
    state_root = Path(state_dir)
    api_path = f"repos/{repo}/contents/{state_root.as_posix()}/{filename}?ref={ref}"
    completed = runner(["gh", "api", api_path])
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        if "404" in stderr or "Not Found" in stderr:
            return None
        raise RuntimeError(f"Failed to download {filename} from GitHub: {stderr}")
    return _decode_github_contents(completed.stdout)


def publish_state_bundle(
    *,
    db: Database,
    project_id: str,
    state_dir: str | Path,
    report_path: str | Path | None = None,
    manager_snapshot_path: str | Path | None = None,
    include_sqlite_snapshot: bool = True,
) -> dict[str, str]:
    """Export key files for external inspection. Simplified from bundle system."""
    state_root = Path(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)

    written: dict[str, str] = {}

    # Export key readable state from DB
    db.export_readable_state(project_id, state_root)

    # Copy report if provided
    if report_path is not None and Path(report_path).exists():
        _atomic_write_bytes(state_root / "report.md", Path(report_path).read_bytes())
        written["report.md"] = str(state_root / "report.md")

    # Copy manager snapshot if provided
    if manager_snapshot_path is not None and Path(manager_snapshot_path).exists():
        _atomic_write_bytes(state_root / "report.manager_snapshot.json", Path(manager_snapshot_path).read_bytes())
        written["report.manager_snapshot.json"] = str(state_root / "report.manager_snapshot.json")

    # Optionally include SQLite snapshot
    if include_sqlite_snapshot:
        snapshot_path = state_root / "state.snapshot.sqlite"
        db.atomic_snapshot_to(snapshot_path)
        written["state.snapshot.sqlite"] = str(snapshot_path)

    return written


def sync_github_state(
    *,
    repo: str,
    ref: str,
    state_dir: str | Path,
    files: tuple[str, ...] = KEY_STATE_FILES,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> list[str]:
    """Sync key state files from GitHub. Simplified from bundle system."""
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
        payload = _github_download(repo=repo, ref=ref, state_dir=state_root, filename=filename, runner=run)
        if payload is None:
            continue
        destination = state_root / filename
        _atomic_write_bytes(destination, payload)
        written.append(str(destination))

    return written
