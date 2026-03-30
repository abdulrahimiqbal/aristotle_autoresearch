from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from research_orchestrator.lemma_utils import normalize_goal, normalize_lemma
from research_orchestrator.types import ArtifactProvenance, ProviderResult, VerificationSignal


THEOREM_PATTERN = re.compile(r"^\s*(?:theorem|lemma)\s+(.*)$", re.MULTILINE)
INTERMEDIATE_PATTERN = re.compile(r"^\s*(?:have|suffices)\s+([A-Za-z0-9_'.]+)?\s*:?\s*(.*)$", re.MULTILINE)
GOAL_PATTERN = re.compile(r"(?im)^(?:unsolved\s+goal|goal|required goal|need|show|prove)\s*:?\s*(.+)$")
BLOCKED_ON_PATTERN = re.compile(r"(?im)^(?:blocked on|requires|need|stuck on|waiting on)\s*:?\s*(.+)$")
MISSING_ASSUMPTION_PATTERN = re.compile(r"(?im)^(?:missing assumption|assumption needed|requires assumption)\s*:?\s*(.+)$")
COUNTEREXAMPLE_PATTERN = re.compile(r"(?im)^(?:counterexample|witness|minimal witness|smallest witness)\s*:?\s*(.+)$")
TRACE_PATTERN = re.compile(r"(?im)^(?:have|suffices|try|tactic|reduce to|it suffices to show)\s*:?\s*(.+)$")

PROVED_HINTS = ("proof complete", "all goals solved", "qed", "no goals remaining", "proved theorem")
DISPROVED_HINTS = ("counterexample", "falsified", "contradiction found", "disproved")
PARTIAL_HINTS = ("partial proof", "generated lemma", "reduced to lemma", "it suffices to show", "enough to prove")
AUTH_HINTS = ("invalid api key", "check your api key", "get a valid api key")
INFRA_HINTS = ("could not resolve host", "nodename nor servname provided", "connection refused", "network is unreachable")
PATH_HINTS = ("cli executable was not found on path", "permission denied", "not found on path")
TOOLCHAIN_HINTS = ("lean-toolchain", "no lean files", "toolchain")
TRACEBACK_HINTS = ("traceback", "exception:")
TIMEOUT_HINTS = ("timeout", "time budget", "resource exhausted", "search budget", "maximum recursion", "too many heartbeats")


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
    proof_trace_fragments: List[str]
    counterexample_witnesses: List[str]
    normalized_candidate_lemmas: List[str]
    normalized_unresolved_goals: List[str]
    new_signal_count: int
    reused_signal_count: int


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
    for declaration in THEOREM_PATTERN.findall(text):
        statement = declaration.strip()
        if ":=" in statement:
            statement = statement.split(":=", 1)[0].strip()
        if statement not in results:
            results.append(statement)
    for name, tail in INTERMEDIATE_PATTERN.findall(text):
        tail = tail.strip()
        if not tail:
            continue
        label = name.strip() if name else "anonymous_intermediate"
        statement = f"{label} : {tail}"
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


def _normalized_unique(values: Iterable[str], normalizer) -> tuple[list[str], list[str]]:
    raw: list[str] = []
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        normalized_value = normalizer(cleaned)
        if not normalized_value or normalized_value in seen:
            continue
        seen.add(normalized_value)
        raw.append(cleaned)
        normalized.append(normalized_value)
    return raw, normalized


def _signal_counts(
    normalized_candidate_lemmas: list[str],
    normalized_unresolved_goals: list[str],
    blocked_on: list[str],
    missing_assumptions: list[str],
    proof_trace_fragments: list[str],
    counterexample_witnesses: list[str],
) -> tuple[int, int]:
    signals = (
        [(item, "lemma") for item in normalized_candidate_lemmas]
        + [(item, "goal") for item in normalized_unresolved_goals]
        + [(item, "block") for item in blocked_on]
        + [(item, "assumption") for item in missing_assumptions]
        + [(item, "trace") for item in proof_trace_fragments]
        + [(item, "witness") for item in counterexample_witnesses]
    )
    unique = {(kind, value) for value, kind in ((v, k) for k, v in signals)}
    return len(unique), 0


