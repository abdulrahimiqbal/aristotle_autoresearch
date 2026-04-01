from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Tuple

from datetime import datetime
import uuid

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate
from research_orchestrator.llm_manager import build_campaign_brief, render_campaign_brief
from research_orchestrator.schema_versions import MANAGER_POLICY_VERSION
from research_orchestrator.move_registry import MoveCandidate
from research_orchestrator.prompts import build_manager_prompt, build_project_constitution
from research_orchestrator.types import ResearchDirective


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


def build_research_directive(
    db: Database,
    project_id: str,
    frontier: List[Dict[str, Any]],
    runtime: Dict[str, Any],
) -> ResearchDirective:
    """Build a research directive from the current state.

    Analyzes the frontier, active experiments, and campaign state to determine
    the optimal research strategy and focus areas for the next cycle.

    Consults search coverage to avoid redundant searches and use negative
    knowledge to inform strategy.
    """
    conjectures = runtime["conjectures"]
    experiments = runtime["experiments"]
    charter = runtime["charter"]

    # Get active experiment counts per conjecture
    active_counts = _counts_by_conjecture(conjectures, db.list_active_experiments(project_id))

    # Determine which conjectures need attention
    focus_conjecture_ids: List[str] = []
    for conjecture in conjectures:
        cid = conjecture.conjecture_id
        exp_count = runtime["counts"].get(cid, 0)
        active_count = active_counts.get(cid, 0)

        # Prioritize conjectures with fewer experiments and no active runs
        if exp_count < 3 and active_count == 0:
            focus_conjecture_ids.append(cid)

    # If no under-explored conjectures, focus on all of them
    if not focus_conjecture_ids:
        focus_conjecture_ids = [c.conjecture_id for c in conjectures]

    # Determine strategy based on frontier characteristics
    strategy = "explore"
    if frontier:
        # Check if we have high-signal candidates to exploit
        high_signal_count = sum(
            1 for f in frontier
            if f.get("recent_signal_velocity", 0) > 1.0 or f.get("dominant_motif_bonus", 0) > 0
        )
        if high_signal_count >= 2:
            strategy = "exploit"

        # Check for bridge opportunities (transfer opportunities)
        bridge_count = sum(1 for f in frontier if f.get("transfer_opportunity", 0) > 0.5)
        if bridge_count >= 2:
            strategy = "bridge"

        # Check for blocker resolution opportunities
        blocker_count = sum(1 for f in frontier if f.get("blocker_support", 0) > 0)
        if blocker_count >= 3 and high_signal_count < 2:
            strategy = "blocker_resolution"

    # Consult search coverage to inform strategy and avoid redundant work
    negative_knowledge = db.get_negative_knowledge(project_id)
    not_found_by_conjecture: Dict[str, int] = {}
    for nk in negative_knowledge:
        cid = nk.get("conjecture_id", "")
        if cid:
            not_found_by_conjecture[cid] = not_found_by_conjecture.get(cid, 0) + 1

    # Check what move families have already been searched for each conjecture
    searched_moves_by_conjecture: Dict[str, set[str]] = {}
    for cid in focus_conjecture_ids:
        coverage = db.get_search_coverage(project_id, conjecture_id=cid, search_type="move_family")
        searched_moves_by_conjecture[cid] = {c.get("search_key", "") for c in coverage}

    # Use negative knowledge to inform strategy
    total_not_found = len(negative_knowledge)
    if total_not_found >= 5 and strategy != "explore":
        # Many searches returned not_found, shift to exploration
        strategy = "explore"

    # Determine priority move families based on frontier and recurring structures
    priority_moves: List[str] = []

    # Always include moves that target recurring structures
    recurring = runtime["recurring"]
    recurring_subgoals = runtime["recurring_subgoals"]
    if recurring or recurring_subgoals:
        priority_moves.extend(["promote_lemma", "decompose_subgoal", "invariant_mining"])

    # Add strategy-specific moves
    if strategy == "explore":
        priority_moves.extend(["underspecify", "reformulate", "perturb_assumption"])
    elif strategy == "exploit":
        priority_moves.extend(["counterexample_mode", "boundary_map_from_witness"])
    elif strategy == "bridge":
        priority_moves.extend(["transfer_reformulation", "cross_conjecture_analogy"])
    elif strategy == "blocker_resolution":
        priority_moves.extend(["boundary_map_from_missing_assumption", "promote_subgoal"])

    # Filter out already-searched moves for each conjecture to avoid redundancy
    # Keep moves that haven't been searched yet for any focus conjecture
    filtered_priority_moves: List[str] = []
    for move in priority_moves:
        # Check if this move family has been searched for all focus conjectures
        all_searched = all(
            move in searched_moves_by_conjecture.get(cid, set())
            for cid in focus_conjecture_ids
        )
        if not all_searched:
            filtered_priority_moves.append(move)

    # If all priority moves have been searched, keep the original list (don't block progress)
    if filtered_priority_moves:
        priority_moves = filtered_priority_moves

    # Deduplicate while preserving order
    seen: set[str] = set()
    priority_moves = [m for m in priority_moves if not (m in seen or seen.add(m))]

    # Get campaign spec for budget limits
    spec = db.get_campaign_spec(project_id)
    max_parallel = 3
    exploration_budget = 5
    if spec is not None:
        max_parallel = spec.budget_policy.max_active_jobs
        exploration_budget = spec.budget_policy.max_total_experiments

    # Build rationale
    rationale_parts: List[str] = []
    rationale_parts.append(f"Strategy '{strategy}' selected based on")
    if strategy == "exploit":
        rationale_parts.append("high signal velocity candidates")
    elif strategy == "bridge":
        rationale_parts.append("transfer opportunities detected")
    elif strategy == "blocker_resolution":
        rationale_parts.append("blocker support signals present")
    else:
        rationale_parts.append("exploration phase needed")

    if recurring:
        rationale_parts.append(f"({len(recurring)} recurring structures)")
    if priority_moves:
        rationale_parts.append(f"Priority moves: {', '.join(priority_moves[:3])}")
    if total_not_found > 0:
        rationale_parts.append(f"({total_not_found} negative knowledge entries)")

    return ResearchDirective(
        project_id=project_id,
        directive_id=f"directive-{uuid.uuid4().hex[:12]}",
        created_at=datetime.utcnow().isoformat(),
        focus_conjecture_ids=focus_conjecture_ids,
        strategy=strategy,
        priority_moves=priority_moves,
        target_obligation_ids=[],  # Could be populated from obligation tracking
        max_parallel_experiments=max_parallel,
        exploration_budget=exploration_budget,
        constraints={
            "allowed_move_families": charter.allowed_moves if charter else [],
            "per_conjecture_active_cap": 2,
            "branch_prune_after_no_signal": 3,
        },
        rationale=" ".join(rationale_parts),
    )


