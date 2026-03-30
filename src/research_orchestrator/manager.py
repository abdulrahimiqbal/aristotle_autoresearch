from __future__ import annotations

import json
import shutil
from typing import Dict, List

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate
from research_orchestrator.prompts import build_manager_prompt

MOVE_PRIORITY = {
    "underspecify": 0,
    "perturb_assumption": 1,
    "promote_lemma": 2,
    "reformulate": 3,
    "counterexample_mode": 4,
}


def _counts_by_conjecture(conjectures, experiments):
    counts = {conjecture.conjecture_id: 0 for conjecture in conjectures}
    for experiment in experiments:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in counts:
            counts[conjecture_id] += 1
    return counts


def _candidate_payload(candidate, conjecture_id, project_id, existing_experiments, discovery_priority):
    return {
        "experiment_id": candidate.experiment_id,
        "project_id": project_id,
        "conjecture_id": conjecture_id,
        "existing_experiments": existing_experiments,
        "phase": candidate.phase,
        "move": candidate.move,
        "move_family": candidate.move_family or candidate.move,
        "theorem_family_id": candidate.theorem_family_id,
        "move_title": candidate.move_title or candidate.move_family or candidate.move,
        "objective": candidate.objective,
        "expected_signal": candidate.expected_signal,
        "modification": candidate.modification,
        "workspace_dir": candidate.workspace_dir,
        "lean_file": candidate.lean_file,
        "rationale": candidate.rationale,
        "candidate_metadata": candidate.candidate_metadata,
        "discovery_question_id": candidate.discovery_question_id,
        "discovery_question": candidate.discovery_question,
        "discovery_priority": discovery_priority,
    }


def _frontier_sort_key(item: Dict[str, object]):
    metadata = item.get("candidate_metadata", {})
    return (
        item.get("existing_experiments", 0),
        -item.get("discovery_priority", 0),
        MOVE_PRIORITY.get(item.get("move", ""), 99),
        -metadata.get("transfer_score", 0),
        -metadata.get("reuse_potential", 0),
        -metadata.get("obstruction_targeting", 0),
        -metadata.get("novelty_score", 0),
        item.get("conjecture_id", ""),
        item.get("move_family", ""),
    )


def choose_next_experiment(db: Database, project_id: str, workspace_root: str):
    charter = db.get_charter(project_id)
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    recurring_proof_traces = db.recurring_proof_traces(project_id)
    no_signal_branches = db.no_signal_branches(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    questions_by_conjecture = {}
    for question in open_questions:
        questions_by_conjecture.setdefault(question["conjecture_id"], []).append(question)
    counts = _counts_by_conjecture(conjectures, experiments)

    frontier = []
    generated_candidates = {}
    for conjecture in conjectures:
        move_candidates = generate_move_candidates(
            charter=charter,
            conjecture=conjecture,
            experiments=experiments,
            recurring_lemmas=recurring,
            recurring_subgoals=recurring_subgoals,
            recurring_proof_traces=recurring_proof_traces,
            no_signal_branches=no_signal_branches,
            discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
            all_conjectures=conjectures,
        )
        generated_candidates[conjecture.conjecture_id] = move_candidates
        for move_candidate in move_candidates:
            brief = materialize_candidate(
                charter=charter,
                conjecture=conjecture,
                workspace_root=workspace_root,
                experiments=experiments,
                candidate=move_candidate,
                discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
            )
            frontier.append(
                _candidate_payload(
                    brief,
                    conjecture.conjecture_id,
                    project_id,
                    counts.get(conjecture.conjecture_id, 0),
                    (questions_by_conjecture.get(conjecture.conjecture_id) or [{}])[0].get("priority", 0),
                )
            )
            shutil.rmtree(brief.workspace_dir, ignore_errors=True)

    manager_prompt = build_manager_prompt(
        charter=charter,
        state_summary=db.project_summary(project_id),
        frontier=frontier,
    )
    chosen_payload = min(frontier, key=_frontier_sort_key)
    chosen_conjecture = next(item for item in conjectures if item.conjecture_id == chosen_payload["conjecture_id"])
    chosen_move_candidate = next(
        item
        for item in generated_candidates[chosen_conjecture.conjecture_id]
        if item.move_family == chosen_payload["move_family"]
        and item.legacy_move == chosen_payload["move"]
        and item.parameters == chosen_payload["modification"]
    )
    chosen = materialize_candidate(
        charter=charter,
        conjecture=chosen_conjecture,
        workspace_root=workspace_root,
        experiments=experiments,
        candidate=chosen_move_candidate,
        discovery_questions=questions_by_conjecture.get(chosen_conjecture.conjecture_id, []),
    )
    return chosen, manager_prompt, frontier


def generate_frontier(db: Database, project_id: str, workspace_root: str) -> List[Dict[str, object]]:
    charter = db.get_charter(project_id)
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    recurring_proof_traces = db.recurring_proof_traces(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    questions_by_conjecture = {}
    for question in open_questions:
        questions_by_conjecture.setdefault(question["conjecture_id"], []).append(question)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    active = db.list_active_experiments(project_id)
    counts = _counts_by_conjecture(conjectures, experiments)
    active_counts = _counts_by_conjecture(conjectures, active)
    active_signatures = {
        (
            item["conjecture_id"],
            item["move"],
            json.dumps(item["modification"], sort_keys=True),
        )
        for item in active
    }

    frontier = []
    for conjecture in conjectures:
        move_candidates = generate_move_candidates(
            charter=charter,
            conjecture=conjecture,
            experiments=experiments,
            recurring_lemmas=recurring,
            recurring_subgoals=recurring_subgoals,
            recurring_proof_traces=recurring_proof_traces,
            no_signal_branches=list(db.no_signal_branches(project_id)),
            discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
            all_conjectures=conjectures,
        )
        for move_candidate in move_candidates:
            brief = materialize_candidate(
                charter=charter,
                conjecture=conjecture,
                workspace_root=workspace_root,
                experiments=experiments,
                candidate=move_candidate,
                discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
            )
            payload = _candidate_payload(
                brief,
                conjecture.conjecture_id,
                project_id,
                counts.get(conjecture.conjecture_id, 0),
                (questions_by_conjecture.get(conjecture.conjecture_id) or [{}])[0].get("priority", 0),
            )
            signature = (
                conjecture.conjecture_id,
                brief.move,
                json.dumps(brief.modification, sort_keys=True),
            )
            payload.update(
                {
                    "active_count_for_conjecture": active_counts.get(conjecture.conjecture_id, 0),
                    "duplicate_active_signature": signature in active_signatures,
                    "targets_recurring_structure": brief.move_family in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"},
                    "signal_priority": 2 if brief.move_family in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"} else 1 if brief.move == "reformulate" else 0,
                    "no_signal_penalty": no_signal.get((conjecture.conjecture_id, brief.move), 0) + brief.candidate_metadata.get("no_signal_penalty", 0),
                    "semantic_novelty": brief.candidate_metadata.get("novelty_score", 0),
                    "reuse_potential": brief.candidate_metadata.get("reuse_potential", 0),
                    "obstruction_targeting": brief.candidate_metadata.get("obstruction_targeting", 0),
                    "transfer_opportunity": brief.candidate_metadata.get("transfer_score", 0),
                }
            )
            frontier.append(payload)
    return sorted(frontier, key=_frontier_sort_key)
