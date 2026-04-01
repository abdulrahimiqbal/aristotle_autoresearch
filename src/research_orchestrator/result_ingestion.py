from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from uuid import uuid4

from research_orchestrator.schema_versions import EVALUATOR_VERSION, SEMANTIC_MEMORY_VERSION, VERIFICATION_PARSER_VERSION, VERIFICATION_SCHEMA_VERSION
from research_orchestrator.semantic_memory import canonicalize_record
from research_orchestrator.types import (
    ArtifactProvenance,
    PreparedIngestion,
    ProviderMetadata,
    ProviderResult,
    SemanticMemorySummary,
    TheoremStatus,
    ValidationSeverity,
    VerificationArtifactKind,
    VerificationObservation,
    VerificationRecord,
    VerificationSchemaVersion,
    VerificationSignal,
    VerificationStatus,
    VerificationValidationIssue,
    VerificationRunMetadata,
)


THEOREM_PATTERN = re.compile(r"^\s*(?:theorem|lemma)\s+(.*)$", re.MULTILINE)
INTERMEDIATE_PATTERN = re.compile(r"^\s*(?:have|suffices)\s+([A-Za-z0-9_'.]+)?\s*:?\s*(.*)$", re.MULTILINE)
GOAL_PATTERN = re.compile(r"(?im)^(?:unsolved\s+goal|goal|required goal|need|show|prove)\s*:?\s*(.+)$")
BLOCKED_ON_PATTERN = re.compile(r"(?im)^(?:blocked on|requires|need|stuck on|waiting on)\s*:?\s*(.+)$")
MISSING_ASSUMPTION_PATTERN = re.compile(r"(?im)^(?:missing assumption|assumption needed|requires assumption)\s*:?\s*(.+)$")
COUNTEREXAMPLE_PATTERN = re.compile(r"(?im)^(?:counterexample|witness|minimal witness|smallest witness)\s*:?\s*(.+)$")
TRACE_PATTERN = re.compile(r"(?im)^(?:have|suffices|try|tactic|reduce to|it suffices to show)\s*:?\s*(.+)$")
GENERATED_LEMMA_PATTERN = re.compile(r"(?im)^(?:generated lemma|lemma candidate|candidate lemma)\s*:?\s*(.+)$")

PROVED_HINTS = ("proof complete", "all goals solved", "qed", "no goals remaining", "proved theorem")
DISPROVED_HINTS = ("counterexample", "falsified", "contradiction found", "disproved")
PARTIAL_HINTS = ("partial proof", "generated lemma", "reduced to lemma", "it suffices to show", "enough to prove")
AUTH_HINTS = ("invalid api key", "check your api key", "get a valid api key")
INFRA_HINTS = ("could not resolve host", "nodename nor servname provided", "connection refused", "network is unreachable")
PATH_HINTS = ("cli executable was not found on path", "permission denied", "not found on path")
TOOLCHAIN_HINTS = ("lean-toolchain", "no lean files", "toolchain")
TRACEBACK_HINTS = ("traceback", "exception:")
TIMEOUT_HINTS = ("timeout", "time budget", "resource exhausted", "search budget", "maximum recursion", "too many heartbeats")


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
        candidates = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
        for candidate in candidates:
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
            cleaned = item.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            merged.append(cleaned)
    return merged


def _obs(values: Iterable[str], artifact_kind: str, provenance: list[ArtifactProvenance]) -> list[VerificationObservation]:
    observations: list[VerificationObservation] = []
    seen: set[str] = set()
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        observations.append(
            VerificationObservation(
                text=cleaned,
                artifact_kind=artifact_kind,
                confidence=0.7 if provenance else 0.5,
                provenance=provenance[:],
            )
        )
    return observations