def _classify_proof_outcome(result: ProviderResult, combined_text: str, candidate_lemmas: list[str], unresolved_goals: list[str], counterexample_witnesses: list[str]) -> str:
    lowered = combined_text.lower()
    if any(hint in lowered for hint in AUTH_HINTS):
        return "auth_failure"
    if any(hint in lowered for hint in INFRA_HINTS):
        return "infra_failure"
    if any(hint in lowered for hint in PATH_HINTS) or any(hint in lowered for hint in TOOLCHAIN_HINTS):
        return "malformed"
    if any(hint in lowered for hint in DISPROVED_HINTS) or counterexample_witnesses:
        return "disproved"
    if any(hint in lowered for hint in PROVED_HINTS):
        return "proved"
    if result.proved_lemmas:
        return "proved"
    if any(hint in lowered for hint in TIMEOUT_HINTS):
        return "stalled"
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
    if record.counterexample_witnesses:
        parts.append(f"witnesses={len(record.counterexample_witnesses)}")
    if record.proof_trace_fragments:
        parts.append(f"traces={len(record.proof_trace_fragments)}")
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
    proof_trace_fragments = _merge_unique(
        result.proof_trace_fragments,
        _extract_lines(TRACE_PATTERN, combined),
    )
    counterexample_witnesses = _merge_unique(
        result.counterexample_witnesses,
        _extract_lines(COUNTEREXAMPLE_PATTERN, combined),
    )

    proved_lemmas = _merge_unique(result.proved_lemmas)
    generated_lemmas = _merge_unique(result.generated_lemmas)
    candidate_lemmas = _merge_unique(
        result.candidate_lemmas,
        theorem_like,
    )
    candidate_lemmas, normalized_candidate_lemmas = _normalized_unique(candidate_lemmas, normalize_lemma)
    unresolved_goals, normalized_unresolved_goals = _normalized_unique(unresolved_goals, normalize_goal)
    proof_trace_fragments, _ = _normalized_unique(proof_trace_fragments, normalize_goal)
    counterexample_witnesses, _ = _normalized_unique(counterexample_witnesses, normalize_goal)
    blocked_on, _ = _normalized_unique(blocked_on, normalize_goal)
    missing_assumptions, _ = _normalized_unique(missing_assumptions, normalize_goal)
    proof_outcome = (
        result.proof_outcome
        if result.proof_outcome not in {"", "unknown"}
        else _classify_proof_outcome(result, combined, candidate_lemmas, unresolved_goals, counterexample_witnesses)
    )
    if proof_outcome in {"proved", "partial"} and candidate_lemmas and not (proved_lemmas or generated_lemmas):
        generated_lemmas = candidate_lemmas[:]
    new_signal_count, reused_signal_count = _signal_counts(
        normalized_candidate_lemmas,
        normalized_unresolved_goals,
        blocked_on,
        missing_assumptions,
        proof_trace_fragments,
        counterexample_witnesses,
    )

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
        proof_trace_fragments=proof_trace_fragments,
        counterexample_witnesses=counterexample_witnesses,
        normalized_candidate_lemmas=normalized_candidate_lemmas,
        normalized_unresolved_goals=normalized_unresolved_goals,
        new_signal_count=new_signal_count,
        reused_signal_count=reused_signal_count,
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
    enriched.proof_trace_fragments = record.proof_trace_fragments
    enriched.counterexample_witnesses = record.counterexample_witnesses
    enriched.normalized_candidate_lemmas = record.normalized_candidate_lemmas
    enriched.normalized_unresolved_goals = record.normalized_unresolved_goals
    enriched.new_signal_count = record.new_signal_count
    enriched.reused_signal_count = record.reused_signal_count
    enriched.status = _status_from_outcome(record.proof_outcome, result)
    metadata = dict(enriched.metadata)
    metadata["ingestion_record"] = asdict(record)
    if artifact_texts:
        metadata["artifact_text_sources"] = [path for path, _ in artifact_texts]
    enriched.metadata = metadata
    if not enriched.notes:
        enriched.notes = record.signal_summary
    return enriched


def build_verification_signals(
    *,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> list[VerificationSignal]:
    provenance = [
        ArtifactProvenance(
            kind="artifact",
            path=item["path"],
            source=item.get("kind", "file"),
            confidence=1.0,
        )
        for item in result.artifact_inventory[:3]
    ]
    fallback_provenance = provenance or [
        ArtifactProvenance(kind="stdout", path="", source="provider_result", confidence=0.55)
    ]
    signals: list[VerificationSignal] = []

    for lemma in result.proved_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="verified_lemma",
                label=lemma,
                detail="Lean/artifact-backed proved lemma extracted from provider result.",
                confidence=0.95,
                provenance=fallback_provenance,
            )
        )
    for lemma in result.candidate_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="reproducible_candidate_lemma" if provenance else "candidate_lemma",
                label=lemma,
                detail="Candidate lemma surfaced during verification-oriented result ingestion.",
                confidence=0.75 if provenance else 0.45,
                provenance=fallback_provenance,
            )
        )
    for goal in result.unresolved_goals:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="recurring_subgoal",
                label=goal,
                detail="Unresolved goal retained as a discovery object.",
                confidence=0.8 if provenance else 0.5,
                provenance=fallback_provenance,
            )
        )
    for assumption in result.missing_assumptions or result.suspected_missing_assumptions:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="assumption_boundary",
                label=assumption,
                detail=f"Potentially necessary assumption under outcome={result.proof_outcome}.",
                confidence=0.78 if provenance else 0.5,
                provenance=fallback_provenance,
            )
        )
    for witness in result.counterexample_witnesses:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="counterexample_witness",
                label=witness,
                detail="Candidate falsifying or fragility witness.",
                confidence=0.82 if provenance else 0.5,
                provenance=fallback_provenance,
            )
        )
    if result.blocker_type in {"formalization", "malformed", "dns_failure", "network_unavailable"}:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="infra_incident" if "failure" in result.proof_outcome else "formalization_blocker",
                label=result.blocker_type,
                detail=result.signal_summary or result.notes,
                confidence=0.9,
                provenance=fallback_provenance,
                metadata={"proof_outcome": result.proof_outcome},
            )
        )
    return signals
