from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from research_orchestrator.db import Database
from research_orchestrator.prompts import build_project_constitution


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


@dataclass
class PolicyDecision:
    chosen: List[CandidateDecision] = field(default_factory=list)
    skipped: List[Dict[str, Any]] = field(default_factory=list)
    policy_path: str = "fallback"
    manager_prompt: str = ""
    raw_response: str = ""
    rationale: str = ""


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
    return (
        candidate["active_count_for_conjecture"],
        -candidate.get("discovery_priority", 0),
        0 if candidate.get("targets_recurring_structure") else 1,
        candidate.get("no_signal_penalty", 0),
        -candidate.get("signal_priority", 0),
        candidate["existing_experiments"],
        0 if not candidate["duplicate_active_signature"] else 1,
        MOVE_PRIORITY.get(candidate["move"], 99),
        candidate["conjecture_id"],
    )


def _heuristic_rank(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(frontier, key=_heuristic_key)


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
    return CandidateDecision(
        experiment_id=candidate["experiment_id"],
        conjecture_id=candidate["conjecture_id"],
        move=candidate["move"],
        reason=reason,
        expected_signal=candidate["expected_signal"],
        modification=candidate["modification"],
        workspace_dir=candidate["workspace_dir"],
        lean_file=candidate["lean_file"],
        phase=candidate["phase"],
    )


def choose_candidates_for_submission(
    db: Database,
    project_id: str,
    frontier: List[Dict[str, Any]],
    max_count: int,
    llm_manager_mode: str,
) -> PolicyDecision:
    charter = db.get_charter(project_id)
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

    eligible = [candidate for candidate in frontier if not candidate["duplicate_active_signature"]]
    heuristic_ranked = _heuristic_rank(eligible)
    skipped = [
        {
            "experiment_id": candidate["experiment_id"],
            "conjecture_id": candidate["conjecture_id"],
            "reason": "duplicate active experiment signature",
        }
        for candidate in frontier
        if candidate["duplicate_active_signature"]
    ]

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
                )
        if llm_manager_mode == "on":
            skipped.append({"experiment_id": "", "conjecture_id": "", "reason": "llm output invalid; falling back to heuristic policy"})

    chosen = [
        _candidate_decision(candidate, "chosen by deterministic fallback policy")
        for candidate in heuristic_ranked[:max_count]
    ]
    return PolicyDecision(
        chosen=chosen,
        skipped=skipped,
        policy_path="fallback",
        manager_prompt=prompt,
        raw_response="",
        rationale="Fallback policy ranked candidates by diversity, existing coverage, and move priority.",
    )
