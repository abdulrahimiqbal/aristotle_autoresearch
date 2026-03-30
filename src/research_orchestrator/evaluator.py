from __future__ import annotations

from typing import Dict, List

from research_orchestrator.types import EvaluationScore, ProviderResult, ProjectCharter


def score_result(charter: ProjectCharter, result: ProviderResult) -> EvaluationScore:
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
        + len(result.counterexample_witnesses) * 1.0
    )
    if result.proof_outcome in {"infra_failure", "auth_failure"} or result.blocker_type in {"dns_failure", "network_unavailable"}:
        boundary = 0.0
    elif result.proof_outcome == "disproved":
        boundary = 1.8
    elif result.blocker_type in {"structural", "malformed"}:
        boundary = 1.5
    elif result.blocker_type in {"search", "formalization"}:
        boundary = 0.8
    else:
        boundary = 0.5
    if result.counterexample_witnesses:
        boundary += 0.8
    if result.new_signal_count:
        boundary += min(1.0, result.new_signal_count * 0.1)
    cost_penalty = 0.6 if result.proof_outcome in {"infra_failure", "auth_failure"} else 0.5 if result.status == "failed" else 0.2

    weights = charter.evaluator_weights or {}
    total = (
        info_gain * weights.get("information_gain", 1.0)
        + novelty * weights.get("novelty", 1.0)
        + reusability * weights.get("reusability", 1.0)
        + boundary * weights.get("boundary_sharpness", 1.0)
        - cost_penalty * weights.get("cost_penalty", 1.0)
    )

    notes: List[str] = []
    if result.generated_lemmas:
        notes.append(f"generated_lemmas={len(result.generated_lemmas)}")
    if result.candidate_lemmas:
        notes.append(f"candidate_lemmas={len(result.candidate_lemmas)}")
    if result.unresolved_goals:
        notes.append(f"unresolved_goals={len(result.unresolved_goals)}")
    if result.proof_trace_fragments:
        notes.append(f"proof_traces={len(result.proof_trace_fragments)}")
    if result.counterexample_witnesses:
        notes.append(f"counterexample_witnesses={len(result.counterexample_witnesses)}")
    if result.missing_assumptions or result.suspected_missing_assumptions:
        notes.append(f"missing_assumptions={len(result.missing_assumptions or result.suspected_missing_assumptions)}")
    notes.append(f"new_signal_count={result.new_signal_count}")
    notes.append(f"reused_signal_count={result.reused_signal_count}")
    notes.append(f"proof_outcome={result.proof_outcome}")
    notes.append(f"blocker={result.blocker_type}")

    return EvaluationScore(
        information_gain=info_gain,
        novelty=novelty,
        reusability=reusability,
        boundary_sharpness=boundary,
        cost_penalty=cost_penalty,
        total=round(total, 3),
        notes=notes,
    )
