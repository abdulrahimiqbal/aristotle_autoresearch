from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from research_orchestrator.db import Database


READABLE_STATE_FILES = (
    "report.md",
    "report.manager_snapshot.json",
    "campaign_summary.json",
    "conjecture_scoreboard.json",
    "recurring_structures.json",
    "active_queue.json",
    "experiments.csv",
    "incidents.json",
    "integrity.json",
)
OPTIONAL_SQLITE_FILES = (
    "state.snapshot.sqlite",
    "state.sqlite",
)
DEFAULT_STATE_FILES = READABLE_STATE_FILES


@dataclass
class StateSyncResult:
    written_files: list[str] = field(default_factory=list)
    authoritative_artifact: str = "readable_bundle"
    sqlite_status: str = "skipped"
    integrity_status: str = "unknown"


def _decode_github_contents(payload: str) -> bytes:
    data = json.loads(payload)
    encoded = data.get("content", "")
    encoding = data.get("encoding", "")
    if encoding != "base64" or not isinstance(encoded, str):
        raise ValueError("GitHub contents payload did not include base64-encoded content.")
    normalized = encoded.replace("\n", "")
    return base64.b64decode(normalized)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def _sqlite_integrity_ok(path: Path) -> bool:
    try:
        conn = sqlite3.connect(str(path), timeout=5.0)
        row = conn.execute("PRAGMA quick_check").fetchone()
        conn.close()
    except sqlite3.DatabaseError:
        return False
    return bool(row) and row[0] == "ok"


def publish_state_bundle(
    *,
    db: Database,
    project_id: str,
    state_dir: str | Path,
    report_path: str | Path | None = None,
    manager_snapshot_path: str | Path | None = None,
    include_sqlite_snapshot: bool = True,
) -> dict[str, str]:
    state_root = Path(state_dir)
    state_root.mkdir(parents=True, exist_ok=True)
    written = db.export_readable_state(project_id, state_root)
    if report_path is not None and Path(report_path).exists():
        _atomic_write_bytes(state_root / "report.md", Path(report_path).read_bytes())
        written["report.md"] = str(state_root / "report.md")
    if manager_snapshot_path is not None and Path(manager_snapshot_path).exists():
        _atomic_write_bytes(state_root / "report.manager_snapshot.json", Path(manager_snapshot_path).read_bytes())
        written["report.manager_snapshot.json"] = str(state_root / "report.manager_snapshot.json")
    integrity_payload = {
        "authoritative_artifact": "readable_bundle",
        "db_integrity": {
            "quick_check": db.quick_check(),
            "integrity_check": db.integrity_check(),
            "wal_checkpoint": db.checkpoint_wal(),
        },
        "files": {},
    }
    for filename in READABLE_STATE_FILES:
        path = state_root / filename
        if path.exists():
            integrity_payload["files"][filename] = {
                "sha256": _sha256_bytes(path.read_bytes()),
                "size_bytes": path.stat().st_size,
            }
    if include_sqlite_snapshot:
        snapshot_path = state_root / "state.snapshot.sqlite"
        db.atomic_snapshot_to(snapshot_path)
        written["state.snapshot.sqlite"] = str(snapshot_path)
        integrity_payload["files"]["state.snapshot.sqlite"] = {
            "sha256": _sha256_bytes(snapshot_path.read_bytes()),
            "size_bytes": snapshot_path.stat().st_size,
            "quick_check": "ok" if _sqlite_integrity_ok(snapshot_path) else "corrupt",
        }
    integrity_path = state_root / "integrity.json"
    _atomic_write_bytes(integrity_path, json.dumps(integrity_payload, indent=2).encode("utf-8"))
    written["integrity.json"] = str(integrity_path)
    return written


def sync_state_bundle(
    *,
    repo: str,
    ref: str,
    state_dir: str | Path,
    include_sqlite_snapshot: bool = False,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> StateSyncResult:
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
    result = StateSyncResult()
    integrity_payload: dict | None = None

    for filename in READABLE_STATE_FILES:
        payload = _github_download(repo=repo, ref=ref, state_dir=state_root, filename=filename, runner=run)
        if payload is None:
            continue
        destination = state_root / filename
        _atomic_write_bytes(destination, payload)
        result.written_files.append(str(destination))
        if filename == "integrity.json":
            integrity_payload = json.loads(payload.decode("utf-8"))

    result.integrity_status = "missing" if integrity_payload is None else "ok"
    if integrity_payload is not None:
        for filename, details in integrity_payload.get("files", {}).items():
            if filename not in READABLE_STATE_FILES:
                continue
            destination = state_root / filename
            if destination.exists() and _sha256_bytes(destination.read_bytes()) != details.get("sha256"):
                raise RuntimeError(f"Checksum mismatch for {filename}")

    if include_sqlite_snapshot:
        for filename in OPTIONAL_SQLITE_FILES:
            payload = _github_download(repo=repo, ref=ref, state_dir=state_root, filename=filename, runner=run)
            if payload is None:
                continue
            destination = state_root / filename
            _atomic_write_bytes(destination, payload)
            expected = (integrity_payload or {}).get("files", {}).get(filename, {}).get("sha256")
            if expected and _sha256_bytes(payload) != expected:
                destination.unlink(missing_ok=True)
                result.sqlite_status = "rejected_checksum"
                break
            if not _sqlite_integrity_ok(destination):
                destination.unlink(missing_ok=True)
                result.sqlite_status = "rejected_corrupt"
                break
            result.written_files.append(str(destination))
            result.sqlite_status = "accepted"
            break
    return result


def sync_github_state(
    *,
    repo: str,
    ref: str,
    state_dir: str | Path,
    files: tuple[str, ...] = DEFAULT_STATE_FILES,
    runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
) -> list[str]:
    if files == DEFAULT_STATE_FILES:
        return sync_state_bundle(repo=repo, ref=ref, state_dir=state_dir, include_sqlite_snapshot=False, runner=runner).written_files
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
