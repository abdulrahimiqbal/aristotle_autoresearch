from __future__ import annotations

import json
import os
import re
import subprocess
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from research_orchestrator.providers.base import Provider
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter, ProviderResult


_PATH_PATTERN = re.compile(r"(?P<path>(?:[A-Za-z]:)?(?:/|\.{1,2}/)[^\s'\"`<>]+)")
_RELATIVE_ARTIFACT_PATTERN = re.compile(r"(?P<path>[A-Za-z0-9._-]+\.(?:tar\.gz|tgz|zip|lean|olean|json|txt|log))")
_ARTIFACT_HINTS = ("artifact", "artifacts", "output", "result", "saved", "downloaded", "written", "destination")
_PROJECT_LINE_PATTERN = re.compile(
    r"^(?P<project_id>[0-9a-f-]{36})\s+(?P<status>[A-Z_]+)\s+",
    re.MULTILINE,
)
_PROJECT_ID_PATTERN = re.compile(r"(?P<project_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")


def _extract_paths(*chunks: str, base_dir: str | None = None) -> list[str]:
    seen: set[str] = set()
    paths: list[str] = []
    root = Path(base_dir).resolve() if base_dir else None

    def remember(path: Path) -> None:
        resolved = str(path.resolve())
        if resolved not in seen and path.exists():
            seen.add(resolved)
            paths.append(resolved)

    for chunk in chunks:
        for line in chunk.splitlines():
            lowered = line.lower()
            if not any(hint in lowered for hint in _ARTIFACT_HINTS):
                continue
            for match in _PATH_PATTERN.finditer(line):
                candidate = match.group("path").rstrip(".,:;)")
                if not candidate:
                    continue
                path = Path(candidate)
                if not path.is_absolute() and root is not None:
                    path = root / path
                remember(path)
            if root is None:
                continue
            for match in _RELATIVE_ARTIFACT_PATTERN.finditer(line):
                candidate = match.group("path").rstrip(".,:;)")
                if not candidate:
                    continue
                remember(root / candidate)
    return paths


def _classify_failure(stdout: str, stderr: str) -> tuple[str, str]:
    text = "\n".join(part for part in (stdout, stderr) if part).lower()
    if "isadirectoryerror" in text or "write_bytes" in text and "destination" in text:
        return (
            "malformed",
            "Aristotle completed remotely, but local result retrieval wrote to an invalid destination path. Use a file destination for `aristotle result` and retry sync.",
        )
    if "invalid api key" in text or "check your api key" in text or "get a valid api key" in text:
        return (
            "malformed",
            "Aristotle rejected the configured API key. Refresh ARISTOTLE_API_KEY and retry.",
        )
    if "nodename nor servname provided" in text or "could not resolve host" in text or "bio_lookup_ex" in text:
        return (
            "dns_failure",
            "Aristotle could not resolve `aristotle.harmonic.fun`. This is a DNS or sandbox name-resolution failure, not an API-key failure. Retry outside the sandbox or from a terminal/network that can resolve the host.",
        )
    if "connecterror" in text or "failed to fetch expected toolchain" in text or "timed out" in text or "connection refused" in text or "network is unreachable" in text:
        return (
            "network_unavailable",
            "Aristotle could not reach its API after starting the CLI request. This looks like an outbound connectivity issue, not an authentication issue. Check firewall, VPN, proxy, or sandbox network restrictions.",
        )
    if "lean-toolchain" in text or "toolchain" in text or "no lean files" in text:
        return (
            "malformed",
            "The workspace is missing the Lean toolchain metadata Aristotle expected.",
        )
    if "permission denied" in text or "not found" in text:
        return (
            "malformed",
            "The Aristotle CLI or one of its required files was not accessible from the workspace.",
        )
    if "traceback" in text or "api error" in text:
        return (
            "unknown",
            "Aristotle returned a Python traceback without a recognizable higher-level classification.",
        )
    return (
        "unknown",
        "Aristotle CLI command returned a non-zero exit code.",
    )


