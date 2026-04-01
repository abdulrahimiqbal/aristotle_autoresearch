from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Tuple

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate
from research_orchestrator.llm_manager import build_campaign_brief, render_campaign_brief
from research_orchestrator.schema_versions import MANAGER_POLICY_VERSION
from research_orchestrator.move_registry import MoveCandidate
from research_orchestrator.prompts import build_manager_prompt, build_project_constitution


MOVE_PRIORITY = {
    "boundary_map_from_missing_assumption": 0,
    "boundary_map_from_witness": 1,
    "counterexample_mode": 2,
    "underspecify": 3,
    "perturb_assumption": 4,
    "promote_lemma": 5,
    "promote_subgoal": 6,
    "promote_trace": 7,
    "reformulate": 8,
}


@dataclass
class CandidateDecision:
    experiment_id: str
    conjecture_id: str
    move: str
    reason: str
    expected_signal: str
    modification: Dict[str, Any]
    workspace_dir: str
    lean_file: str
    phase: str
    policy_score: float = 0.0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    chosen: List[CandidateDecision] = field(default_factory=list)
    skipped: List[Dict[str, Any]] = field(default_factory=list)
    policy_path: str = "fallback"
    manager_prompt: str = ""
    raw_response: str = ""
    rationale: str = ""
    candidate_audits: List[Dict[str, Any]] = field(default_factory=list)


def _counts_by_conjecture(conjectures, experiments):
    counts = {conjecture.conjecture_id: 0 for conjecture in conjectures}
    for experiment in experiments:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in counts:
            counts[conjecture_id] += 1
    return counts


def _has_seeded_structure(conjecture) -> bool:
    return any(
        conjecture.family_metadata.get(key)
        for key in (
            "seed_invariants",
            "seed_subclaims",
            "seed_extremal_targets",
            "seed_adversarial_targets",
            "seed_witness_targets",
            "seed_transfer_hints",
            "seed_discovery_questions",
        )
    )


def _manager_candidate_slice(conjecture, experiments, candidates):
    if _has_seeded_structure(conjecture):
        return candidates
    existing = [exp for exp in experiments if exp["conjecture_id"] == conjecture.conjecture_id]
    if existing:
        return candidates
    return [cand for cand in candidates if cand.move_family not in {"transfer_reformulation", "cross_conjecture_analogy"}]


def _frontier_sort_key(candidate: Dict[str, Any]):
    move_priority = MOVE_PRIORITY.get(candidate["move"], 99)
    stage_priority = move_priority if candidate["existing_experiments"] == 0 else (-1 if candidate.get("targets_recurring_structure") else move_priority)
    return (
        0 if candidate["existing_experiments"] == 0 and candidate["move"] == "underspecify" else 1,
        0 if candidate["existing_experiments"] > 0 and candidate["move"] == "perturb_assumption" else 1,
        0 if candidate.get("dominant_motif_bonus", 0) > 0 else candidate["active_count_for_conjecture"],
        -candidate.get("discovery_priority", 0),
        -candidate.get("dominant_motif_bonus", 0),
        -candidate.get("recent_signal_velocity", 0),
        -candidate.get("motif_reuse_count", 0),
        -candidate.get("signal_support", 0),
        -candidate.get("witness_support", 0),
        -candidate.get("assumption_boundary_support", 0),
        -candidate.get("campaign_priority", 0),
        -candidate.get("transfer_opportunity", 0),
        -candidate.get("reuse_potential", 0),
        -candidate.get("obstruction_targeting", 0),
        -candidate.get("semantic_novelty", 0),
        candidate["existing_experiments"],
        0 if candidate.get("targets_recurring_structure") else 1,
        candidate.get("no_signal_penalty", 0),
        -candidate.get("signal_priority", 0),
        stage_priority,
        0 if not candidate["duplicate_active_signature"] else 1,
        candidate.get("move_family", candidate["move"]),
        candidate["conjecture_id"],
    )