def _classify_proof_outcome(
    result: ProviderResult,
    combined_text: str,
    candidate_lemmas: list[str],
    unresolved_goals: list[str],
    counterexample_witnesses: list[str],
) -> str:
    lowered = combined_text.lower()
    has_partial_signal = bool(
        any(hint in lowered for hint in PARTIAL_HINTS)
        or candidate_lemmas
        or unresolved_goals
        or result.generated_lemmas
    )
    if any(hint in lowered for hint in AUTH_HINTS):
        return VerificationStatus.AUTH_FAILURE.value
    if any(hint in lowered for hint in INFRA_HINTS):
        return VerificationStatus.INFRA_FAILURE.value
    if any(hint in lowered for hint in PATH_HINTS) or any(hint in lowered for hint in TOOLCHAIN_HINTS):
        return VerificationStatus.MALFORMED.value
    if any(hint in lowered for hint in DISPROVED_HINTS if hint != "counterexample"):
        return VerificationStatus.DISPROVED.value
    if counterexample_witnesses or "counterexample" in lowered:
        if result.status == "failed" or not has_partial_signal:
            return VerificationStatus.DISPROVED.value
    if any(hint in lowered for hint in PROVED_HINTS):
        return VerificationStatus.PROVED.value
    if result.proved_lemmas:
        return VerificationStatus.PROVED.value
    if any(hint in lowered for hint in TIMEOUT_HINTS):
        return VerificationStatus.STALLED.value
    if any(hint in lowered for hint in PARTIAL_HINTS):
        return VerificationStatus.PARTIAL.value
    if candidate_lemmas or unresolved_goals or result.generated_lemmas:
        return VerificationStatus.PARTIAL.value
    if any(hint in lowered for hint in TRACEBACK_HINTS):
        return VerificationStatus.UNKNOWN.value
    if result.status == "stalled":
        return VerificationStatus.STALLED.value
    if result.status == "failed":
        return VerificationStatus.UNKNOWN.value
    if result.status == "succeeded":
        return VerificationStatus.STALLED.value
    return VerificationStatus.UNKNOWN.value


def _theorem_status_for(verification_status: str) -> str:
    if verification_status == VerificationStatus.PROVED.value:
        return TheoremStatus.VERIFIED.value
    if verification_status == VerificationStatus.PARTIAL.value:
        return TheoremStatus.PARTIALLY_VERIFIED.value
    if verification_status == VerificationStatus.DISPROVED.value:
        return TheoremStatus.REFUTED.value
    if verification_status == VerificationStatus.MALFORMED.value:
        return TheoremStatus.INVALID.value
    return TheoremStatus.UNRESOLVED.value


def _status_from_outcome(proof_outcome: str, result: ProviderResult) -> str:
    if result.status in {"submitted", "in_progress"}:
        return result.status
    if proof_outcome == VerificationStatus.PROVED.value:
        return "succeeded"
    if proof_outcome in {
        VerificationStatus.DISPROVED.value,
        VerificationStatus.INFRA_FAILURE.value,
        VerificationStatus.AUTH_FAILURE.value,
        VerificationStatus.MALFORMED.value,
    }:
        return "failed"
    if proof_outcome in {VerificationStatus.PARTIAL.value, VerificationStatus.STALLED.value, VerificationStatus.UNKNOWN.value}:
        return "stalled"
    return result.status


def _summary_for(result: ProviderResult, record: VerificationRecord, semantic_summary: SemanticMemorySummary) -> str:
    parts = [
        f"remote_status={result.external_status or 'n/a'}",
        f"verification_status={record.verification_status}",
        f"theorem_status={record.theorem_status}",
        f"blocker={result.blocker_type}",
    ]
    if record.proved_lemmas:
        parts.append(f"proved={len(record.proved_lemmas)}")
    if record.generated_lemmas:
        parts.append(f"generated={len(record.generated_lemmas)}")
    if record.unsolved_goals:
        parts.append(f"subgoals={len(record.unsolved_goals)}")
    if record.counterexamples:
        parts.append(f"witnesses={len(record.counterexamples)}")
    if semantic_summary.new_exact_count or semantic_summary.canonical_reuse_count:
        parts.append(f"semantic=new:{semantic_summary.new_exact_count}/reuse:{semantic_summary.canonical_reuse_count}")
    return "; ".join(parts)


