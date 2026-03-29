from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

from research_orchestrator.types import ProviderResult


THEOREM_PATTERN = re.compile(r"^\s*(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)\s*:(.*)$", re.MULTILINE)
GOAL_PATTERN = re.compile(r"(?im)^(?:unsolved\s+goal|goal|required goal|need)\s*:?\s*(.+)$")
BLOCKED_ON_PATTERN = re.compile(r"(?im)^(?:blocked on|requires|need)\s*:?\s*(.+)$")
MISSING_ASSUMPTION_PATTERN = re.compile(r"(?im)^(?:missing assumption|assumption needed|requires assumption)\s*:?\s*(.+)$")

PROVED_HINTS = ("proof complete", "all goals solved", "qed", "no goals remaining", "proved theorem")
DISPROVED_HINTS = ("counterexample", "falsified", "contradiction found", "disproved")
PARTIAL_HINTS = ("partial proof", "generated lemma", "reduced to lemma", "it suffices to show", "enough to prove")
AUTH_HINTS = ("invalid api key", "check your api key", "get a valid api key")
INFRA_HINTS = ("could not resolve host", "nodename nor servname provided", "connection refused", "network is unreachable")
PATH_HINTS = ("cli executable was not found on path", "permission denied", "not found on path")
TOOLCHAIN_HINTS = ("lean-toolchain", "no lean files", "toolchain")
TRACEBACK_HINTS = ("traceback", "exception:")


@dataclass
class IngestionRecord:
    proof_outcome: str
    signal_summary: str
    generated_lemmas: List[str]
    proved_lemmas: List[str]
    candidate_lemmas: List[str]
    unresolved_goals: List[str]
    blocked_on: List[str]
    missing_assumptions: List[str]
    artifact_inventory: List[Dict[str, Any]]