def _candidate_payload(brief, conjecture_id: str, project_id: str, existing_count: int, priority: int) -> Dict[str, Any]:
    return {
        "experiment_id": brief.experiment_id,
        "project_id": project_id,
        "conjecture_id": conjecture_id,
        "phase": brief.phase,
        "move": brief.move,
        "move_family": brief.move_family,
        "objective": brief.objective,
        "expected_signal": brief.expected_signal,
        "modification": brief.modification,
        "workspace_dir": brief.workspace_dir,
        "lean_file": brief.lean_file,
        "route_id": "",
        "existing_experiments": existing_count,
        "priority": priority,
        "rationale": brief.rationale,
        "candidate_metadata": brief.candidate_metadata,
    }


def _runtime_context(db: Database, project_id: str) -> Dict[str, Any]:
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    questions = db.list_discovery_questions(project_id)
    questions_by_conjecture: Dict[str, List[Any]] = {}
    for question in questions:
        cid = question.conjecture_id
        if cid not in questions_by_conjecture:
            questions_by_conjecture[cid] = []
        questions_by_conjecture[cid].append(question)
    charter = db.get_charter(project_id)
    return {
        "charter": charter,
        "conjectures": conjectures,
        "experiments": experiments,
        "questions_by_conjecture": questions_by_conjecture,
        "counts": _counts_by_conjecture(conjectures, experiments),
        "recurring": db.recurring_lemmas(),
        "recurring_subgoals": db.recurring_subgoals(project_id),
        "recurring_proof_traces": db.recurring_proof_traces(project_id),
    }


def _materialize_payload(
    project_id: str,
    workspace_root: str,
    conjecture,
    move_candidate: MoveCandidate,
    runtime: Dict[str, Any],
) -> Dict[str, Any]:
    brief = materialize_candidate(
        charter=runtime["charter"],
        conjecture=conjecture,
        workspace_root=workspace_root,
        experiments=runtime["experiments"],
        candidate=move_candidate,
        discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
    )
    payload = _candidate_payload(
        brief,
        conjecture.conjecture_id,
        project_id,
        runtime["counts"].get(conjecture.conjecture_id, 0),
        0,
    )
    payload["_frontier_candidate"] = {
        "conjecture_id": conjecture.conjecture_id,
        "move_candidate": move_candidate,
        "brief": brief,
    }
    return payload