def collect_result_artifacts(result: ProviderResult) -> Tuple[list[dict[str, Any]], list[tuple[str, str]], str]:
    text_chunks = [result.raw_stdout, result.raw_stderr, result.notes]
    artifact_texts = _read_text_artifacts(result.artifacts)
    text_chunks.extend(text for _, text in artifact_texts)
    return _artifact_inventory(result.artifacts), artifact_texts, "\n".join(chunk for chunk in text_chunks if chunk)


def parse_provider_result(result: ProviderResult) -> VerificationRecord:
    artifact_inventory, artifact_texts, combined = collect_result_artifacts(result)
    provenance = [
        ArtifactProvenance(kind="artifact", path=item["path"], source=item.get("kind", "file"), confidence=1.0)
        for item in artifact_inventory[:5]
    ]

    theorem_like = _merge_unique(*(_extract_theorem_like_statements(text) for _, text in artifact_texts))
    unresolved_goals = _merge_unique(result.unresolved_goals, _extract_lines(GOAL_PATTERN, combined))
    blocked_on = _merge_unique(_extract_lines(BLOCKED_ON_PATTERN, combined), result.blocked_on)
    missing_assumptions = _merge_unique(result.missing_assumptions, result.suspected_missing_assumptions, _extract_lines(MISSING_ASSUMPTION_PATTERN, combined))
    proof_trace_fragments = _merge_unique(result.proof_trace_fragments, _extract_lines(TRACE_PATTERN, combined))
    counterexample_witnesses = _merge_unique(result.counterexample_witnesses, _extract_lines(COUNTEREXAMPLE_PATTERN, combined))
    proved_lemmas = _merge_unique(result.proved_lemmas)
    generated_lemmas = _merge_unique(result.generated_lemmas, _extract_lines(GENERATED_LEMMA_PATTERN, combined))
    candidate_lemmas = _merge_unique(result.candidate_lemmas, theorem_like)

    verification_status = (
        result.proof_outcome
        if result.proof_outcome not in {"", VerificationStatus.UNKNOWN.value}
        else _classify_proof_outcome(result, combined, candidate_lemmas, unresolved_goals, counterexample_witnesses)
    )
    if verification_status in {VerificationStatus.PROVED.value, VerificationStatus.PARTIAL.value} and candidate_lemmas and not (proved_lemmas or generated_lemmas):
        generated_lemmas = candidate_lemmas[:]

    return VerificationRecord(
        schema_version=VerificationSchemaVersion.V1.value,
        provider=ProviderMetadata(
            provider_name=result.metadata.get("provider_name", "unknown"),
            adapter_name="structured-verification-adapter",
            adapter_version=VERIFICATION_PARSER_VERSION,
            provider_status=result.status,
            provider_blocker_type=result.blocker_type,
            external_id=result.external_id,
            external_status=result.external_status,
            metadata=dict(result.metadata),
        ),
        run=VerificationRunMetadata(
            parser_version=VERIFICATION_PARSER_VERSION,
            evaluator_version=EVALUATOR_VERSION,
            semantic_memory_version=SEMANTIC_MEMORY_VERSION,
            schema_version=VERIFICATION_SCHEMA_VERSION,
            artifact_paths=list(result.artifacts),
            raw_stdout_excerpt=result.raw_stdout[:1000],
            raw_stderr_excerpt=result.raw_stderr[:1000],
            notes=result.notes,
        ),
        verification_status=verification_status,
        theorem_status=_theorem_status_for(verification_status),
        unsolved_goals=_obs(unresolved_goals, VerificationArtifactKind.GOAL.value, provenance),
        generated_lemmas=_obs(generated_lemmas, VerificationArtifactKind.LEMMA.value, provenance),
        proved_lemmas=_obs(proved_lemmas, VerificationArtifactKind.LEMMA.value, provenance),
        missing_assumptions=_obs(missing_assumptions, VerificationArtifactKind.ASSUMPTION.value, provenance),
        counterexamples=_obs(counterexample_witnesses, VerificationArtifactKind.COUNTEREXAMPLE.value, provenance),
        blocker_observations=_obs(blocked_on or ([result.blocker_type] if result.blocker_type and result.blocker_type != "unknown" else []), VerificationArtifactKind.BLOCKER.value, provenance),
        proof_traces=_obs(proof_trace_fragments, VerificationArtifactKind.PROOF_TRACE.value, provenance),
        artifact_provenance=provenance,
        raw_text_fallback={
            "stdout": result.raw_stdout,
            "stderr": result.raw_stderr,
            "notes": result.notes,
            "combined_text": combined,
        },
        raw_payload={"provider_result": asdict(result)},
    )