def materialize_from_directive(
    db: Database,
    directive: ResearchDirective,
    workspace_root: str,
) -> List[Dict[str, Any]]:
    """Generate experiment candidates from a research directive.

    Takes a directive and materializes it into concrete experiment candidates,
    filtering and prioritizing based on the directive's strategy and constraints.
    """
    project_id = directive.project_id
    runtime = _runtime_context(db, project_id)

    candidates: List[Dict[str, Any]] = []

    # Generate candidates only for focus conjectures
    focus_conjectures = [
        c for c in runtime["conjectures"]
        if c.conjecture_id in directive.focus_conjecture_ids
    ]

    for conjecture in focus_conjectures:
        # Generate move candidates for this conjecture
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

        # Filter by priority moves if specified
        if directive.priority_moves:
            move_candidates = [
                mc for mc in move_candidates
                if mc.move_family in directive.priority_moves
                or mc.move in directive.priority_moves
            ]

        # Apply manager candidate slice logic
        move_candidates = _manager_candidate_slice(conjecture, runtime["experiments"], move_candidates)

        # Materialize each candidate
        for move_candidate in move_candidates:
            payload = _materialize_payload(
                project_id,
                workspace_root,
                conjecture,
                move_candidate,
                runtime,
            )
            candidates.append(payload)

    # Annotate with runtime fields for ranking
    active = db.list_active_experiments(project_id)
    active_counts = _counts_by_conjecture(runtime["conjectures"], active)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    _annotate_runtime_fields(candidates, active, no_signal, active_counts)

    # Clean up internal fields for return
    cleaned = _strip_frontier_internal_fields(candidates)

    # Apply directive constraints filtering
    max_candidates = min(directive.exploration_budget, directive.max_parallel_experiments)

    # Remove duplicates and sort by priority
    sorted_candidates = sorted(cleaned, key=_frontier_sort_key)

    # Return limited set based on budget
    return sorted_candidates[:max_candidates]


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
    """Choose the next experiment using the directive-based decision pattern.

    This function:
    1. Builds a research directive from current state
    2. Materializes experiment candidates from the directive
    3. Returns the single best experiment
    """
    # Step 1: Get runtime context and build frontier
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

    # Annotate frontier with runtime fields for directive building
    active = db.list_active_experiments(project_id)
    active_counts = _counts_by_conjecture(runtime["conjectures"], active)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    _annotate_runtime_fields(frontier, active, no_signal, active_counts)

    cleaned_frontier = _strip_frontier_internal_fields(frontier)
    for item in cleaned_frontier:
        item["route_id"] = ""
    for payload in frontier:
        payload["route_id"] = ""
    for item in cleaned_frontier:
        shutil.rmtree(item["workspace_dir"], ignore_errors=True)

    # Step 2: Build directive from current state
    directive = build_research_directive(db, project_id, cleaned_frontier, runtime)

    # Step 3: Materialize experiments from directive
    candidates = materialize_from_directive(db, directive, workspace_root)

    # Step 4: Return single best experiment
    manager_prompt = build_manager_prompt(
        charter=runtime["charter"],
        state_summary=db.project_summary(project_id),
        frontier=candidates,
    )

    if not candidates:
        # Fallback: use the original frontier if directive produces nothing
        candidates = cleaned_frontier

    chosen_payload = min(candidates, key=_frontier_sort_key)

    # Re-materialize the chosen experiment with fresh workspace
    chosen_conjecture = next(
        item for item in runtime["conjectures"]
        if item.conjecture_id == chosen_payload["conjecture_id"]
    )

    # Find the original move candidate from frontier for re-materialization
    chosen_move_candidate = None
    for item in frontier:
        if item["experiment_id"] == chosen_payload["experiment_id"]:
            chosen_move_candidate = item["_frontier_candidate"]["move_candidate"]
            break

    if chosen_move_candidate is None:
        # If not found in frontier, we need to regenerate
        move_candidates = generate_move_candidates(
            charter=runtime["charter"],
            conjecture=chosen_conjecture,
            experiments=runtime["experiments"],
            recurring_lemmas=runtime["recurring"],
            recurring_subgoals=runtime["recurring_subgoals"],
            recurring_proof_traces=runtime["recurring_proof_traces"],
            no_signal_branches=db.no_signal_branches(project_id),
            discovery_questions=runtime["questions_by_conjecture"].get(chosen_conjecture.conjecture_id, []),
            all_conjectures=runtime["conjectures"],
        )
        for mc in move_candidates:
            if mc.move == chosen_payload["move"]:
                chosen_move_candidate = mc
                break
        if chosen_move_candidate is None:
            chosen_move_candidate = move_candidates[0] if move_candidates else None

    if chosen_move_candidate is None:
        raise ValueError(f"Could not find move candidate for experiment {chosen_payload['experiment_id']}")

    chosen = materialize_candidate(
        charter=runtime["charter"],
        conjecture=chosen_conjecture,
        workspace_root=workspace_root,
        experiments=runtime["experiments"],
        candidate=chosen_move_candidate,
        discovery_questions=runtime["questions_by_conjecture"].get(chosen_conjecture.conjecture_id, []),
    )
    chosen.route_id = ""

    return chosen, manager_prompt, candidates


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

    # Build a strategic reason explaining why this candidate was selected
    strategic_factors = []

    # Key scoring factors that contributed to selection
    bonuses = breakdown.get("bonuses", {})
    if bonuses.get("signal_support", 0) > 0:
        strategic_factors.append(f"signal_support={bonuses['signal_support']:.2f}")
    if bonuses.get("transfer_opportunity", 0) > 0:
        strategic_factors.append(f"transfer={bonuses['transfer_opportunity']:.2f}")
    if bonuses.get("reuse_potential", 0) > 0:
        strategic_factors.append(f"reuse={bonuses['reuse_potential']:.2f}")
    if bonuses.get("semantic_novelty", 0) > 0:
        strategic_factors.append(f"novelty={bonuses['semantic_novelty']:.2f}")
    if bonuses.get("discovery_priority", 0) > 0:
        strategic_factors.append(f"discovery={bonuses['discovery_priority']:.2f}")
    if bonuses.get("recent_signal_velocity", 0) > 0:
        strategic_factors.append(f"velocity={bonuses['recent_signal_velocity']:.2f}")

    # Build the full reason
    full_reason_parts = [reason]
    full_reason_parts.append(f"move_family={candidate.get('move_family', candidate['move'])}")
    if strategic_factors:
        full_reason_parts.append(f"scoring_factors=[{', '.join(strategic_factors)}]")
    full_reason_parts.append(f"policy_score={breakdown['score']:.2f}")

    return CandidateDecision(
        experiment_id=candidate["experiment_id"],
        conjecture_id=candidate["conjecture_id"],
        move=candidate["move"],
        reason="; ".join(full_reason_parts),
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
    workspace_root: str | None = None,
) -> PolicyDecision:
    """Choose candidates for submission with optional directive-based generation.

    If workspace_root is provided and the frontier is empty or stale, this function
    will use directive-based generation to create fresh candidates.
    """
    filtered_frontier = frontier
    if route_id:
        filtered_frontier = [item for item in frontier if item.get("route_id") == route_id]
    if route_id and not filtered_frontier:
        filtered_frontier = frontier

    # Directive-based generation: if frontier is empty and workspace_root provided,
    # generate fresh candidates from a directive
    if not filtered_frontier and workspace_root:
        runtime = _runtime_context(db, project_id)
        # Build a minimal frontier for directive building
        directive = build_research_directive(db, project_id, [], runtime)
        # Override with more aggressive exploration since we have no candidates
        directive.strategy = "explore"
        directive.exploration_budget = max_count * 2
        directive.rationale += " (Emergency exploration mode: frontier was empty)"
        filtered_frontier = materialize_from_directive(db, directive, workspace_root)

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

    # Build strategic rationale explaining the selection decision
    rationale_parts = []

    # Overall strategy context
    if not frontier and workspace_root and filtered_frontier:
        rationale_parts.append(f"Generated {len(filtered_frontier)} fresh candidates via directive-based exploration.")

    # Selection summary
    if chosen:
        selected_moves = [c.move for c in chosen]
        selected_conjectures = list(set(c.conjecture_id for c in chosen))
        rationale_parts.append(
            f"Selected {len(chosen)} candidates: moves={', '.join(selected_moves[:3])}"
            + (f" (and {len(selected_moves) - 3} more)" if len(selected_moves) > 3 else "")
        )
        rationale_parts.append(f"Targeting {len(selected_conjectures)} conjecture(s)")

    # Strategic priorities from top candidates
    if heuristic_ranked:
        top_candidate = heuristic_ranked[0]
        top_factors = []
        if top_candidate.get("signal_support", 0) > 0:
            top_factors.append("strong signal support")
        if top_candidate.get("transfer_opportunity", 0) > 0.5:
            top_factors.append("transfer opportunity")
        if top_candidate.get("reuse_potential", 0) > 0:
            top_factors.append("reuse potential")
        if top_candidate.get("semantic_novelty", 0) > 0:
            top_factors.append("novelty")
        if top_candidate.get("discovery_priority", 0) > 0:
            top_factors.append("discovery priority")
        if top_factors:
            rationale_parts.append(f"Top candidate prioritized: {', '.join(top_factors)}")

    # Rejection summary
    if skipped:
        skip_reasons = {}
        for s in skipped:
            reason = s.get("reason", "unknown")
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        top_skips = sorted(skip_reasons.items(), key=lambda x: x[1], reverse=True)[:2]
        skip_summary = ", ".join([f"{count} {reason}" for reason, count in top_skips])
        rationale_parts.append(f"Skipped: {skip_summary}")

    # Exploration vs exploitation balance
    if chosen and heuristic_ranked:
        selected_ids_set = set(c.experiment_id for c in chosen)
        total_frontier = len(heuristic_ranked)
        selected_count = len(chosen)
        rationale_parts.append(
            f"Selection ratio: {selected_count}/{total_frontier} "
            f"({(selected_count/total_frontier*100):.0f}%) of frontier"
        )

    base_rationale = "; ".join(rationale_parts) if rationale_parts else "No candidates available for selection."

    return PolicyDecision(
        chosen=chosen,
        skipped=skipped,
        policy_path="fallback",
        manager_prompt=prompt,
        raw_response="",
        rationale=base_rationale,
        candidate_audits=build_candidate_audits(filtered_frontier, selected_ids, skipped, final_ranking=heuristic_ranked),
    )