def _strip_frontier_internal_fields(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for item in frontier:
        payload = dict(item)
        payload.pop("_frontier_candidate", None)
        cleaned.append(payload)
    return cleaned


def _annotate_runtime_fields(frontier: List[Dict[str, Any]], active: List[Dict[str, Any]], no_signal: Dict[tuple[str, str], int], active_counts: Dict[str, int]) -> None:
    active_signatures = {
        (
            item["conjecture_id"],
            item["move"],
            json.dumps(item["modification"], sort_keys=True),
        )
        for item in active
    }
    for payload in frontier:
        metadata = payload["candidate_metadata"]
        signature = (
            payload["conjecture_id"],
            payload["move"],
            json.dumps(payload["modification"], sort_keys=True),
        )
        payload.update(
            {
                "active_count_for_conjecture": active_counts.get(payload["conjecture_id"], 0),
                "duplicate_active_signature": signature in active_signatures,
                "targets_recurring_structure": payload["move_family"] in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"},
                "signal_priority": 2 if payload["move_family"] in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"} else 1 if payload["move"] == "reformulate" else 0,
                "no_signal_penalty": no_signal.get((payload["conjecture_id"], payload["move"]), 0) + metadata.get("no_signal_penalty", 0),
                "semantic_novelty": metadata.get("novelty_score", 0),
                "reuse_potential": metadata.get("reuse_potential", 0),
                "obstruction_targeting": metadata.get("obstruction_targeting", 0),
                "transfer_opportunity": metadata.get("transfer_score", 0),
                "campaign_priority": metadata.get("campaign_priority", 0),
                "motif_id": metadata.get("motif_id", ""),
                "motif_reuse_count": metadata.get("motif_reuse_count", 0),
                "signal_support": metadata.get("signal_support", 0),
                "blocker_support": metadata.get("blocker_support", 0),
                "witness_support": metadata.get("witness_support", 0),
                "assumption_boundary_support": metadata.get("assumption_boundary_support", 0),
                "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
            }
        )


def choose_next_experiment(db: Database, project_id: str, workspace_root: str):
    runtime = _runtime_context(db, project_id)
    frontier: List[Dict[str, Any]] = []
    generated_candidates: Dict[str, List[MoveCandidate]] = {}
    for conjecture in runtime["conjectures"]:
        move_candidates = generate_move_candidates(
            charter=runtime["charter"],
            conjecture=conjecture,
            experiments=runtime["experiments"],
            recurring_lemmas=runtime["recurring"],
            recurring_subgoals=runtime["recurring_subgoals"],
            recurring_proof_traces=runtime["recurring_proof_traces"],
            no_signal_branches=db.no_signal_branches(project_id),
            discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
            all_conjectures=runtime["conjectures"],
        )
        move_candidates = _manager_candidate_slice(conjecture, runtime["experiments"], move_candidates)
        generated_candidates[conjecture.conjecture_id] = move_candidates
        for move_candidate in move_candidates:
            frontier.append(_materialize_payload(project_id, workspace_root, conjecture, move_candidate, runtime))

    cleaned_frontier = _strip_frontier_internal_fields(frontier)
    for item in cleaned_frontier:
        item["route_id"] = ""
    for payload in frontier:
        payload["route_id"] = ""
    for item in cleaned_frontier:
        shutil.rmtree(item["workspace_dir"], ignore_errors=True)

    manager_prompt = build_manager_prompt(
        charter=runtime["charter"],
        state_summary=db.project_summary(project_id),
        frontier=cleaned_frontier,
    )
    chosen_payload = min(cleaned_frontier, key=_frontier_sort_key)
    chosen_conjecture = next(item for item in runtime["conjectures"] if item.conjecture_id == chosen_payload["conjecture_id"])
    chosen_move_candidate = next(item["_frontier_candidate"]["move_candidate"] for item in frontier if item["experiment_id"] == chosen_payload["experiment_id"])
    chosen = materialize_candidate(
        charter=runtime["charter"],
        conjecture=chosen_conjecture,
        workspace_root=workspace_root,
        experiments=runtime["experiments"],
        candidate=chosen_move_candidate,
        discovery_questions=runtime["questions_by_conjecture"].get(chosen_conjecture.conjecture_id, []),
    )
    chosen.route_id = ""
    return chosen, manager_prompt, cleaned_frontier


def generate_frontier(db: Database, project_id: str, workspace_root: str) -> List[Dict[str, object]]:
    runtime = _runtime_context(db, project_id)
    frontier: List[Dict[str, Any]] = []
    for conjecture in runtime["conjectures"]:
        move_candidates = generate_move_candidates(
            charter=runtime["charter"],
            conjecture=conjecture,
            experiments=runtime["experiments"],
            recurring_lemmas=runtime["recurring"],
            recurring_subgoals=runtime["recurring_subgoals"],
            recurring_proof_traces=runtime["recurring_proof_traces"],
            no_signal_branches=db.no_signal_branches(project_id),
            discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
            all_conjectures=runtime["conjectures"],
        )
        move_candidates = _manager_candidate_slice(conjecture, runtime["experiments"], move_candidates)
        for move_candidate in move_candidates:
            frontier.append(_materialize_payload(project_id, workspace_root, conjecture, move_candidate, runtime))

    active = db.list_active_experiments(project_id)
    active_counts = _counts_by_conjecture(runtime["conjectures"], active)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    _annotate_runtime_fields(frontier, active, no_signal, active_counts)
    cleaned = _strip_frontier_internal_fields(frontier)
    for item in cleaned:
        item["route_id"] = ""
    return sorted(cleaned, key=_frontier_sort_key)


# ============== Manager Policy Functions (merged from manager_policy.py) ==============


def _active_signature(experiment: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        experiment["conjecture_id"],
        experiment["move"],
        json.dumps(experiment["modification"], sort_keys=True),
    )


def build_manager_tick_prompt(
    charter,
    state_summary: Dict[str, Any],
    active_experiments: List[Dict[str, Any]],
    completed_experiments: List[Dict[str, Any]],
    frontier: List[Dict[str, Any]],
    recurring_lemmas: List[Dict[str, Any]],
    recurring_subgoals: List[Dict[str, Any]],
    assumption_sensitivity: List[Dict[str, Any]],
    capacity: Dict[str, int],
    route_context: Dict[str, Any] | None = None,
) -> str:
    route_section = ""
    if route_context:
        route_section = f"\nRoute selection context:\n{json.dumps(route_context, indent=2)}\n"
    return f"""
{build_project_constitution(charter)}

Campaign state summary:
{json.dumps(state_summary, indent=2)}

Active experiments:
{json.dumps(active_experiments, indent=2)}

Recently completed experiments:
{json.dumps(completed_experiments[:10], indent=2)}

Recurring lemmas:
{json.dumps(recurring_lemmas[:10], indent=2)}

Recurring subgoals:
{json.dumps(recurring_subgoals[:10], indent=2)}

Assumption sensitivity:
{json.dumps(assumption_sensitivity[:10], indent=2)}

Frontier candidates:
{json.dumps(frontier, indent=2)}

Capacity:
{json.dumps(capacity, indent=2)}
{route_section}

Return valid JSON with this exact shape:
{{
  "ranked_experiment_ids": ["candidate-id-1", "candidate-id-2"],
  "rationale": "one short paragraph"
}}

Hard constraints:
- rank only experiment ids that appear in the frontier candidates
- prefer candidates with explicit high-priority discovery questions
- preserve exploration, but allow deeper exploitation when a motif is clearly producing more reusable signal
- avoid duplicate active runs for the same conjecture, move, and modification
- favor information gain and reusability
- prefer candidates that attack recurring lemmas, recurring subgoals, recurring proof traces, or boundary maps from witnesses/missing assumptions
- de-prioritize branches with repeated no-signal outcomes
- prefer unexplored move types when otherwise similar
""".strip()


def candidate_score_breakdown(candidate: Dict[str, Any]) -> Dict[str, Any]:
    penalties = {
        "active_load": float(candidate.get("active_count_for_conjecture", 0) * 2.4),
        "existing_coverage": float(candidate.get("existing_experiments", 0) * 1.0),
        "no_signal_penalty": float(candidate.get("no_signal_penalty", 0) * 2.2),
        "duplicate_active_signature": 5.0 if candidate.get("duplicate_active_signature") else 0.0,
    }
    bonuses = {
        "discovery_priority": float(candidate.get("discovery_priority", 0) * 1.8),
        "campaign_priority": float(candidate.get("campaign_priority", 0) * 1.5),
        "signal_priority": float(candidate.get("signal_priority", 0) * 1.2),
        "transfer_opportunity": float(candidate.get("transfer_opportunity", 0) * 1.1),
        "reuse_potential": float(candidate.get("reuse_potential", 0) * 1.0),
        "obstruction_targeting": float(candidate.get("obstruction_targeting", 0) * 1.0),
        "semantic_novelty": float(candidate.get("semantic_novelty", 0) * 0.9),
        "targets_recurring_structure": 1.5 if candidate.get("targets_recurring_structure") else 0.0,
        "motif_reuse_count": float(candidate.get("motif_reuse_count", 0) * 0.8),
        "signal_support": float(candidate.get("signal_support", 0) * 0.7),
        "blocker_support": float(candidate.get("blocker_support", 0) * 0.45),
        "witness_support": float(candidate.get("witness_support", 0) * 0.6),
        "assumption_boundary_support": float(candidate.get("assumption_boundary_support", 0) * 0.6),
        "recent_signal_velocity": float(candidate.get("recent_signal_velocity", 0) * 1.3),
        "dominant_motif_bonus": float(candidate.get("dominant_motif_bonus", 0)),
    }
    move_bonus = max(0.0, float(5 - MOVE_PRIORITY.get(candidate["move"], 5)))
    bonuses["move_family_priority"] = move_bonus
    baseline_score = round(sum(bonuses.values()) - sum(penalties.values()), 4)
    score = round(baseline_score, 4)
    return {
        "policy_version": MANAGER_POLICY_VERSION,
        "bonuses": bonuses,
        "penalties": penalties,
        "baseline_score": baseline_score,
        "score": score,
    }


def _heuristic_rank(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(frontier, key=_frontier_sort_key)


def _score_rank(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        frontier,
        key=lambda candidate: (
            -candidate_score_breakdown(candidate)["score"],
            *_frontier_sort_key(candidate),
        ),
    )


def _diversify_candidates(ranked: List[Dict[str, Any]], max_count: int, exploration_floor: int) -> List[Dict[str, Any]]:
    if not ranked or max_count <= 0:
        return []
    unique_conjectures = {candidate["conjecture_id"] for candidate in ranked}
    chosen: List[Dict[str, Any]] = [ranked[0]]
    seen_conjectures: set[str] = {ranked[0]["conjecture_id"]}
    minimum_unique = min(max_count, max(1, exploration_floor))
    while len(chosen) < max_count:
        remaining = [candidate for candidate in ranked if candidate not in chosen]
        if not remaining:
            break
        if len(seen_conjectures) < minimum_unique:
            unseen = [candidate for candidate in remaining if candidate["conjecture_id"] not in seen_conjectures]
            if unseen:
                chosen.append(unseen[0])
                seen_conjectures.add(unseen[0]["conjecture_id"])
                continue
        unseen = [candidate for candidate in remaining if candidate["conjecture_id"] not in seen_conjectures]
        if unseen:
            chosen.append(unseen[0])
            seen_conjectures.add(unseen[0]["conjecture_id"])
            continue
        if len(seen_conjectures) >= len(unique_conjectures):
            if len(unique_conjectures) > 1:
                break
            if not any(item.get("dominant_motif_bonus", 0) > 0 for item in chosen):
                break
        chosen.append(remaining[0])
    return chosen[:max_count]


def _candidate_decision(candidate: Dict[str, Any], reason: str) -> CandidateDecision:
    breakdown = candidate_score_breakdown(candidate)
    return CandidateDecision(
        experiment_id=candidate["experiment_id"],
        conjecture_id=candidate["conjecture_id"],
        move=candidate["move"],
        reason=f"{reason}; move_family={candidate.get('move_family', candidate['move'])}; rationale={candidate.get('rationale', '')}".strip(),
        expected_signal=candidate["expected_signal"],
        modification=candidate["modification"],
        workspace_dir=candidate["workspace_dir"],
        lean_file=candidate["lean_file"],
        phase=candidate["phase"],
        policy_score=breakdown["score"],
        score_breakdown=breakdown,
    )


def build_candidate_audits(
    frontier: List[Dict[str, Any]],
    selected_ids: List[str],
    skipped: List[Dict[str, Any]],
    final_ranking: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    skipped_by_id = {item["experiment_id"]: item["reason"] for item in skipped if item.get("experiment_id")}
    ranked = _heuristic_rank(frontier)
    final_ranking = final_ranking or ranked
    final_positions = {item["experiment_id"]: index for index, item in enumerate(final_ranking, start=1)}
    audits: List[Dict[str, Any]] = []
    for index, candidate in enumerate(ranked, start=1):
        breakdown = candidate_score_breakdown(candidate)
        selection_reason = ""
        if candidate["experiment_id"] in selected_ids:
            selection_reason = "selected"
        elif candidate["experiment_id"] in skipped_by_id:
            selection_reason = skipped_by_id[candidate["experiment_id"]]
        audits.append(
            {
                "experiment_id": candidate["experiment_id"],
                "conjecture_id": candidate["conjecture_id"],
                "rank_position": index,
                "final_rank_position": final_positions.get(candidate["experiment_id"], index),
                "selected": candidate["experiment_id"] in selected_ids,
                "selection_reason": selection_reason,
                "policy_score": breakdown["score"],
                "score_breakdown": breakdown,
                "candidate": candidate,
            }
        )
    return audits


def choose_candidates_for_submission(
    db: Database,
    project_id: str,
    frontier: List[Dict[str, Any]],
    max_count: int,
    llm_manager_mode: str,
    route_id: str | None = None,
    route_context: Dict[str, Any] | None = None,
) -> PolicyDecision:
    filtered_frontier = frontier
    if route_id:
        filtered_frontier = [item for item in frontier if item.get("route_id") == route_id]
    if route_id and not filtered_frontier:
        filtered_frontier = frontier
    charter = db.get_charter(project_id)
    spec = db.get_campaign_spec(project_id)
    active = db.list_active_experiments(project_id)
    completed = db.list_completed_experiments(project_id, limit=10)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    sensitivity = db.assumption_sensitivity(project_id)
    summary = db.project_summary(project_id)
    capacity = {"requested_submissions": max_count, "current_active": len(active)}

    prompt = build_manager_tick_prompt(
        charter=charter,
        state_summary=summary,
        active_experiments=active,
        completed_experiments=completed,
        frontier=filtered_frontier,
        recurring_lemmas=recurring,
        recurring_subgoals=recurring_subgoals,
        assumption_sensitivity=sensitivity,
        capacity=capacity,
        route_context=route_context,
    )

    branch_prune_after_no_signal = spec.budget_policy.branch_prune_after_no_signal if spec is not None else 3
    duplicate_family_limit = spec.budget_policy.duplicate_frontier_family_limit if spec is not None else 2
    per_conjecture_active_cap = spec.budget_policy.per_conjecture_active_cap if spec is not None else 2
    per_motif_active_cap = spec.budget_policy.per_motif_active_cap if spec is not None else 2
    exploration_floor = spec.budget_policy.exploration_floor if spec is not None else 1
    active_conjecture_counts: Dict[str, int] = {}
    active_motif_counts: Dict[str, int] = {}
    for item in active:
        active_conjecture_counts[item["conjecture_id"]] = active_conjecture_counts.get(item["conjecture_id"], 0) + 1
        motif = item.get("candidate_metadata", {}).get("motif_id") if isinstance(item.get("candidate_metadata"), dict) else ""
        if motif:
            active_motif_counts[motif] = active_motif_counts.get(motif, 0) + 1
    motif_signal_map: Dict[str, float] = {}
    for candidate in filtered_frontier:
        motif_id = candidate.get("motif_id") or ""
        if not motif_id:
            continue
        score = (
            float(candidate.get("motif_reuse_count", 0))
            + float(candidate.get("recent_signal_velocity", 0)) * 1.4
            + float(candidate.get("signal_support", 0))
            + float(candidate.get("witness_support", 0)) * 0.5
            + float(candidate.get("assumption_boundary_support", 0)) * 0.5
        )
        motif_signal_map[motif_id] = max(motif_signal_map.get(motif_id, 0.0), score)
    dominant_motif_score = max(motif_signal_map.values(), default=0.0)
    eligible: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    family_counts: Dict[tuple[str, str], int] = {}
    for candidate in filtered_frontier:
        candidate = dict(candidate)
        motif_id = candidate.get("motif_id") or ""
        dominant_motif_bonus = 0.0
        if motif_id and motif_signal_map.get(motif_id, 0.0) >= dominant_motif_score and dominant_motif_score >= 3.5 and not candidate["duplicate_active_signature"]:
            dominant_motif_bonus = 2.5
        candidate["dominant_motif_bonus"] = dominant_motif_bonus
        if candidate["duplicate_active_signature"]:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "duplicate active experiment signature",
                }
            )
            continue
        if active_conjecture_counts.get(candidate["conjecture_id"], 0) >= per_conjecture_active_cap:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "conjecture active cap reached",
                }
            )
            continue
        if motif_id and active_motif_counts.get(motif_id, 0) >= per_motif_active_cap:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "motif active cap reached",
                }
            )
            continue
        if candidate.get("no_signal_penalty", 0) >= branch_prune_after_no_signal:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "pruned after repeated no-signal outcomes",
                }
            )
            continue
        family_key = (candidate["conjecture_id"], candidate.get("move_family", candidate["move"]))
        current = family_counts.get(family_key, 0)
        if current >= duplicate_family_limit:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "frontier throttled for duplicate move-family pressure",
                }
            )
            continue
        family_counts[family_key] = current + 1
        eligible.append(candidate)
    heuristic_ranked = _heuristic_rank(eligible)
    chosen = [
        _candidate_decision(candidate, "chosen by deterministic policy")
        for candidate in _diversify_candidates(heuristic_ranked, max_count, exploration_floor)
    ]
    selected_ids = [item.experiment_id for item in chosen]
    return PolicyDecision(
        chosen=chosen,
        skipped=skipped,
        policy_path="fallback",
        manager_prompt=prompt,
        raw_response="",
        rationale="Fallback policy ranked candidates by motif reuse, recent signal velocity, boundary evidence, and an exploration floor.",
        candidate_audits=build_candidate_audits(filtered_frontier, selected_ids, skipped, final_ranking=heuristic_ranked),
    )
