from __future__ import annotations

from typing import Dict, List

from research_orchestrator.types import EvaluationScore, ProviderResult, ProjectCharter


def score_result(charter: ProjectCharter, result: ProviderResult) -> EvaluationScore:
    info_gain = float(len(result.generated_lemmas) + len(result.suspected_missing_assumptions))
    novelty = float(len(set(result.generated_lemmas + result.proved_lemmas)))
    reusability = float(len(result.proved_lemmas) * 1.5 + len(result.generated_lemmas) * 0.5)
    if result.blocker_type in {"dns_failure", "network_unavailable"}:
        boundary = 0.0
    elif result.blocker_type in {"structural", "malformed"}:
        boundary = 1.5
    elif result.blocker_type in {"search", "formalization"}:
        boundary = 0.8
    else:
        boundary = 0.5
    cost_penalty = 0.5 if result.status == "failed" else 0.2

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
    if result.suspected_missing_assumptions:
        notes.append(f"missing_assumptions={len(result.suspected_missing_assumptions)}")
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
