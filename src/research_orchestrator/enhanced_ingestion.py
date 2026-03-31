"""Upgraded result ingestion that uses structured Lean parsing.

This module provides `enhanced_parse_provider_result` which replaces
the regex-based `parse_provider_result` in result_ingestion.py with
Lean-aware artifact extraction.

Integration point: call `upgrade_provider_result` on any ProviderResult
before passing it to the existing `prepare_ingested_result`. Or replace
`parse_provider_result` entirely.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from research_orchestrator.aristotle_result_parser import (
    AristotleResultAnalysis,
    analyze_aristotle_result,
)
from research_orchestrator.lean_parser import (
    LeanProjectAnalysis,
    parse_lean_file,
    parse_lean_project,
)
from research_orchestrator.result_ingestion import (
    _artifact_inventory,
    _merge_unique,
    _obs,
    _summary_for,
    _status_from_outcome,
    collect_result_artifacts,
    parse_provider_result,
    validate_verification_record,
)
from research_orchestrator.schema_versions import (
    EVALUATOR_VERSION,
    SEMANTIC_MEMORY_VERSION,
    VERIFICATION_PARSER_VERSION,
    VERIFICATION_SCHEMA_VERSION,
)
from research_orchestrator.semantic_memory import canonicalize_record
from research_orchestrator.types import (
    ArtifactProvenance,
    PreparedIngestion,
    ProviderMetadata,
    ProviderResult,
    SemanticMemorySummary,
    VerificationArtifactKind,
    VerificationObservation,
    VerificationRecord,
    VerificationRunMetadata,
    VerificationSchemaVersion,
    VerificationStatus,
)


def _preferred_artifact_paths(artifact_paths: List[str]) -> List[str]:
    """Prefer the most specific Lean artifact when duplicate basenames exist."""
    preferred_lean: Dict[str, str] = {}
    ordered_nonlean: List[str] = []

    for artifact in artifact_paths:
        path = Path(artifact)
        if path.suffix != ".lean":
            ordered_nonlean.append(artifact)
            continue
        key = path.name
        current = preferred_lean.get(key)
        if current is None or len(path.parts) > len(Path(current).parts):
            preferred_lean[key] = artifact

    combined: List[str] = []
    seen: set[str] = set()
    for artifact in artifact_paths:
        path = Path(artifact)
        chosen = artifact if path.suffix != ".lean" else preferred_lean.get(path.name, artifact)
        if chosen in seen:
            continue
        seen.add(chosen)
        combined.append(chosen)
    return combined


def _merge_observations(
    regex_obs: List[VerificationObservation],
    lean_obs: List[VerificationObservation],
) -> List[VerificationObservation]:
    """Merge observations from regex and Lean parsing, preferring Lean-sourced.

    Lean-sourced observations have higher confidence and richer provenance,
    so they take priority when texts overlap.
    """
    seen: set = set()
    merged: List[VerificationObservation] = []

    # Lean observations first (higher quality)
    for obs in lean_obs:
        key = obs.text.strip().lower()[:200]
        if key and key not in seen:
            seen.add(key)
            merged.append(obs)

    # Then regex observations that aren't duplicates
    for obs in regex_obs:
        key = obs.text.strip().lower()[:200]
        if key and key not in seen:
            seen.add(key)
            merged.append(obs)

    return merged


def enhanced_parse_provider_result(result: ProviderResult) -> VerificationRecord:
    """Parse a provider result using both Lean-aware extraction and regex fallback.

    This is a drop-in replacement for `parse_provider_result` that:
    1. Runs the Aristotle archive analyzer on artifact paths
    2. Falls back to the existing regex parser for anything not covered
    3. Merges both sources, preferring Lean-extracted content
    """
    # Step 1: Run the existing regex-based parser
    regex_record = parse_provider_result(result)

    # Step 2: Run the Lean-aware analyzer
    workspace_dir = ""
    for artifact in result.artifacts:
        path = Path(artifact)
        if path.is_dir():
            workspace_dir = str(path)
            break

    preferred_artifacts = _preferred_artifact_paths(list(result.artifacts))
    lean_result = analyze_aristotle_result(
        artifact_paths=preferred_artifacts,
        stdout=result.raw_stdout,
        stderr=result.raw_stderr,
        workspace_dir=workspace_dir,
    )

    # Step 3: If Lean analysis found nothing, return the regex result
    if not lean_result.has_meaningful_content():
        return regex_record

    # Step 4: Merge observations, preferring Lean-extracted content
    proved_lemmas = _merge_observations(regex_record.proved_lemmas, lean_result.proved_lemmas)
    generated_lemmas = _merge_observations(regex_record.generated_lemmas, lean_result.generated_lemmas)
    unsolved_goals = _merge_observations(regex_record.unsolved_goals, lean_result.unsolved_goals)
    blocker_observations = _merge_observations(regex_record.blocker_observations, lean_result.blocker_observations)
    proof_traces = _merge_observations(regex_record.proof_traces, lean_result.proof_traces)
    counterexamples = _merge_observations(regex_record.counterexamples, lean_result.counterexamples)
    missing_assumptions = _merge_observations(regex_record.missing_assumptions, lean_result.missing_assumptions)

    # Step 5: Use Lean-aware status if it's more specific
    verification_status = lean_result.verification_status
    if verification_status == VerificationStatus.UNKNOWN.value:
        verification_status = regex_record.verification_status

    # Step 6: Build the merged artifact provenance
    provenance = lean_result.artifact_provenance or regex_record.artifact_provenance

    # Step 7: Build the merged record
    theorem_status = regex_record.theorem_status
    if verification_status == VerificationStatus.PROVED.value:
        theorem_status = "verified"
    elif verification_status == VerificationStatus.PARTIAL.value:
        theorem_status = "partially_verified"
    elif verification_status == VerificationStatus.DISPROVED.value:
        theorem_status = "refuted"

    # Lean analysis metadata
    lean_metadata = {}
    if lean_result.lean_analysis:
        lean_metadata = {
            "sorry_count": lean_result.sorry_count,
            "completed_count": lean_result.completed_count,
            "error_count": lean_result.error_count,
            "file_count": len(lean_result.lean_analysis.files),
            "sorry_locations": [
                {
                    "file": s.file_path,
                    "line": s.line_number,
                    "declaration": s.enclosing_declaration,
                    "type": s.enclosing_type,
                }
                for s in lean_result.lean_analysis.all_sorry_locations[:10]
            ],
            "completed_declarations": [
                {
                    "name": d.name,
                    "kind": d.kind,
                    "file": d.file_path,
                    "dependencies": d.dependencies[:5],
                }
                for d in lean_result.lean_analysis.all_completed_proofs[:10]
            ],
        }
    if lean_result.manifest:
        lean_metadata["manifest"] = {
            "project_id": lean_result.manifest.project_id,
            "status": lean_result.manifest.status,
            "sorries_filled": lean_result.manifest.sorries_filled,
            "sorries_remaining": lean_result.manifest.sorries_remaining,
        }

    return VerificationRecord(
        schema_version=VerificationSchemaVersion.V1.value,
        provider=ProviderMetadata(
            provider_name=result.metadata.get("provider_name", regex_record.provider.provider_name),
            adapter_name="lean-aware-verification-adapter",
            adapter_version=VERIFICATION_PARSER_VERSION,
            provider_status=result.status,
            provider_blocker_type=result.blocker_type,
            external_id=result.external_id,
            external_status=result.external_status,
            metadata={
                **dict(result.metadata),
                "lean_analysis": lean_metadata,
                "parser_upgrade": "lean_aware_v1",
            },
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
        theorem_status=theorem_status,
        unsolved_goals=unsolved_goals,
        generated_lemmas=generated_lemmas,
        proved_lemmas=proved_lemmas,
        missing_assumptions=missing_assumptions,
        counterexamples=counterexamples,
        blocker_observations=blocker_observations,
        proof_traces=proof_traces,
        artifact_provenance=provenance,
        raw_text_fallback=regex_record.raw_text_fallback,
        raw_payload={
            "provider_result": asdict(result),
            "lean_analysis_summary": lean_metadata,
        },
    )


def upgrade_provider_result(result: ProviderResult) -> ProviderResult:
    """Upgrade a ProviderResult with Lean-aware content extraction.

    This enriches the result's fields (generated_lemmas, proved_lemmas,
    unresolved_goals, etc.) with content extracted from actual Lean artifacts,
    without changing the ProviderResult interface.

    Call this before passing to `prepare_ingested_result` to get richer signal.
    """
    workspace_dir = ""
    for artifact in result.artifacts:
        path = Path(artifact)
        if path.is_dir():
            workspace_dir = str(path)
            break

    preferred_artifacts = _preferred_artifact_paths(list(result.artifacts))
    lean_result = analyze_aristotle_result(
        artifact_paths=preferred_artifacts,
        stdout=result.raw_stdout,
        stderr=result.raw_stderr,
        workspace_dir=workspace_dir,
    )
    regex_record = parse_provider_result(result)

    if not lean_result.has_meaningful_content():
        return result

    upgraded_status = lean_result.verification_status
    parsed_blockers = [
        obs for obs in regex_record.blocker_observations if obs.text != result.blocker_type
    ]
    if upgraded_status == VerificationStatus.PROVED.value and (
        regex_record.unsolved_goals
        or parsed_blockers
        or regex_record.missing_assumptions
        or regex_record.counterexamples
    ):
        upgraded_status = VerificationStatus.PARTIAL.value

    # Enrich without overwriting
    result.proved_lemmas = _merge_unique(
        result.proved_lemmas,
        [obs.text for obs in lean_result.proved_lemmas],
    )
    result.generated_lemmas = _merge_unique(
        result.generated_lemmas,
        [obs.text for obs in lean_result.generated_lemmas],
    )
    result.candidate_lemmas = _merge_unique(
        result.candidate_lemmas,
        [obs.text for obs in lean_result.generated_lemmas + lean_result.proved_lemmas],
    )
    result.unresolved_goals = _merge_unique(
        result.unresolved_goals,
        [obs.text for obs in lean_result.unsolved_goals],
    )
    result.proof_trace_fragments = _merge_unique(
        result.proof_trace_fragments,
        [obs.text for obs in lean_result.proof_traces],
    )
    result.counterexample_witnesses = _merge_unique(
        result.counterexample_witnesses,
        [obs.text for obs in lean_result.counterexamples],
    )
    result.blocked_on = _merge_unique(
        result.blocked_on,
        [obs.text for obs in lean_result.blocker_observations],
    )
    result.missing_assumptions = _merge_unique(
        result.missing_assumptions,
        [obs.text for obs in lean_result.missing_assumptions],
    )

    # Update metadata
    result.metadata = dict(result.metadata)
    if lean_result.lean_analysis:
        result.metadata["lean_sorry_count"] = lean_result.sorry_count
        result.metadata["lean_completed_count"] = lean_result.completed_count
        result.metadata["lean_error_count"] = lean_result.error_count
    if upgraded_status != VerificationStatus.UNKNOWN.value:
        result.proof_outcome = upgraded_status

    return result
