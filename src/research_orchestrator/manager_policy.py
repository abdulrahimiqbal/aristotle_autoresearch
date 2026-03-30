from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from research_orchestrator.db import Database
from research_orchestrator.prompts import build_project_constitution
from research_orchestrator.schema_versions import MANAGER_POLICY_VERSION


MOVE_PRIORITY = {
    "underspecify": 0,
    "perturb_assumption": 1,
    "reformulate": 2,
    "promote_lemma": 3,
    "counterexample_mode": 4,
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
) -> str:
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

Return valid JSON with this exact shape:
{{
  "ranked_experiment_ids": ["candidate-id-1", "candidate-id-2"],
  "rationale": "one short paragraph"
}}

Hard constraints:
- rank only experiment ids that appear in the frontier candidates
- prefer candidates with explicit high-priority discovery questions
- prefer cross-problem diversity before deepening one branch
- avoid duplicate active runs for the same conjecture, move, and modification
- favor information gain and reusability
- prefer candidates that attack recurring lemmas or recurring subgoals
- de-prioritize branches with repeated no-signal outcomes
- prefer unexplored move types when otherwise similar
""".strip()


def _heuristic_key(candidate: Dict[str, Any]) -> Tuple[int, int, int, int, str]:
    move_priority = MOVE_PRIORITY.get(candidate["move"], 99)
    if candidate["existing_experiments"] == 0:
        stage_priority = move_priority
    elif candidate.get("targets_recurring_structure"):
        stage_priority = -1
    else:
        stage_priority = move_priority
    return (
        candidate["active_count_for_conjecture"],
        -candidate.get("discovery_priority", 0),
        candidate["existing_experiments"],
        stage_priority,
        -candidate.get("transfer_opportunity", 0),
        -candidate.get("reuse_potential", 0),
        -candidate.get("obstruction_targeting", 0),
        -candidate.get("semantic_novelty", 0),
        0 if candidate.get("targets_recurring_structure") else 1,
        candidate.get("no_signal_penalty", 0),
        -candidate.get("signal_priority", 0),
        0 if not candidate["duplicate_active_signature"] else 1,
        candidate.get("move_family", candidate["move"]),
        candidate["conjecture_id"],
    )


def candidate_score_breakdown(candidate: Dict[str, Any]) -> Dict[str, Any]:
    penalties = {
        "active_load": float(candidate.get("active_count_for_conjecture", 0) * 3.0),
        "existing_coverage": float(candidate.get("existing_experiments", 0) * 1.4),
        "no_signal_penalty": float(candidate.get("no_signal_penalty", 0) * 2.2),
        "duplicate_active_signature": 5.0 if candidate.get("duplicate_active_signature") else 0.0,
    }
    bonuses = {
        "discovery_priority": float(candidate.get("discovery_priority", 0) * 1.8),
        "signal_priority": float(candidate.get("signal_priority", 0) * 1.2),
        "transfer_opportunity": float(candidate.get("transfer_opportunity", 0) * 1.1),
        "reuse_potential": float(candidate.get("reuse_potential", 0) * 1.0),
        "obstruction_targeting": float(candidate.get("obstruction_targeting", 0) * 1.0),
        "semantic_novelty": float(candidate.get("semantic_novelty", 0) * 0.9),
        "targets_recurring_structure": 1.5 if candidate.get("targets_recurring_structure") else 0.0,
    }
    move_bonus = max(0.0, float(5 - MOVE_PRIORITY.get(candidate["move"], 5)))
    bonuses["move_family_priority"] = move_bonus
    score = round(sum(bonuses.values()) - sum(penalties.values()), 4)
    return {
        "policy_version": MANAGER_POLICY_VERSION,
        "bonuses": bonuses,
        "penalties": penalties,
        "heuristic_key": list(_heuristic_key(candidate)),
        "score": score,
    }


def _heuristic_rank(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(frontier, key=_heuristic_key)


def _diversify_candidates(ranked: List[Dict[str, Any]], max_count: int) -> List[Dict[str, Any]]:
    chosen: List[Dict[str, Any]] = []
    seen_conjectures: set[str] = set()
    for candidate in ranked:
        if candidate["conjecture_id"] in seen_conjectures:
            continue
        chosen.append(candidate)
        seen_conjectures.add(candidate["conjecture_id"])
        if len(chosen) >= max_count:
            return chosen
    return chosen


def _llm_command() -> List[str]:
    raw = os.environ.get("RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND", "").strip()
    if not raw:
        return []
    return raw.split()


def _run_llm_manager(prompt: str) -> Tuple[str, bool]:
    command = _llm_command()
    if not command:
        return "", False
    completed = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stdout + ("\n" + completed.stderr if completed.stderr else ""), False
    return completed.stdout.strip(), True


def _validate_llm_response(
    raw_response: str,
    frontier: List[Dict[str, Any]],
    max_count: int,
) -> Tuple[bool, List[str], str]:
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError:
        return False, [], ""
    if not isinstance(payload, dict):
        return False, [], ""
    ranked_ids = payload.get("ranked_experiment_ids")
    rationale = payload.get("rationale", "")
    if not isinstance(ranked_ids, list) or not all(isinstance(item, str) for item in ranked_ids):
        return False, [], ""
    known = {candidate["experiment_id"]: candidate for candidate in frontier}
    deduped: List[str] = []
    seen: set[str] = set()
    for experiment_id in ranked_ids:
        if experiment_id in seen:
            continue
        if experiment_id not in known:
            return False, [], ""
        candidate = known[experiment_id]
        if candidate["duplicate_active_signature"]:
            return False, [], ""
        seen.add(experiment_id)
        deduped.append(experiment_id)
        if len(deduped) >= max_count:
            break
    return True, deduped, rationale if isinstance(rationale, str) else ""


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
) -> List[Dict[str, Any]]:
    skipped_by_id = {item["experiment_id"]: item["reason"] for item in skipped if item.get("experiment_id")}
    ranked = _heuristic_rank(frontier)
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
) -> PolicyDecision:
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
        frontier=frontier,
        recurring_lemmas=recurring,
        recurring_subgoals=recurring_subgoals,
        assumption_sensitivity=sensitivity,
        capacity=capacity,
    )

    branch_prune_after_no_signal = spec.budget_policy.branch_prune_after_no_signal if spec is not None else 3
    duplicate_family_limit = spec.budget_policy.duplicate_frontier_family_limit if spec is not None else 2
    eligible: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    family_counts: Dict[tuple[str, str], int] = {}
    for candidate in frontier:
        if candidate["duplicate_active_signature"]:
            skipped.append(
                {
                    "experiment_id": candidate["experiment_id"],
                    "conjecture_id": candidate["conjecture_id"],
                    "reason": "duplicate active experiment signature",
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

    should_try_llm = llm_manager_mode in {"on", "auto"}
    if should_try_llm:
        raw_response, success = _run_llm_manager(prompt)
        if success:
            valid, ranked_ids, rationale = _validate_llm_response(raw_response, frontier, max_count)
            if valid:
                mapping = {candidate["experiment_id"]: candidate for candidate in frontier}
                chosen = [
                    _candidate_decision(mapping[experiment_id], "chosen by llm-ranked policy")
                    for experiment_id in ranked_ids
                ]
                return PolicyDecision(
                    chosen=chosen,
                    skipped=skipped,
                    policy_path="llm",
                    manager_prompt=prompt,
                    raw_response=raw_response,
                    rationale=rationale or "LLM-ranked candidate ordering accepted by validator.",
                    candidate_audits=build_candidate_audits(frontier, ranked_ids, skipped),
                )
        if llm_manager_mode == "on":
            skipped.append({"experiment_id": "", "conjecture_id": "", "reason": "llm output invalid; falling back to heuristic policy"})

    chosen = [
        _candidate_decision(candidate, "chosen by deterministic fallback policy")
        for candidate in _diversify_candidates(heuristic_ranked, max_count)
    ]
    return PolicyDecision(
        chosen=chosen,
        skipped=skipped,
        policy_path="fallback",
        manager_prompt=prompt,
        raw_response="",
        rationale="Fallback policy ranked candidates by diversity, existing coverage, and move priority.",
        candidate_audits=build_candidate_audits(frontier, [item.experiment_id for item in chosen], skipped),
    )