def validate_verification_record(record: VerificationRecord) -> list[VerificationValidationIssue]:
    issues: list[VerificationValidationIssue] = []
    if record.schema_version != VerificationSchemaVersion.V1.value:
        issues.append(
            VerificationValidationIssue(
                issue_type="unsupported_schema_version",
                detail=f"Unsupported verification schema version `{record.schema_version}`.",
            )
        )
    if record.verification_status not in {item.value for item in VerificationStatus}:
        issues.append(
            VerificationValidationIssue(
                issue_type="invalid_verification_status",
                detail=f"Unexpected verification status `{record.verification_status}`.",
                path="verification_status",
            )
        )
    if not record.provider.provider_name:
        issues.append(
            VerificationValidationIssue(
                issue_type="missing_provider_name",
                detail="Verification record is missing provider metadata.",
                path="provider.provider_name",
            )
        )
    if not record.run.parser_version:
        issues.append(
            VerificationValidationIssue(
                issue_type="missing_parser_version",
                detail="Verification record is missing parser version stamping.",
                path="run.parser_version",
            )
        )
    if record.verification_status == VerificationStatus.PROVED.value and not record.proved_lemmas:
        issues.append(
            VerificationValidationIssue(
                issue_type="proved_without_artifact",
                detail="Verification record claims a proof but contains no proved lemmas.",
                severity=ValidationSeverity.WARNING.value,
                path="proved_lemmas",
            )
        )
    return issues


def _apply_semantic_ids(record: VerificationRecord, summary: SemanticMemorySummary) -> None:
    keyed = {}
    for artifact in summary.artifacts:
        keyed.setdefault((artifact.kind, artifact.raw_text), artifact)
    for bucket in (
        record.generated_lemmas,
        record.proved_lemmas,
        record.unsolved_goals,
        record.blocker_observations,
        record.missing_assumptions,
        record.counterexamples,
        record.proof_traces,
    ):
        for observation in bucket:
            artifact = keyed.get((observation.artifact_kind, observation.text))
            if artifact is None:
                continue
            observation.normalized_text = artifact.canonical_text
            observation.canonical_id = artifact.canonical_id
            observation.cluster_id = artifact.cluster_id


def build_followup_hints(record: VerificationRecord) -> Dict[str, list[dict[str, Any]]]:
    def _pack(items: list[VerificationObservation], kind: str) -> list[dict[str, Any]]:
        packed: list[dict[str, Any]] = []
        for item in items:
            packed.append(
                {
                    "kind": kind,
                    "text": item.text,
                    "normalized_text": item.normalized_text,
                    "canonical_id": item.canonical_id,
                    "cluster_id": item.cluster_id,
                    "confidence": item.confidence,
                }
            )
        return packed

    return {
        "proof_trace_fragments": _pack(record.proof_traces, "proof_trace"),
        "counterexample_witnesses": _pack(record.counterexamples, "counterexample"),
        "unresolved_goals": _pack(record.unsolved_goals, "goal"),
        "blocked_on": _pack(record.blocker_observations, "blocker"),
        "missing_assumptions": _pack(record.missing_assumptions, "assumption"),
    }


