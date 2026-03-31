from __future__ import annotations

import json
import shutil
from typing import Dict, List

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate, select_discovery_question
from research_orchestrator.prompts import build_manager_prompt

MOVE_PRIORITY = {
    "underspecify": 0,
    "perturb_assumption": 1,
    "promote_lemma": 2,
    "promote_subgoal": 3,
    "promote_trace": 4,
    "reformulate": 5,
    "boundary_map_from_witness": 6,
    "boundary_map_from_missing_assumption": 7,
    "counterexample_mode": 8,
}


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


def _manager_candidate_slice(conjecture, experiments, move_candidates):
    conjecture_experiments = [item for item in experiments if item["conjecture_id"] == conjecture.conjecture_id]
    effective_moves = {
        item["move"]
        for item in conjecture_experiments
        if item.get("proof_outcome") not in {"unknown", "auth_failure", "infra_failure", "malformed"}
        or (item.get("new_signal_count") or 0) > 0
    }
    tested_assumptions = {
        item["modification"].get("assumption")
        for item in conjecture_experiments
        if item["move"] == "perturb_assumption" and item.get("modification", {}).get("assumption")
    }
    if not conjecture_experiments and not _has_seeded_structure(conjecture):
        initial = [candidate for candidate in move_candidates if candidate.legacy_move == "underspecify"]
        return initial[:1] if initial else move_candidates
    if "underspecify" in effective_moves and not tested_assumptions:
        high_value_nonperturb = [
            candidate
            for candidate in move_candidates
            if candidate.legacy_move != "perturb_assumption"
            and candidate.transfer_score > 0
        ]
        if high_value_nonperturb:
            return move_candidates
        perturb = [candidate for candidate in move_candidates if candidate.legacy_move == "perturb_assumption"]
        if perturb:
            return perturb
    return move_candidates


def _candidate_payload(candidate, conjecture_id, project_id, existing_experiments, discovery_priority):
    metadata = candidate.candidate_metadata
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
        "candidate_metadata": metadata,
        "discovery_question_id": candidate.discovery_question_id,
        "discovery_question": candidate.discovery_question,
        "discovery_priority": discovery_priority,
        "motif_id": metadata.get("motif_id", ""),
        "motif_signature": metadata.get("motif_signature", ""),
        "motif_reuse_count": metadata.get("motif_reuse_count", 0),
        "signal_support": metadata.get("signal_support", 0),
        "blocker_support": metadata.get("blocker_support", 0),
        "witness_support": metadata.get("witness_support", 0),
        "assumption_boundary_support": metadata.get("assumption_boundary_support", 0),
        "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
    }


def _frontier_sort_key(item: Dict[str, object]):
    metadata = item.get("candidate_metadata", {})
    return (
        item.get("existing_experiments", 0),
        -item.get("discovery_priority", 0),
        -item.get("recent_signal_velocity", 0),
        -item.get("motif_reuse_count", 0),
        MOVE_PRIORITY.get(item.get("move", ""), 99),
        -metadata.get("campaign_priority", 0),
        -metadata.get("transfer_score", 0),
        -metadata.get("reuse_potential", 0),
        -metadata.get("obstruction_targeting", 0),
        -metadata.get("novelty_score", 0),
        -item.get("signal_support", 0),
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
    blocker_signals = [item["blocker_type"] for item in db.recurring_blockers_by_move(project_id)]
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
        move_candidates = _manager_candidate_slice(conjecture, experiments, move_candidates)
        generated_candidates[conjecture.conjecture_id] = move_candidates
        for move_candidate in move_candidates:
            selected_question = select_discovery_question(
                conjecture=conjecture,
                discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
                recurring_lemmas=recurring,
                recurring_subgoals=recurring_subgoals,
                recurring_proof_traces=recurring_proof_traces,
                blocker_signals=blocker_signals,
            )
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
                    (selected_question or {}).get("priority", 0),
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
    blocker_signals = [item["blocker_type"] for item in db.recurring_blockers_by_move(project_id)]
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
        move_candidates = _manager_candidate_slice(conjecture, experiments, move_candidates)
        for move_candidate in move_candidates:
            selected_question = select_discovery_question(
                conjecture=conjecture,
                discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
                recurring_lemmas=recurring,
                recurring_subgoals=recurring_subgoals,
                recurring_proof_traces=recurring_proof_traces,
                blocker_signals=blocker_signals,
            )
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
                (selected_question or {}).get("priority", 0),
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
                    "campaign_priority": brief.candidate_metadata.get("campaign_priority", 0),
                    "motif_id": brief.candidate_metadata.get("motif_id", ""),
                    "motif_reuse_count": brief.candidate_metadata.get("motif_reuse_count", 0),
                    "signal_support": brief.candidate_metadata.get("signal_support", 0),
                    "blocker_support": brief.candidate_metadata.get("blocker_support", 0),
                    "witness_support": brief.candidate_metadata.get("witness_support", 0),
                    "assumption_boundary_support": brief.candidate_metadata.get("assumption_boundary_support", 0),
                    "recent_signal_velocity": brief.candidate_metadata.get("recent_signal_velocity", 0),
                }
            )
            frontier.append(payload)
    return sorted(frontier, key=_frontier_sort_key)
