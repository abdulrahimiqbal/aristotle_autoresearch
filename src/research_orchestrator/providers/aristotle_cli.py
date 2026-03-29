from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import List

from research_orchestrator.providers.base import Provider
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter, ProviderResult


_PATH_PATTERN = re.compile(r"(?P<path>(?:[A-Za-z]:)?(?:/|\.{1,2}/)[^\s'\"`<>]+)")
_RELATIVE_ARTIFACT_PATTERN = re.compile(r"(?P<path>[A-Za-z0-9._-]+\.(?:tar\.gz|tgz|zip|lean|olean|json|txt|log))")
_ARTIFACT_HINTS = ("artifact", "artifacts", "output", "result", "saved", "downloaded", "written", "destination")


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

    def __init__(self, command_template: List[str] | None = None):
        self.command_template = command_template or [
            "aristotle",
            "submit",
            "{objective}",
            "--project-dir",
            "{project_dir}",
            "--wait",
        ]

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
            completed = subprocess.run(
                command,
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return ProviderResult(
                status="failed",
                blocker_type="malformed",
                notes="The `aristotle` CLI executable was not found on PATH.",
                confidence=0.0,
            )

        artifacts = []
        stdout_path = Path(project_dir) / "aristotle_stdout.txt"
        stderr_path = Path(project_dir) / "aristotle_stderr.txt"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        artifacts.extend([str(stdout_path), str(stderr_path)])
        artifacts.extend(_extract_paths(completed.stdout, completed.stderr, base_dir=project_dir))

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
        )