def summarize_boundary_map(record: VerificationRecord) -> Dict[str, Any]:
    fragile_variant = bool(record.counterexamples) and record.verification_status in {VerificationStatus.DISPROVED.value, VerificationStatus.PARTIAL.value}
    witness_backed_false_region = [item.text for item in record.counterexamples[:3]]
    assumption_repairs = [item.text for item in record.missing_assumptions[:3]]
    recurring_obstructions = [item.text for item in record.blocker_observations[:3]]
    summary_bits: list[str] = []
    if fragile_variant:
        summary_bits.append("fragile_variant")
    if witness_backed_false_region:
        summary_bits.append("witness-backed false region")
    if assumption_repairs:
        summary_bits.append("likely salvageable with assumption repair")
    if recurring_obstructions:
        summary_bits.append("recurring obstruction")
    return {
        "fragile_variant": fragile_variant,
        "witness_backed_false_region": witness_backed_false_region,
        "likely_salvageable_with_assumption_repair": assumption_repairs,
        "recurring_obstruction": recurring_obstructions,
        "summary": ", ".join(summary_bits) if summary_bits else "no sharp boundary signal",
    }


def prepare_ingested_result(result: ProviderResult) -> PreparedIngestion:
    from research_orchestrator.enhanced_ingestion import upgrade_provider_result

    result = upgrade_provider_result(result)
    record = result.verification_record if isinstance(result.verification_record, VerificationRecord) else parse_provider_result(result)
    if isinstance(result.verification_record, dict):
        try:
            record = parse_provider_result(
                ProviderResult(
                    **{
                        **asdict(result),
                        "verification_record": None,
                        "semantic_summary": None,
                    }
                )
            )
        except TypeError:
            record = parse_provider_result(result)
    issues = validate_verification_record(record)
    record.validation_issues = issues
    semantic_summary = canonicalize_record(record)
    _apply_semantic_ids(record, semantic_summary)

    enriched = ProviderResult(**{**asdict(result), "verification_record": None, "semantic_summary": None})
    enriched.verification_record = record
    enriched.semantic_summary = semantic_summary
    enriched.proof_outcome = record.verification_status
    enriched.generated_lemmas = [item.text for item in record.generated_lemmas]
    enriched.proved_lemmas = [item.text for item in record.proved_lemmas]
    enriched.candidate_lemmas = [item.text for item in record.generated_lemmas + record.proved_lemmas]
    enriched.unresolved_goals = [item.text for item in record.unsolved_goals]
    enriched.blocked_on = [item.text for item in record.blocker_observations]
    enriched.missing_assumptions = [item.text for item in record.missing_assumptions]
    enriched.suspected_missing_assumptions = enriched.missing_assumptions[:]
    enriched.proof_trace_fragments = [item.text for item in record.proof_traces]
    enriched.counterexample_witnesses = [item.text for item in record.counterexamples]
    enriched.normalized_candidate_lemmas = [item.normalized_text for item in record.generated_lemmas + record.proved_lemmas if item.normalized_text]
    enriched.normalized_unresolved_goals = [item.normalized_text for item in record.unsolved_goals if item.normalized_text]
    enriched.artifact_inventory = _artifact_inventory(result.artifacts)
    enriched.status = _status_from_outcome(record.verification_status, result)
    enriched.metadata = dict(enriched.metadata)
    enriched.metadata["verification_record"] = asdict(record)
    enriched.metadata["semantic_summary"] = asdict(semantic_summary)
    enriched.metadata["followup_hints"] = build_followup_hints(record)
    enriched.metadata["boundary_map"] = summarize_boundary_map(record)
    if issues:
        enriched.metadata["validation_issues"] = [asdict(item) for item in issues]
    enriched.new_signal_count = sum(1 for item in semantic_summary.artifacts if item.canonical_text)
    enriched.reused_signal_count = semantic_summary.normalized_equivalent_count + semantic_summary.exact_reuse_count
    enriched.signal_summary = _summary_for(enriched, record, semantic_summary)
    if not enriched.notes:
        enriched.notes = enriched.signal_summary
    return PreparedIngestion(
        provider_result=enriched,
        verification_record=record,
        semantic_summary=semantic_summary,
        validation_issues=issues,
    )


