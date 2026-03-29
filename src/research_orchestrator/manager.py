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

    frontier = []
    for conjecture in conjectures:
        candidate = materialize_experiment(
            charter=charter,
            conjecture=conjecture,
            workspace_root=workspace_root,
            experiments=experiments,
            recurring_lemmas=recurring,
        )
        frontier.append({
            "project_id": project_id,
            "conjecture_id": conjecture.conjecture_id,
            "phase": candidate.phase,
            "move": candidate.move,
            "objective": candidate.objective,
            "expected_signal": candidate.expected_signal,
            "modification": candidate.modification,
        })
        # Only use this as a dry-run frontier preview; delete the temp candidate workspace.
        import shutil
        shutil.rmtree(candidate.workspace_dir, ignore_errors=True)

    manager_prompt = build_manager_prompt(
        charter=charter,
        state_summary=db.project_summary(project_id),
        frontier=frontier,
    )

    # Heuristic policy: choose the first conjecture's next candidate.
    chosen = materialize_experiment(
        charter=charter,
        conjecture=conjectures[0],
        workspace_root=workspace_root,
        experiments=experiments,
        recurring_lemmas=recurring,
    )
    return chosen, manager_prompt, frontier
