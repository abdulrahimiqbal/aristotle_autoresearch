from __future__ import annotations

from typing import List, Optional

from research_orchestrator.result_ingestion import prepare_ingested_result
from research_orchestrator.types import EvaluationScore, ProviderResult, ProjectCharter, SemanticMemorySummary, VerificationRecord


def _fallback_score(charter: ProjectCharter, result: ProviderResult) -> EvaluationScore:
    info_gain = float(
        len(result.generated_lemmas)
        + len(result.candidate_lemmas)
        + len(result.unresolved_goals)
        + len(result.missing_assumptions or result.suspected_missing_assumptions)
        + len(result.proof_trace_fragments)
        + len(result.counterexample_witnesses) * 2
    )
    novelty = float(len(set(result.generated_lemmas + result.proved_lemmas + result.candidate_lemmas)))
    reusability = float(
        len(result.proved_lemmas) * 1.5
        + len(result.generated_lemmas) * 0.75
        + len(result.candidate_lemmas) * 0.5
        + len(result.unresolved_goals) * 0.25
        + len(result.proof_trace_fragments) * 0.25
        + len(result.counterexample_witnesses)
    )
    boundary = 1.8 if result.proof_outcome == "disproved" else 0.8 if result.blocker_type in {"structural", "formalization"} else 0.5
    cost_penalty = 0.6 if result.proof_outcome in {"infra_failure", "auth_failure"} else 0.5 if result.status == "failed" else 0.2
    total = info_gain + novelty + reusability + boundary - cost_penalty
    return EvaluationScore(
        information_gain=info_gain,
        novelty=novelty,
        reusability=reusability,
        boundary_sharpness=boundary,
        cost_penalty=cost_penalty,
        total=round(total, 3),
        notes=["fallback_evaluator=true"],
    )


def score_result(
    charter: ProjectCharter,
    result: ProviderResult,
    *,
    verification_record: Optional[VerificationRecord] = None,
    semantic_summary: Optional[SemanticMemorySummary] = None,
) -> EvaluationScore:
    if verification_record is None or semantic_summary is None:
        prepared = prepare_ingested_result(result)
        verification_record = prepared.verification_record
        semantic_summary = prepared.semantic_summary

    if verification_record is None or semantic_summary is None:
        return _fallback_score(charter, result)

    unique_canonical = len({item.canonical_id for item in semantic_summary.artifacts if item.canonical_id})
    equivalent_penalty = max(
        semantic_summary.normalized_equivalent_count,
        max(0, len(semantic_summary.artifacts) - unique_canonical),
    )
    exact_novelty = float(max(semantic_summary.new_exact_count, unique_canonical))
    normalized_novelty = float(
        max(
            0,
            unique_canonical - semantic_summary.canonical_reuse_count - semantic_summary.exact_reuse_count,
        )
    )
    novelty = max(0.0, exact_novelty + 0.5 * normalized_novelty - 0.8 * equivalent_penalty)

    reusability = float(
        len(verification_record.proved_lemmas) * 2.0
        + len(verification_record.generated_lemmas) * 1.2
        + semantic_summary.reusable_artifact_count * 0.4
        + semantic_summary.proof_motif_count * 0.3
    )
    obstruction = float(
        len(verification_record.blocker_observations) * 1.1
        + len(verification_record.missing_assumptions) * 0.8
        + semantic_summary.blocker_reuse_count * 0.35
    )
    boundary = float(
        len(verification_record.counterexamples) * 1.6
        + len(verification_record.missing_assumptions) * 0.5
        + (1.0 if verification_record.verification_status == "disproved" else 0.0)
    )
    transfer = float(
        len({item.cluster_id for item in verification_record.generated_lemmas + verification_record.proved_lemmas if item.cluster_id}) * 0.6
        + semantic_summary.proof_motif_count * 0.25
    )
    duplication_penalty = float(semantic_summary.exact_reuse_count * 0.9 + semantic_summary.normalized_equivalent_count * 0.6)
    ambiguity_penalty = float(len(verification_record.validation_issues) * 0.7 + semantic_summary.parser_ambiguity_count * 0.4)
    shallow_count_penalty = float(max(0, len(semantic_summary.artifacts) - semantic_summary.new_exact_count) * 0.1)
    cost_penalty = 0.6 if verification_record.verification_status in {"infra_failure", "auth_failure"} else 0.45 if result.status == "failed" else 0.2

    information_gain = novelty + obstruction + boundary + transfer

    weights = charter.evaluator_weights or {}
    total = (
        information_gain * weights.get("information_gain", 1.0)
        + novelty * weights.get("novelty", 1.0)
        + reusability * weights.get("reusability", 1.0)
        + boundary * weights.get("boundary_sharpness", 1.0)
        + obstruction * weights.get("obstruction_discovery", 0.8)
        + transfer * weights.get("transfer_potential", 0.7)
        - cost_penalty * weights.get("cost_penalty", 1.0)
        - duplication_penalty * weights.get("duplication_penalty", 1.0)
        - ambiguity_penalty * weights.get("ambiguity_penalty", 1.0)
        - shallow_count_penalty * weights.get("shallow_count_penalty", 0.8)
    )

    notes: List[str] = [
        f"verification_status={verification_record.verification_status}",
        f"new_exact={semantic_summary.new_exact_count}",
        f"exact_reuse={semantic_summary.exact_reuse_count}",
        f"normalized_reuse={semantic_summary.canonical_reuse_count}",
        f"blocker_reuse={semantic_summary.blocker_reuse_count}",
        f"validation_issues={len(verification_record.validation_issues)}",
    ]
    if verification_record.proved_lemmas:
        notes.append(f"proved_lemmas={len(verification_record.proved_lemmas)}")
    if verification_record.generated_lemmas:
        notes.append(f"generated_lemmas={len(verification_record.generated_lemmas)}")
    if verification_record.unsolved_goals:
        notes.append(f"unsolved_goals={len(verification_record.unsolved_goals)}")
    if verification_record.counterexamples:
        notes.append(f"counterexamples={len(verification_record.counterexamples)}")

    return EvaluationScore(
        information_gain=round(information_gain, 3),
        novelty=round(novelty, 3),
        reusability=round(reusability, 3),
        boundary_sharpness=round(boundary, 3),
        cost_penalty=round(cost_penalty, 3),
        total=round(total, 3),
        obstruction_discovery=round(obstruction, 3),
        transfer_potential=round(transfer, 3),
        duplication_penalty=round(duplication_penalty + shallow_count_penalty, 3),
        ambiguity_penalty=round(ambiguity_penalty, 3),
        notes=notes,
    )
