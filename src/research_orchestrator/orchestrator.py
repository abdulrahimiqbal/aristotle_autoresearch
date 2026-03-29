from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from research_orchestrator.db import Database
from research_orchestrator.evaluator import score_result
from research_orchestrator.manager import choose_next_experiment
from research_orchestrator.prompt_linter import lint_manager_prompt, lint_worker_prompt
from research_orchestrator.prompts import build_worker_prompt
from research_orchestrator.provider_registry import get_provider


def run_one_cycle(db: Database, project_id: str, provider_name: str, workspace_root: str) -> Dict[str, object]:
    workspace_root = str(Path(workspace_root).resolve())
    Path(workspace_root).mkdir(parents=True, exist_ok=True)

    brief, manager_prompt, frontier = choose_next_experiment(db, project_id, workspace_root)
    db.save_experiment_plan(brief.__dict__)

    charter = db.get_charter(project_id)
    conjecture = db.get_conjecture(brief.conjecture_id)
    recurring = db.recurring_lemmas()
    sensitivity = db.assumption_sensitivity(project_id)
    worker_prompt = build_worker_prompt(charter, conjecture, brief, recurring, sensitivity)

    manager_lint = lint_manager_prompt(manager_prompt)
    worker_lint = lint_worker_prompt(worker_prompt)

    provider = get_provider(provider_name)
    result = provider.run(
        charter=charter,
        conjecture=conjecture,
        brief=brief,
        worker_prompt=worker_prompt,
    )
    evaluation = score_result(charter, result)

    db.complete_experiment(
        experiment_id=brief.experiment_id,
        provider=provider.name,
        result=result,
        evaluation=evaluation.__dict__,
    )
    db.save_lemma_occurrences(
        experiment_id=brief.experiment_id,
        conjecture_id=brief.conjecture_id,
        generated=result.generated_lemmas,
        proved=result.proved_lemmas,
    )

    if brief.move == "perturb_assumption":
        assumption = brief.modification.get("assumption")
        if assumption:
            sensitivity_score = 1.0 if result.blocker_type == "structural" else 0.45 if result.blocker_type == "search" else 0.2
            db.record_assumption_observation(
                project_id=project_id,
                conjecture_id=brief.conjecture_id,
                experiment_id=brief.experiment_id,
                assumption_name=assumption,
                outcome=result.status,
                sensitivity_score=sensitivity_score,
            )

    memo = {
        "experiment_id": brief.experiment_id,
        "project_id": project_id,
        "move": brief.move,
        "phase": brief.phase,
        "status": result.status,
        "blocker_type": result.blocker_type,
        "manager_prompt_lint_ok": manager_lint.ok,
        "worker_prompt_lint_ok": worker_lint.ok,
        "evaluation_total": evaluation.total,
    }
    db.add_note(
        project_id=project_id,
        experiment_id=brief.experiment_id,
        note_markdown=json.dumps(memo, indent=2),
        structured=memo,
    )

    return {
        "brief": brief,
        "manager_prompt": manager_prompt,
        "worker_prompt": worker_prompt,
        "result": result,
        "evaluation": evaluation,
        "frontier": frontier,
        "manager_prompt_lint": manager_lint,
        "worker_prompt_lint": worker_lint,
    }
