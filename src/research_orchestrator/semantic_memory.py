from __future__ import annotations

import hashlib
from collections import Counter
from typing import Dict, Iterable, List

from research_orchestrator.lemma_utils import normalize_goal, normalize_lemma
from research_orchestrator.types import SemanticArtifact, SemanticMemorySummary, VerificationArtifactKind, VerificationRecord


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def canonicalize_text(kind: str, text: str, theorem_family: str = "") -> SemanticArtifact:
    cleaned = " ".join(text.strip().split())
    if kind == VerificationArtifactKind.LEMMA.value:
        canonical = normalize_lemma(cleaned)
    else:
        canonical = normalize_goal(cleaned)
    family_prefix = f"{theorem_family.lower()}::" if theorem_family else ""
    canonical_key = family_prefix + canonical
    exact_key = family_prefix + cleaned.lower()
    return SemanticArtifact(
        kind=kind,
        raw_text=cleaned,
        canonical_text=canonical,
        exact_id=_stable_id(f"{kind}:exact", exact_key),
        canonical_id=_stable_id(f"{kind}:canonical", canonical_key),
        cluster_id=_stable_id(f"{kind}:cluster", canonical_key),
        theorem_family=theorem_family,
        metadata={},
    )


def canonicalize_record(record: VerificationRecord, theorem_family: str = "") -> SemanticMemorySummary:
    artifacts: List[SemanticArtifact] = []
    for observation in record.generated_lemmas + record.proved_lemmas:
        artifacts.append(canonicalize_text(VerificationArtifactKind.LEMMA.value, observation.text, theorem_family))
    for observation in record.unsolved_goals:
        artifacts.append(canonicalize_text(VerificationArtifactKind.GOAL.value, observation.text, theorem_family))
    for observation in record.blocker_observations:
        artifacts.append(canonicalize_text(VerificationArtifactKind.BLOCKER.value, observation.text, theorem_family))
    for observation in record.missing_assumptions:
        artifacts.append(canonicalize_text(VerificationArtifactKind.ASSUMPTION.value, observation.text, theorem_family))
    for observation in record.counterexamples:
        artifacts.append(canonicalize_text(VerificationArtifactKind.COUNTEREXAMPLE.value, observation.text, theorem_family))
    for observation in record.proof_traces:
        artifacts.append(canonicalize_text(VerificationArtifactKind.PROOF_TRACE.value, observation.text, theorem_family))

    exact_counts = Counter(item.exact_id for item in artifacts)
    canonical_counts = Counter(item.canonical_id for item in artifacts)
    by_kind: Dict[str, Dict[str, int]] = {}
    for item in artifacts:
        stats = by_kind.setdefault(item.kind, {"count": 0})
        stats["count"] += 1

    return SemanticMemorySummary(
        artifacts=artifacts,
        duplicate_artifact_count=sum(count - 1 for count in exact_counts.values() if count > 1),
        normalized_equivalent_count=sum(count - 1 for count in canonical_counts.values() if count > 1),
        reusable_artifact_count=sum(1 for item in artifacts if item.kind in {VerificationArtifactKind.LEMMA.value, VerificationArtifactKind.PROOF_TRACE.value}),
        obstruction_artifact_count=sum(1 for item in artifacts if item.kind in {VerificationArtifactKind.BLOCKER.value, VerificationArtifactKind.ASSUMPTION.value}),
        boundary_artifact_count=sum(1 for item in artifacts if item.kind in {VerificationArtifactKind.COUNTEREXAMPLE.value, VerificationArtifactKind.ASSUMPTION.value}),
        proof_motif_count=sum(1 for item in artifacts if item.kind == VerificationArtifactKind.PROOF_TRACE.value),
        blocker_reuse_count=sum(count - 1 for key, count in canonical_counts.items() if key.startswith(f"{VerificationArtifactKind.BLOCKER.value}:canonical") and count > 1),
        parser_ambiguity_count=len(record.validation_issues),
        by_kind=by_kind,
    )


def hydrate_semantic_summary(
    artifacts: Iterable[SemanticArtifact],
    *,
    new_exact_count: int,
    normalized_equivalent_count: int,
    exact_reuse_count: int,
    canonical_reuse_count: int,
    blocker_reuse_count: int,
    parser_ambiguity_count: int,
) -> SemanticMemorySummary:
    materialized = list(artifacts)
    summary = SemanticMemorySummary(
        artifacts=materialized,
        new_exact_count=new_exact_count,
        normalized_equivalent_count=normalized_equivalent_count,
        exact_reuse_count=exact_reuse_count,
        canonical_reuse_count=canonical_reuse_count,
        blocker_reuse_count=blocker_reuse_count,
        parser_ambiguity_count=parser_ambiguity_count,
    )
    summary.duplicate_artifact_count = max(0, exact_reuse_count + normalized_equivalent_count - new_exact_count)
    summary.reusable_artifact_count = sum(
        1 for item in materialized if item.kind in {VerificationArtifactKind.LEMMA.value, VerificationArtifactKind.PROOF_TRACE.value}
    )
    summary.obstruction_artifact_count = sum(
        1 for item in materialized if item.kind in {VerificationArtifactKind.BLOCKER.value, VerificationArtifactKind.ASSUMPTION.value}
    )
    summary.boundary_artifact_count = sum(
        1 for item in materialized if item.kind in {VerificationArtifactKind.COUNTEREXAMPLE.value, VerificationArtifactKind.ASSUMPTION.value}
    )
    summary.proof_motif_count = sum(1 for item in materialized if item.kind == VerificationArtifactKind.PROOF_TRACE.value)
    return summary