class AristotleCLIProvider(Provider):
    name = "aristotle-cli"
    supports_async = True
    GHOST_JOB_TIMEOUT_SECONDS = 2 * 3600
    STALE_PROGRESS_TIMEOUT_SECONDS = 6 * 3600
    SUBPROCESS_TIMEOUT_SECONDS = 20 * 60

    def __init__(self, command_template: List[str] | None = None):
        self.command_template = command_template or [
            "aristotle",
            "submit",
            "{objective}",
            "--project-dir",
            "{project_dir}",
            "--wait",
        ]
        self.submit_template = [
            "aristotle",
            "submit",
            "{objective}",
            "--project-dir",
            "{project_dir}",
        ]
        self.result_template = [
            "aristotle",
            "result",
            "{external_id}",
            "--destination",
            "{destination}",
        ]

    def _submission_age_seconds(self, submitted_at: str) -> float | None:
        if not submitted_at:
            return None
        try:
            parsed = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()

    def _run_command(self, command: List[str], cwd: str):
        return subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=self.SUBPROCESS_TIMEOUT_SECONDS,
        )

    def _safe_extract_zip(self, archive: zipfile.ZipFile, destination: Path) -> None:
        root = destination.resolve()
        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()
            if not str(member_path).startswith(str(root)):
                raise OSError(f"Unsafe zip member path: {member.filename}")
        archive.extractall(destination)

    def _safe_extract_tar(self, archive: tarfile.TarFile, destination: Path) -> None:
        root = destination.resolve()
        members = archive.getmembers()
        for member in members:
            member_path = (destination / member.name).resolve()
            if not str(member_path).startswith(str(root)):
                raise OSError(f"Unsafe tar member path: {member.name}")
        archive.extractall(destination, members=members)

    def _write_stream_artifacts(self, project_dir: str, prefix: str, stdout: str, stderr: str) -> List[str]:
        artifacts: List[str] = []
        stdout_path = Path(project_dir) / f"{prefix}_stdout.txt"
        stderr_path = Path(project_dir) / f"{prefix}_stderr.txt"
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        artifacts.extend([str(stdout_path), str(stderr_path)])
        artifacts.extend(_extract_paths(stdout, stderr, base_dir=project_dir))
        return artifacts

    def _extract_project_id(self, stdout: str, stderr: str) -> str:
        match = _PROJECT_ID_PATTERN.search("\n".join([stdout, stderr]))
        return match.group("project_id") if match else ""

    def _status_for_project(self, project_dir: str, external_id: str) -> tuple[str, str, str]:
        completed = self._run_command(
            ["aristotle", "list", "--limit", "100"],
            cwd=project_dir,
        )
        for match in _PROJECT_LINE_PATTERN.finditer(completed.stdout):
            if match.group("project_id") == external_id:
                return match.group("status"), completed.stdout, completed.stderr
        return "UNKNOWN", completed.stdout, completed.stderr

    def _result_destination(self, project_dir: str, external_id: str) -> Path:
        return Path(project_dir) / f"aristotle_result_{external_id}.bin"

    def _collect_result_artifacts(self, destination: Path) -> List[str]:
        artifacts: List[str] = []
        if not destination.exists():
            return artifacts
        artifacts.append(str(destination))

        extract_dir = destination.with_suffix(destination.suffix + ".contents")
        if extract_dir.exists():
            for path in extract_dir.rglob("*"):
                if path.is_file():
                    artifacts.append(str(path))
            return artifacts

        try:
            if zipfile.is_zipfile(destination):
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(destination) as archive:
                    self._safe_extract_zip(archive, extract_dir)
            elif tarfile.is_tarfile(destination):
                extract_dir.mkdir(parents=True, exist_ok=True)
                with tarfile.open(destination) as archive:
                    self._safe_extract_tar(archive, extract_dir)
        except (tarfile.TarError, OSError, zipfile.BadZipFile):
            return artifacts

        if extract_dir.exists():
            for path in extract_dir.rglob("*"):
                if path.is_file():
                    artifacts.append(str(path))
        return artifacts

    def submit(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        if not os.environ.get("ARISTOTLE_API_KEY"):
            return ProviderResult(
                status="failed",
                blocker_type="malformed",
                notes="ARISTOTLE_API_KEY is not set.",
                confidence=0.0,
            )

        project_dir = str(Path(brief.workspace_dir).resolve())
        command = [
            part.format(
                objective=brief.objective,
                project_dir=project_dir,
                experiment_id=brief.experiment_id,
            )
            for part in self.submit_template
        ]

        try:
            completed = self._run_command(command, cwd=project_dir)
        except FileNotFoundError:
            return ProviderResult(
                status="failed",
                blocker_type="malformed",
                notes="The `aristotle` CLI executable was not found on PATH.",
                confidence=0.0,
            )
        except subprocess.TimeoutExpired:
            return ProviderResult(
                status="failed",
                blocker_type="network_unavailable",
                notes="The `aristotle` CLI submission timed out locally before a structured result could be captured.",
                confidence=0.0,
            )

        artifacts = self._write_stream_artifacts(
            project_dir=project_dir,
            prefix="aristotle_submit",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

        if completed.returncode != 0:
            blocker_type, failure_note = _classify_failure(completed.stdout, completed.stderr)
            return ProviderResult(
                status="failed",
                blocker_type=blocker_type,
                notes=failure_note,
                confidence=0.2,
                raw_stdout=completed.stdout,
                raw_stderr=completed.stderr,
                artifacts=artifacts,
            )

        external_id = self._extract_project_id(completed.stdout, completed.stderr)
        if not external_id:
            return ProviderResult(
                status="failed",
                blocker_type="unknown",
                notes="Aristotle submission succeeded locally, but no remote project id was found in stdout/stderr.",
                confidence=0.2,
                raw_stdout=completed.stdout,
                raw_stderr=completed.stderr,
                artifacts=artifacts,
            )

        return ProviderResult(
            status="submitted",
            blocker_type="unknown",
            notes="Submitted Aristotle job without waiting for completion.",
            confidence=0.6,
            raw_stdout=completed.stdout,
            raw_stderr=completed.stderr,
            artifacts=artifacts,
            external_id=external_id,
            external_status="QUEUED",
        )

    def poll(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
        external_id: str,
        submitted_at: str = "",
    ) -> ProviderResult:
        project_dir = str(Path(brief.workspace_dir).resolve())
        age_seconds = self._submission_age_seconds(submitted_at)
        status, list_stdout, list_stderr = self._status_for_project(project_dir, external_id)
        list_artifacts = self._write_stream_artifacts(
            project_dir=project_dir,
            prefix="aristotle_list",
            stdout=list_stdout,
            stderr=list_stderr,
        )
        if status == "UNKNOWN":
            if age_seconds is not None and age_seconds > self.GHOST_JOB_TIMEOUT_SECONDS:
                note = (
                    f"Aristotle job {external_id} has disappeared from the remote listing. "
                    "It may have been garbage-collected, cancelled externally, or completed without being captured. "
                    "Marking as failed for campaign recovery."
                )
                return ProviderResult(
                    status="failed",
                    blocker_type="unknown",
                    notes=note,
                    confidence=0.35,
                    raw_stdout=list_stdout,
                    raw_stderr=list_stderr,
                    artifacts=list_artifacts,
                    external_id=external_id,
                    external_status=status,
                    metadata={
                        "incident_type": "ghost_job",
                        "incident_detail": note,
                        "incident_severity": "warning",
                    },
                )
            return ProviderResult(
                status="submitted",
                blocker_type="unknown",
                notes=(
                    f"Aristotle job {external_id} was not present in the remote listing yet. "
                    "Keeping it active until the ghost timeout elapses."
                ),
                confidence=0.35,
                raw_stdout=list_stdout,
                raw_stderr=list_stderr,
                artifacts=list_artifacts,
                external_id=external_id,
                external_status=status,
            )
        if status in {"NOT_STARTED", "QUEUED", "PENDING_RETRY"}:
            return ProviderResult(
                status="submitted",
                blocker_type="unknown",
                notes=f"Aristotle job {external_id} is still queued.",
                confidence=0.5,
                raw_stdout=list_stdout,
                raw_stderr=list_stderr,
                artifacts=list_artifacts,
                external_id=external_id,
                external_status=status,
            )
        if status == "IN_PROGRESS":
            if age_seconds is not None and age_seconds > self.STALE_PROGRESS_TIMEOUT_SECONDS:
                note = (
                    f"Aristotle job {external_id} has been IN_PROGRESS for over 6 hours. "
                    "Marking as stalled to free campaign capacity. The backfill mechanism can retry result retrieval later."
                )
                return ProviderResult(
                    status="stalled",
                    blocker_type="unknown",
                    notes=note,
                    confidence=0.4,
                    raw_stdout=list_stdout,
                    raw_stderr=list_stderr,
                    artifacts=list_artifacts,
                    external_id=external_id,
                    external_status=status,
                    metadata={
                        "incident_type": "stale_active_timeout",
                        "incident_detail": note,
                        "incident_severity": "warning",
                    },
                )
            return ProviderResult(
                status="in_progress",
                blocker_type="unknown",
                notes=f"Aristotle job {external_id} is still in progress.",
                confidence=0.55,
                raw_stdout=list_stdout,
                raw_stderr=list_stderr,
                artifacts=list_artifacts,
                external_id=external_id,
                external_status=status,
            )
        if status in {"FAILED", "OUT_OF_BUDGET", "CANCELED"}:
            return ProviderResult(
                status="failed",
                blocker_type="unknown",
                notes=f"Aristotle job {external_id} finished with remote status {status}.",
                confidence=0.25,
                raw_stdout=list_stdout,
                raw_stderr=list_stderr,
                artifacts=list_artifacts,
                external_id=external_id,
                external_status=status,
            )

        destination = self._result_destination(project_dir, external_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = [
            part.format(external_id=external_id, destination=str(destination))
            for part in self.result_template
        ]
        completed = self._run_command(command, cwd=project_dir)
        artifacts = list_artifacts + self._write_stream_artifacts(
            project_dir=project_dir,
            prefix="aristotle_result",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        artifacts.extend(self._collect_result_artifacts(destination))

        if completed.returncode != 0:
            blocker_type, failure_note = _classify_failure(completed.stdout, completed.stderr)
            return ProviderResult(
                status="failed",
                blocker_type=blocker_type,
                notes=failure_note,
                confidence=0.2,
                raw_stdout=completed.stdout,
                raw_stderr=completed.stderr,
                artifacts=artifacts,
                external_id=external_id,
                external_status=status,
            )

        final_status = "stalled"
        notes = (
            "Aristotle result downloaded successfully."
            if status == "COMPLETE"
            else f"Aristotle finished with remote status {status}; downloaded whatever artifacts were available."
        )
        return ProviderResult(
            status=final_status,
            blocker_type="unknown",
            notes=notes + " Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.",
            confidence=0.7 if status == "COMPLETE" else 0.45,
            raw_stdout=completed.stdout,
            raw_stderr=completed.stderr,
            artifacts=artifacts,
            external_id=external_id,
            external_status=status,
        )

    def run(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        if not os.environ.get("ARISTOTLE_API_KEY"):
            return ProviderResult(
                status="failed",
                blocker_type="malformed",
                notes="ARISTOTLE_API_KEY is not set.",
                confidence=0.0,
            )

        project_dir = str(Path(brief.workspace_dir).resolve())
        command = [
            part.format(
                objective=brief.objective,
                project_dir=project_dir,
                experiment_id=brief.experiment_id,
            )
            for part in self.command_template
        ]

        try:
            completed = self._run_command(command, cwd=project_dir)
        except FileNotFoundError:
            return ProviderResult(
                status="failed",
                blocker_type="malformed",
                notes="The `aristotle` CLI executable was not found on PATH.",
                confidence=0.0,
            )
        except subprocess.TimeoutExpired:
            return ProviderResult(
                status="failed",
                blocker_type="network_unavailable",
                notes="The `aristotle` CLI command timed out locally before a structured result could be captured.",
                confidence=0.0,
            )

        artifacts = self._write_stream_artifacts(
            project_dir=project_dir,
            prefix="aristotle",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

        if completed.returncode == 0:
            notes = "Aristotle CLI command completed successfully."
            if len(artifacts) > 2:
                notes += " Captured generated artifacts: " + ", ".join(artifacts[2:])
            # Conservative classification: live adapter is successful at the CLI layer,
            # but result parsing is intentionally cautious until customized by the user.
            return ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                generated_lemmas=[],
                proved_lemmas=[],
                unresolved_goals=[],
                suspected_missing_assumptions=[],
                notes=notes
                + " Customize result ingestion to extract generated Lean artifacts and intermediate lemmas.",
                confidence=0.65,
                raw_stdout=completed.stdout,
                raw_stderr=completed.stderr,
                artifacts=artifacts,
                external_status="COMPLETE",
            )

        blocker_type, failure_note = _classify_failure(completed.stdout, completed.stderr)
        notes = failure_note
        if len(artifacts) > 2:
            notes += " Captured generated artifacts: " + ", ".join(artifacts[2:])
        return ProviderResult(
            status="failed",
            blocker_type=blocker_type,
            generated_lemmas=[],
            proved_lemmas=[],
            unresolved_goals=[],
            suspected_missing_assumptions=[],
            notes=notes,
            confidence=0.2,
            raw_stdout=completed.stdout,
            raw_stderr=completed.stderr,
            artifacts=artifacts,
            external_status="FAILED",
        )
