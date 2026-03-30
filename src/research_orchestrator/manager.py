from __future__ import annotations

from typing import Dict, List

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import materialize_experiment
from research_orchestrator.prompts import build_manager_prompt


def choose_next_experiment(db: Database, project_id: str, workspace_root: str):
    charter = db.get_charter(project_id)
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    questions_by_conjecture = {}
    for question in open_questions:
        questions_by_conjecture.setdefault(question["conjecture_id"], []).append(question)
    counts_by_conjecture = {
        conjecture.conjecture_id: 0 for conjecture in conjectures
    }
    for experiment in experiments:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in counts_by_conjecture:
            counts_by_conjecture[conjecture_id] += 1

    frontier = []
    for conjecture in conjectures:
        candidate = materialize_experiment(
            charter=charter,
            conjecture=conjecture,
            workspace_root=workspace_root,
            experiments=experiments,
            recurring_lemmas=recurring,
            recurring_subgoals=recurring_subgoals,
            discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
        )
        frontier.append({
            "project_id": project_id,
            "conjecture_id": conjecture.conjecture_id,
            "existing_experiments": counts_by_conjecture.get(conjecture.conjecture_id, 0),
            "phase": candidate.phase,
            "move": candidate.move,
            "objective": candidate.objective,
            "expected_signal": candidate.expected_signal,
            "modification": candidate.modification,
            "discovery_question_id": candidate.discovery_question_id,
            "discovery_question": candidate.discovery_question,
            "discovery_priority": (questions_by_conjecture.get(conjecture.conjecture_id) or [{}])[0].get("priority", 0),
        })
        # Only use this as a dry-run frontier preview; delete the temp candidate workspace.
        import shutil
        shutil.rmtree(candidate.workspace_dir, ignore_errors=True)

    manager_prompt = build_manager_prompt(
        charter=charter,
        state_summary=db.project_summary(project_id),
        frontier=frontier,
    )

    # Heuristic policy: balance attention across the theorem family by picking
    # the least-explored conjecture first, then falling back to conjecture id.
    chosen_conjecture = min(
        conjectures,
        key=lambda conjecture: (
            counts_by_conjecture.get(conjecture.conjecture_id, 0),
            conjecture.conjecture_id,
        ),
    )
    chosen = materialize_experiment(
        charter=charter,
        conjecture=chosen_conjecture,
        workspace_root=workspace_root,
        experiments=experiments,
        recurring_lemmas=recurring,
        recurring_subgoals=recurring_subgoals,
        discovery_questions=questions_by_conjecture.get(chosen_conjecture.conjecture_id, []),
    )
    return chosen, manager_prompt, frontier


def generate_frontier(db: Database, project_id: str, workspace_root: str) -> List[Dict[str, object]]:
    charter = db.get_charter(project_id)
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    questions_by_conjecture = {}
    for question in open_questions:
        questions_by_conjecture.setdefault(question["conjecture_id"], []).append(question)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    active = db.list_active_experiments(project_id)
    counts_by_conjecture = {
        conjecture.conjecture_id: 0 for conjecture in conjectures
    }
    active_by_conjecture = {
        conjecture.conjecture_id: 0 for conjecture in conjectures
    }
    active_signatures = {
        (
            item["conjecture_id"],
            item["move"],
            __import__("json").dumps(item["modification"], sort_keys=True),
        )
        for item in active
    }
    for experiment in experiments:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in counts_by_conjecture:
            counts_by_conjecture[conjecture_id] += 1
    for experiment in active:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in active_by_conjecture:
            active_by_conjecture[conjecture_id] += 1

    frontier = []
    for conjecture in conjectures:
        candidate = materialize_experiment(
            charter=charter,
            conjecture=conjecture,
            workspace_root=workspace_root,
            experiments=experiments,
            recurring_lemmas=recurring,
            recurring_subgoals=recurring_subgoals,
            discovery_questions=questions_by_conjecture.get(conjecture.conjecture_id, []),
        )
        signature = (
            conjecture.conjecture_id,
            candidate.move,
            __import__("json").dumps(candidate.modification, sort_keys=True),
        )
        targets_recurring_structure = (
            candidate.move == "promote_lemma"
            or bool(recurring_subgoals and candidate.move == "counterexample_mode")
        )
        signal_priority = 2 if candidate.move == "promote_lemma" else 1 if candidate.move == "reformulate" else 0
        frontier.append({
            "experiment_id": candidate.experiment_id,
            "project_id": project_id,
            "conjecture_id": conjecture.conjecture_id,
            "existing_experiments": counts_by_conjecture.get(conjecture.conjecture_id, 0),
            "active_count_for_conjecture": active_by_conjecture.get(conjecture.conjecture_id, 0),
            "phase": candidate.phase,
            "move": candidate.move,
            "objective": candidate.objective,
            "expected_signal": candidate.expected_signal,
            "modification": candidate.modification,
            "workspace_dir": candidate.workspace_dir,
            "lean_file": candidate.lean_file,
            "discovery_question_id": candidate.discovery_question_id,
            "discovery_question": candidate.discovery_question,
            "discovery_priority": (questions_by_conjecture.get(conjecture.conjecture_id) or [{}])[0].get("priority", 0),
            "duplicate_active_signature": signature in active_signatures,
            "targets_recurring_structure": targets_recurring_structure,
            "signal_priority": signal_priority,
            "no_signal_penalty": no_signal.get((conjecture.conjecture_id, candidate.move), 0),
        })
    return frontier