def ingest_provider_result(result: ProviderResult) -> ProviderResult:
    return prepare_ingested_result(result).provider_result


def build_verification_signals(
    *,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> list[VerificationSignal]:
    record = result.verification_record
    if record is None:
        record = prepare_ingested_result(result).verification_record
    provenance = record.artifact_provenance or [ArtifactProvenance(kind="stdout", path="", source="provider_result", confidence=0.55)]
    signals: list[VerificationSignal] = []

    for lemma in record.proved_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="verified_lemma",
                label=lemma.text,
                detail="Structured verification record marked this lemma as proved.",
                confidence=0.95,
                provenance=lemma.provenance or provenance,
                metadata={"canonical_id": lemma.canonical_id},
            )
        )
    for lemma in record.generated_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="reproducible_candidate_lemma",
                label=lemma.text,
                detail="Structured verification record surfaced a reusable generated lemma.",
                confidence=0.75,
                provenance=lemma.provenance or provenance,
                metadata={"canonical_id": lemma.canonical_id},
            )
        )
    for goal in record.unsolved_goals:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="recurring_subgoal",
                label=goal.text,
                detail="Structured verification retained this unsolved goal as a discovery object.",
                confidence=0.8,
                provenance=goal.provenance or provenance,
                metadata={"canonical_id": goal.canonical_id},
            )
        )
    for assumption in record.missing_assumptions:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="assumption_boundary",
                label=assumption.text,
                detail=f"Potentially necessary assumption under outcome={record.verification_status}.",
                confidence=0.78,
                provenance=assumption.provenance or provenance,
                metadata={"canonical_id": assumption.canonical_id},
            )
        )
    for witness in record.counterexamples:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="counterexample_witness",
                label=witness.text,
                detail="Structured verification captured a falsifying or fragility witness.",
                confidence=0.82,
                provenance=witness.provenance or provenance,
                metadata={"canonical_id": witness.canonical_id},
            )
        )
    for blocker in record.blocker_observations:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="formalization_blocker" if "failure" not in record.verification_status else "infra_incident",
                label=blocker.text,
                detail=result.signal_summary or result.notes,
                confidence=0.9,
                provenance=blocker.provenance or provenance,
                metadata={"canonical_id": blocker.canonical_id, "proof_outcome": result.proof_outcome},
            )
        )
    return signals


def save_proved_lemmas_to_ledger(
    db,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> None:
    """Save proved lemmas from a provider result to the proof ledger.

    This extracts proved lemmas from the verification record and adds them
    to the cumulative proof ledger for reuse across experiments.
    """
    record = result.verification_record
    if record is None:
        return

    for lemma in record.proved_lemmas:
        if not lemma.text or not lemma.canonical_id:
            continue

        # Check if already proved to avoid duplicates
        if db.lemma_is_proved(lemma.canonical_id):
            continue

        db.add_proof_ledger_entry(
            entry_id=str(uuid4()),
            project_id=project_id,
            conjecture_id=conjecture_id,
            experiment_id=experiment_id,
            lemma_statement=lemma.text,
            lemma_hash=lemma.canonical_id,
            proof_status="proved",
            proof_lean_code=lemma.raw_lean_code if hasattr(lemma, "raw_lean_code") else None,
            dependencies=[],  # TODO: extract dependencies from proof
        )