def _read_text_artifacts(paths: Iterable[str]) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists() or path.is_dir():
            continue
        if path.suffix.lower() not in {".txt", ".log", ".json", ".lean"}:
            continue
        try:
            chunks.append((str(path), path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return chunks


def _artifact_inventory(paths: Iterable[str]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
        for candidate in ([path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]):
            resolved = str(candidate.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            inventory.append(
                {
                    "path": resolved,
                    "kind": candidate.suffix.lower().lstrip(".") or "file",
                    "size_bytes": candidate.stat().st_size,
                }
            )
    return sorted(inventory, key=lambda item: item["path"])


def _extract_theorem_like_statements(text: str) -> list[str]:
    results: list[str] = []
    for name, tail in THEOREM_PATTERN.findall(text):
        statement = f"{name} : {tail.strip()}"
        if statement not in results:
            results.append(statement)
    return results


def _extract_lines(pattern: re.Pattern[str], text: str) -> list[str]:
    lines: list[str] = []
    for match in pattern.findall(text):
        value = match.strip()
        if value and value not in lines:
            lines.append(value)
    return lines


def _merge_unique(*groups: Iterable[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if not item or item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return merged


def _classify_proof_outcome(result: ProviderResult, combined_text: str, candidate_lemmas: list[str], unresolved_goals: list[str]) -> str:
    lowered = combined_text.lower()
    if any(hint in lowered for hint in AUTH_HINTS):
        return "auth_failure"
    if any(hint in lowered for hint in INFRA_HINTS):
        return "infra_failure"
    if any(hint in lowered for hint in PATH_HINTS) or any(hint in lowered for hint in TOOLCHAIN_HINTS):
        return "malformed"
    if any(hint in lowered for hint in DISPROVED_HINTS):
        return "disproved"
    if any(hint in lowered for hint in PROVED_HINTS):
        return "proved"
    if result.proved_lemmas:
        return "proved"
    if any(hint in lowered for hint in PARTIAL_HINTS):
        return "partial"
    if candidate_lemmas or unresolved_goals or result.generated_lemmas:
        return "partial"
    if any(hint in lowered for hint in TRACEBACK_HINTS):
        return "unknown"
    if result.status == "stalled":
        return "stalled"
    if result.status == "failed":
        return "unknown"
    if result.status == "succeeded":
        return "stalled"
    return "unknown"


def _summary_for(record: IngestionRecord, remote_status: str, blocker_type: str) -> str:
    parts = [f"remote_status={remote_status or 'n/a'}", f"proof_outcome={record.proof_outcome}", f"blocker={blocker_type}"]
    if record.proved_lemmas:
        parts.append(f"proved={len(record.proved_lemmas)}")
    if record.generated_lemmas:
        parts.append(f"generated={len(record.generated_lemmas)}")
    if record.candidate_lemmas:
        parts.append(f"candidates={len(record.candidate_lemmas)}")
    if record.unresolved_goals:
        parts.append(f"subgoals={len(record.unresolved_goals)}")
    return "; ".join(parts)


def _status_from_outcome(proof_outcome: str, result: ProviderResult) -> str:
    if result.status in {"submitted", "in_progress"}:
        return result.status
    if proof_outcome == "proved":
        return "succeeded"
    if proof_outcome in {"disproved", "infra_failure", "auth_failure", "malformed"}:
        return "failed"
    if proof_outcome in {"partial", "stalled", "unknown"}:
        return "stalled"
    return result.status


def ingest_provider_result(result: ProviderResult) -> ProviderResult:
    text_chunks = [result.raw_stdout, result.raw_stderr, result.notes]
    artifact_texts = _read_text_artifacts(result.artifacts)
    text_chunks.extend(text for _, text in artifact_texts)
    combined = "\n".join(chunk for chunk in text_chunks if chunk)

    artifact_inventory = _artifact_inventory(result.artifacts)
    theorem_like = _merge_unique(*(_extract_theorem_like_statements(text) for _, text in artifact_texts))
    unresolved_goals = _merge_unique(
        result.unresolved_goals,
        _extract_lines(GOAL_PATTERN, combined),
    )
    blocked_on = _merge_unique(
        _extract_lines(BLOCKED_ON_PATTERN, combined),
        result.blocked_on,
    )
    missing_assumptions = _merge_unique(
        result.missing_assumptions,
        result.suspected_missing_assumptions,
        _extract_lines(MISSING_ASSUMPTION_PATTERN, combined),
    )

    proved_lemmas = _merge_unique(result.proved_lemmas)
    generated_lemmas = _merge_unique(result.generated_lemmas)
    candidate_lemmas = _merge_unique(
        result.candidate_lemmas,
        theorem_like,
    )
    proof_outcome = (
        result.proof_outcome
        if result.proof_outcome not in {"", "unknown"}
        else _classify_proof_outcome(result, combined, candidate_lemmas, unresolved_goals)
    )
    if proof_outcome in {"proved", "partial"} and candidate_lemmas and not (proved_lemmas or generated_lemmas):
        generated_lemmas = candidate_lemmas[:]

    record = IngestionRecord(
        proof_outcome=proof_outcome,
        signal_summary="",
        generated_lemmas=generated_lemmas,
        proved_lemmas=proved_lemmas,
        candidate_lemmas=candidate_lemmas,
        unresolved_goals=unresolved_goals,
        blocked_on=blocked_on,
        missing_assumptions=missing_assumptions,
        artifact_inventory=artifact_inventory,
    )
    record.signal_summary = _summary_for(record, result.external_status, result.blocker_type)

    enriched = ProviderResult(**asdict(result))
    enriched.proof_outcome = record.proof_outcome
    enriched.signal_summary = record.signal_summary
    enriched.generated_lemmas = record.generated_lemmas
    enriched.proved_lemmas = record.proved_lemmas
    enriched.candidate_lemmas = record.candidate_lemmas
    enriched.unresolved_goals = record.unresolved_goals
    enriched.blocked_on = record.blocked_on
    enriched.missing_assumptions = record.missing_assumptions
    enriched.suspected_missing_assumptions = record.missing_assumptions[:]
    enriched.artifact_inventory = record.artifact_inventory
    enriched.status = _status_from_outcome(record.proof_outcome, result)
    metadata = dict(enriched.metadata)
    metadata["ingestion_record"] = asdict(record)
    if artifact_texts:
        metadata["artifact_text_sources"] = [path for path, _ in artifact_texts]
    enriched.metadata = metadata
    if not enriched.notes:
        enriched.notes = record.signal_summary
    return enriched
