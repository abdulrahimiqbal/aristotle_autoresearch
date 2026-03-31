from __future__ import annotations

from collections import Counter
from typing import Any


def _slugify(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def classify_proof_traction(
    *,
    experiments_count: int,
    recurring_reuse: int,
    stabilized_lemmas: int,
    recurring_subgoals: int,
    recurring_traces: int,
    witness_density: float,
    recent_signal_velocity: float,
) -> str:
    if experiments_count <= 1 and recurring_reuse == 0:
        return "exploratory"
    route_score = (
        stabilized_lemmas * 2
        + recurring_subgoals * 2
        + recurring_traces * 3
        + recurring_reuse
        + int(witness_density >= 0.5)
        + int(recent_signal_velocity >= 1.0)
    )
    if recurring_traces >= 2 and stabilized_lemmas >= 2 and route_score >= 9:
        return "closure-attempt ready"
    if recurring_traces >= 1 and route_score >= 7:
        return "proof-fragment emerging"
    if recurring_subgoals >= 1 and recurring_reuse >= 2:
        return "route-forming"
    if recurring_reuse >= 1 or recent_signal_velocity > 0:
        return "structure-forming"
    return "exploratory"


def choose_strongest_motif(
    conjecture_id: str,
    experiments: list[dict[str, Any]],
    knowledge_structures: list[dict[str, Any]],
) -> str:
    weighted = Counter()
    for item in experiments:
        if item.get("conjecture_id") != conjecture_id:
            continue
        motif = (item.get("motif_signature") or item.get("motif_id") or "").strip()
        if not motif:
            continue
        weighted[motif] += int(item.get("new_signal_count", 0) or 0) + 1
    if weighted:
        return weighted.most_common(1)[0][0]
    fallback = [
        row["name"]
        for row in knowledge_structures
        if conjecture_id in row.get("touches", [])
        and row.get("type") in {"recurring lemma", "recurring subgoal", "recurring proof trace", "witness motif"}
    ]
    return fallback[0] if fallback else "no stable motif yet"


def choose_strongest_obstruction(
    conjecture_id: str,
    experiments: list[dict[str, Any]],
    missing_assumptions: dict[str, list[str]],
) -> str:
    blocker_counter = Counter()
    for item in experiments:
        if item.get("conjecture_id") != conjecture_id:
            continue
        blocker = (item.get("blocker_type") or "").strip()
        if blocker and blocker != "unknown":
            blocker_counter[blocker] += 1
    if blocker_counter:
        return blocker_counter.most_common(1)[0][0]
    assumptions = Counter(missing_assumptions.get(conjecture_id, []))
    if assumptions:
        return f"missing assumption: {assumptions.most_common(1)[0][0]}"
    return "no recurring obstruction yet"


def summarize_problem_progress(
    *,
    conjecture_id: str,
    experiments_count: int,
    new_signals: int,
    traction: str,
    strongest_motif: str,
    strongest_obstruction: str,
    missing_assumptions: list[str],
) -> tuple[str, str]:
    route = (
        f"Push '{strongest_motif}' toward reusable assets"
        if strongest_motif != "no stable motif yet"
        else "Increase structure discovery before route commitments"
    )
    if traction in {"proof-fragment emerging", "closure-attempt ready"}:
        route = "Attempt closure route with promoted traces and stabilized lemmas"
    if traction == "exploratory":
        route = "Probe boundary variants and diversify move families"
    if missing_assumptions:
        missing = f"still missing assumptions: {', '.join(sorted(set(missing_assumptions))[:3])}"
    elif strongest_obstruction != "no recurring obstruction yet":
        missing = f"still blocked by recurring obstruction '{strongest_obstruction}'"
    elif new_signals == 0 and experiments_count > 0:
        missing = "still missing fresh signal-producing branch"
    else:
        missing = "still missing stable proof fragments"
    return route, missing


def summarize_falsehood_boundary(
    *,
    conjecture_id: str,
    disproved_count: int,
    witness_regions: list[str],
    missing_assumptions: list[str],
    salvage_hints: list[str],
) -> dict[str, str]:
    witness_text = ", ".join(witness_regions[:2]) if witness_regions else "no witness-backed region recorded"
    missing_text = ", ".join(sorted(set(missing_assumptions))[:3]) if missing_assumptions else "none recurring"
    salvage_text = ", ".join(salvage_hints[:2]) if salvage_hints else "no concrete repair hint yet"
    return {
        "conjecture_id": conjecture_id,
        "falsified_weakened_variants": f"{disproved_count} disproved variant runs",
        "witness_backed_false_regions": witness_text,
        "recurring_missing_assumptions": missing_text,
        "likely_salvageable_repairs": salvage_text,
    }


def summarize_recent_result(experiment: dict[str, Any]) -> str:
    outcome = (experiment.get("proof_outcome") or "").lower()
    status = (experiment.get("status") or "").lower()
    new_signal = int(experiment.get("new_signal_count") or 0)
    reused = int(experiment.get("reused_signal_count") or 0)
    boundary = (experiment.get("boundary_summary") or "").strip()
    if outcome == "disproved" and new_signal >= 1:
        return "falsified a fragile variant and sharpened a boundary"
    if reused >= 3 and new_signal == 0:
        return "reused prior structure without adding new signal"
    if new_signal >= 5:
        return "promoted recurring subgoal evidence"
    if status in {"stalled", "failed"} and new_signal == 0 and not boundary:
        return "added local structure but no stable proof asset"
    if status in {"submitted", "in_progress", "planned"}:
        return "queued for evaluation; interpretation pending completion"
    return "produced incremental evidence for route selection"


def normalize_structure_type(raw_kind: str, name: str) -> tuple[str, str]:
    kind = (raw_kind or "").strip().lower()
    lowered_name = (name or "").lower()
    if kind in {"lemma", "recurring lemma"}:
        return "recurring lemma", "lemma reuse candidate"
    if kind in {"subgoal", "goal", "recurring_subgoal"}:
        return "recurring subgoal", "intermediate proof target"
    if kind in {"proof_trace", "trace"}:
        return "recurring proof trace", "proof-fragment motif"
    if kind in {"counterexample", "witness", "witness_motif"}:
        return "witness motif", "false-region witness"
    if kind in {"blocker", "obstruction"} or "obstruction" in lowered_name or "boundary" in lowered_name:
        return "boundary fact / obstruction", "recurring blocker or boundary condition"
    return "recurring structure", "general recurring signal"


def structure_status_from_reuse(reuse: int) -> str:
    if reuse >= 8:
        return "stabilizing"
    if reuse >= 4:
        return "emerging"
    return "early"


def normalized_name(text: str) -> str:
    return _slugify((text or "").strip()) or "unknown_structure"

