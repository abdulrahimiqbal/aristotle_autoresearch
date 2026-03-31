from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from research_orchestrator.db import Database


@dataclass
class RouteScore:
    route_id: str
    route_key: str
    conjecture_id: str
    route_status: str
    total_score: float
    components: Dict[str, float]
    summary: Dict[str, Any]


def route_key_for_candidate(candidate: Dict[str, Any]) -> str:
    conjecture_id = candidate.get("conjecture_id", "unknown")
    motif_signature = candidate.get("motif_signature") or candidate.get("candidate_metadata", {}).get("motif_signature")
    if motif_signature:
        return f"{conjecture_id}::motif:{motif_signature}"
    move_family = candidate.get("move_family") or candidate.get("move") or "unknown"
    return f"{conjecture_id}::move:{move_family}"


def _base_route_key(conjecture_id: str) -> str:
    return f"{conjecture_id}::base"


def _route_strength(components: Dict[str, float], operator_priority: int, route_status: str) -> float:
    penalty = 0.0
    if route_status == "stalled":
        penalty = 4.0
    if route_status == "closed":
        penalty = 100.0
    score = (
        components.get("recent_signal_velocity", 0.0) * 1.4
        + components.get("reuse_score", 0.0) * 1.0
        + components.get("transfer_score", 0.0) * 1.1
        + components.get("novelty_score", 0.0) * 0.8
        + components.get("signal_support", 0.0) * 1.2
        - components.get("blocker_pressure", 0.0) * 0.7
        - components.get("no_signal_pressure", 0.0) * 0.9
        + float(operator_priority) * 2.0
    )
    return round(score - penalty, 4)


def assign_routes_to_frontier(
    db: Database,
    project_id: str,
    frontier: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[RouteScore]]:
    conjectures = db.list_conjectures(project_id)
    route_keys: set[str] = {_base_route_key(conjecture.conjecture_id) for conjecture in conjectures}
    for candidate in frontier:
        route_keys.add(route_key_for_candidate(candidate))

    route_records: Dict[str, Dict[str, Any]] = {}
    for route_key in route_keys:
        existing = db.get_theorem_route_by_key(route_key)
        if existing is not None:
            route_records[route_key] = existing
            continue
        route_id = f"route:{route_key}"
        if len(route_id) > 120:
            route_id = route_id[:120]
        route_records[route_key] = {
            "route_id": route_id,
            "project_id": project_id,
            "route_key": route_key,
            "route_stage": "mapping",
            "route_status": "active",
            "summary": {},
            "theorem_family": "",
        }

    candidates_by_route: Dict[str, List[Dict[str, Any]]] = {key: [] for key in route_keys}
    for candidate in frontier:
        key = route_key_for_candidate(candidate)
        candidates_by_route.setdefault(key, []).append(candidate)
        base_key = _base_route_key(candidate.get("conjecture_id", "unknown"))
        candidates_by_route.setdefault(base_key, []).append(candidate)

    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    route_scores: List[RouteScore] = []
    for route_key, candidates in candidates_by_route.items():
        if not candidates:
            continue
        route = route_records[route_key]
        conjecture_id = candidates[0].get("conjecture_id", "")
        route.setdefault("conjecture_id", conjecture_id)
        operator_priority = int(route.get("operator_priority", 0))

        recent_signal_velocity = max((candidate.get("recent_signal_velocity", 0) for candidate in candidates), default=0.0)
        reuse_score = max((candidate.get("reuse_potential", 0) for candidate in candidates), default=0.0)
        transfer_score = max((candidate.get("transfer_opportunity", 0) for candidate in candidates), default=0.0)
        novelty_score = max((candidate.get("semantic_novelty", 0) for candidate in candidates), default=0.0)
        signal_support = max((candidate.get("signal_support", 0) for candidate in candidates), default=0.0)
        blocker_pressure = max((candidate.get("blocker_support", 0) for candidate in candidates), default=0.0)
        no_signal_pressure = max(
            (no_signal.get((candidate.get("conjecture_id", ""), candidate.get("move", "")), 0) for candidate in candidates),
            default=0.0,
        )
        components = {
            "recent_signal_velocity": float(recent_signal_velocity),
            "reuse_score": float(reuse_score),
            "transfer_score": float(transfer_score),
            "novelty_score": float(novelty_score),
            "signal_support": float(signal_support),
            "blocker_pressure": float(blocker_pressure),
            "no_signal_pressure": float(no_signal_pressure),
        }
        total_score = _route_strength(components, operator_priority, route.get("route_status", "active"))

        top_candidate = max(
            candidates,
            key=lambda candidate: (
                candidate.get("signal_support", 0),
                candidate.get("recent_signal_velocity", 0),
                candidate.get("reuse_potential", 0),
            ),
        )
        summary = {
            "top_candidate_id": top_candidate.get("experiment_id"),
            "top_move_family": top_candidate.get("move_family") or top_candidate.get("move"),
            "motif_signature": top_candidate.get("motif_signature"),
            "candidate_count": len(candidates),
            "components": components,
        }
        route.update(
            {
                "current_strength": total_score,
                "recent_signal_velocity": components["recent_signal_velocity"],
                "blocker_pressure": components["blocker_pressure"],
                "novelty_score": components["novelty_score"],
                "reuse_score": components["reuse_score"],
                "transfer_score": components["transfer_score"],
                "summary": summary,
            }
        )
        db.upsert_theorem_route(route)
        route_scores.append(
            RouteScore(
                route_id=route["route_id"],
                route_key=route_key,
                conjecture_id=conjecture_id,
                route_status=route.get("route_status", "active"),
                total_score=total_score,
                components=components,
                summary=summary,
            )
        )

    for candidate in frontier:
        key = route_key_for_candidate(candidate)
        route = route_records[key]
        candidate["route_id"] = route["route_id"]
        candidate["route_key"] = key
        metadata = candidate.setdefault("candidate_metadata", {})
        metadata["route_key"] = key
        metadata["route_id"] = route["route_id"]

    return frontier, route_scores


def select_route(route_scores: List[RouteScore]) -> Tuple[RouteScore | None, List[RouteScore]]:
    if not route_scores:
        return None, []
    ranked = sorted(route_scores, key=lambda item: (-item.total_score, item.route_key))
    return ranked[0], ranked
