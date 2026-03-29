from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from research_orchestrator.db import Database
from research_orchestrator.evaluator import score_result
from research_orchestrator.manager import choose_next_experiment, generate_frontier
from research_orchestrator.manager_policy import choose_candidates_for_submission
from research_orchestrator.prompt_linter import lint_manager_prompt, lint_worker_prompt
from research_orchestrator.prompts import build_worker_prompt
from research_orchestrator.provider_registry import get_provider
from research_orchestrator.types import ExperimentBrief


def _prepare_cycle(db: Database, project_id: str, workspace_root: str) -> Dict[str, object]:
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
    return {
        "brief": brief,
        "charter": charter,
        "conjecture": conjecture,
        "manager_prompt": manager_prompt,
        "worker_prompt": worker_prompt,
        "frontier": frontier,
        "manager_prompt_lint": manager_lint,
        "worker_prompt_lint": worker_lint,
    }


def _prepare_cycle_from_candidate(db: Database, project_id: str, candidate: Dict[str, object]) -> Dict[str, object]:
    brief = ExperimentBrief(
        experiment_id=candidate["experiment_id"],
        project_id=project_id,
        conjecture_id=candidate["conjecture_id"],
        phase=candidate["phase"],
        move=candidate["move"],
        objective=candidate["objective"],
        expected_signal=candidate["expected_signal"],
        modification=candidate["modification"],
        workspace_dir=candidate["workspace_dir"],
        lean_file=candidate["lean_file"],
    )
    db.save_experiment_plan(brief.__dict__)

    charter = db.get_charter(project_id)
    conjecture = db.get_conjecture(brief.conjecture_id)
    recurring = db.recurring_lemmas()
    sensitivity = db.assumption_sensitivity(project_id)
    worker_prompt = build_worker_prompt(charter, conjecture, brief, recurring, sensitivity)
    return {
        "brief": brief,
        "charter": charter,
        "conjecture": conjecture,
        "worker_prompt": worker_prompt,
        "manager_prompt": "",
        "frontier": [],
        "manager_prompt_lint": lint_manager_prompt(""),
        "worker_prompt_lint": lint_worker_prompt(worker_prompt),
    }


def _brief_from_experiment(experiment: Dict[str, object]) -> ExperimentBrief:
    return ExperimentBrief(
        experiment_id=experiment["experiment_id"],
        project_id=experiment["project_id"],
        conjecture_id=experiment["conjecture_id"],
        phase=experiment["phase"],
        move=experiment["move"],
        objective=experiment["objective"],
        expected_signal=experiment["expected_signal"],
        modification=experiment["modification"],
        workspace_dir=experiment["workspace_dir"],
        lean_file=experiment["lean_file"],
    )


def _finalize_result(
    db: Database,
    project_id: str,
    provider_name: str,
    brief: ExperimentBrief,
    result,
    manager_lint,
    worker_lint,
):
    evaluation = score_result(db.get_charter(project_id), result)
    db.update_experiment_result(
        experiment_id=brief.experiment_id,
        provider=provider_name,
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
    return evaluation


def run_one_cycle(db: Database, project_id: str, provider_name: str, workspace_root: str) -> Dict[str, object]:
    prepared = _prepare_cycle(db, project_id, workspace_root)
    brief = prepared["brief"]
    provider = get_provider(provider_name)

    result = provider.run(
        charter=prepared["charter"],
        conjecture=prepared["conjecture"],
        brief=brief,
        worker_prompt=prepared["worker_prompt"],
    )
    evaluation = _finalize_result(
        db=db,
        project_id=project_id,
        provider_name=provider.name,
        brief=brief,
        result=result,
        manager_lint=prepared["manager_prompt_lint"],
        worker_lint=prepared["worker_prompt_lint"],
    )

    return {
        "brief": brief,
        "manager_prompt": prepared["manager_prompt"],
        "worker_prompt": prepared["worker_prompt"],
        "result": result,
        "evaluation": evaluation,
        "frontier": prepared["frontier"],
        "manager_prompt_lint": prepared["manager_prompt_lint"],
        "worker_prompt_lint": prepared["worker_prompt_lint"],
    }


def submit_one_cycle(db: Database, project_id: str, provider_name: str, workspace_root: str) -> Dict[str, object]:
    prepared = _prepare_cycle(db, project_id, workspace_root)
    brief = prepared["brief"]
    provider = get_provider(provider_name)
    if not provider.supports_async:
        return run_one_cycle(db, project_id, provider_name, workspace_root)

    result = provider.submit(
        charter=prepared["charter"],
        conjecture=prepared["conjecture"],
        brief=brief,
        worker_prompt=prepared["worker_prompt"],
    )
    db.update_experiment_result(
        experiment_id=brief.experiment_id,
        provider=provider.name,
        result=result,
        evaluation=None,
    )
    memo = {
        "experiment_id": brief.experiment_id,
        "project_id": project_id,
        "move": brief.move,
        "phase": brief.phase,
        "status": result.status,
        "blocker_type": result.blocker_type,
        "external_id": result.external_id,
        "external_status": result.external_status,
        "manager_prompt_lint_ok": prepared["manager_prompt_lint"].ok,
        "worker_prompt_lint_ok": prepared["worker_prompt_lint"].ok,
    }
    db.add_note(
        project_id=project_id,
        experiment_id=brief.experiment_id,
        note_markdown=json.dumps(memo, indent=2),
        structured=memo,
    )
    return {
        "brief": brief,
        "manager_prompt": prepared["manager_prompt"],
        "worker_prompt": prepared["worker_prompt"],
        "result": result,
        "evaluation": None,
        "frontier": prepared["frontier"],
        "manager_prompt_lint": prepared["manager_prompt_lint"],
        "worker_prompt_lint": prepared["worker_prompt_lint"],
    }


def sync_provider_results(db: Database, project_id: str, provider_name: str, limit: Optional[int] = None) -> List[Dict[str, object]]:
    provider = get_provider(provider_name)
    if not provider.supports_async:
        return []

    synced = []
    active = db.list_active_experiments(project_id, provider=provider.name)
    if limit is not None:
        active = active[:limit]

    for experiment in active:
        brief = _brief_from_experiment(experiment)
        conjecture = db.get_conjecture(brief.conjecture_id)
        charter = db.get_charter(project_id)
        worker_prompt = build_worker_prompt(
            charter,
            conjecture,
            brief,
            db.recurring_lemmas(),
            db.assumption_sensitivity(project_id),
        )
        external_id = experiment.get("external_id") or ""
        if not external_id:
            continue
        result = provider.poll(
            charter=charter,
            conjecture=conjecture,
            brief=brief,
            worker_prompt=worker_prompt,
            external_id=external_id,
        )
        if result.status in {"submitted", "in_progress"}:
            db.update_experiment_result(
                experiment_id=brief.experiment_id,
                provider=provider.name,
                result=result,
                evaluation=None,
            )
            synced.append({"brief": brief, "result": result, "evaluation": None})
            continue

        evaluation = _finalize_result(
            db=db,
            project_id=project_id,
            provider_name=provider.name,
            brief=brief,
            result=result,
            manager_lint=lint_manager_prompt(""),
            worker_lint=lint_worker_prompt(""),
        )
        synced.append({"brief": brief, "result": result, "evaluation": evaluation})
    return synced


def manager_tick(
    db: Database,
    project_id: str,
    provider_name: str,
    workspace_root: str,
    max_active: int,
    max_submit_per_tick: int,
    llm_manager_mode: str,
    report_output: str | Path,
    snapshot_output: str | Path,
) -> Dict[str, object]:
    provider = get_provider(provider_name)
    active_before = db.count_active_experiments(project_id, provider=provider.name)
    synced = sync_provider_results(db, project_id, provider_name, limit=max_active * 4)
    active_now = db.count_active_experiments(project_id, provider=provider.name)
    capacity_remaining = max(0, max_active - active_now)
    requested_submissions = min(capacity_remaining, max_submit_per_tick)

    frontier = generate_frontier(db, project_id, workspace_root)
    policy = choose_candidates_for_submission(
        db=db,
        project_id=project_id,
        frontier=frontier,
        max_count=requested_submissions,
        llm_manager_mode=llm_manager_mode,
    )

    submissions = []
    for decision in policy.chosen[:requested_submissions]:
        candidate = next(
            item for item in frontier if item["experiment_id"] == decision.experiment_id
        )
        prepared = _prepare_cycle_from_candidate(db, project_id, candidate)
        result = provider.submit(
            charter=prepared["charter"],
            conjecture=prepared["conjecture"],
            brief=prepared["brief"],
            worker_prompt=prepared["worker_prompt"],
        ) if provider.supports_async else provider.run(
            charter=prepared["charter"],
            conjecture=prepared["conjecture"],
            brief=prepared["brief"],
            worker_prompt=prepared["worker_prompt"],
        )
        if provider.supports_async:
            db.update_experiment_result(
                experiment_id=prepared["brief"].experiment_id,
                provider=provider.name,
                result=result,
                evaluation=None,
            )
        else:
            _finalize_result(
                db=db,
                project_id=project_id,
                provider_name=provider.name,
                brief=prepared["brief"],
                result=result,
                manager_lint=prepared["manager_prompt_lint"],
                worker_lint=prepared["worker_prompt_lint"],
            )
        submissions.append({
            "experiment_id": prepared["brief"].experiment_id,
            "conjecture_id": prepared["brief"].conjecture_id,
            "move": prepared["brief"].move,
            "phase": prepared["brief"].phase,
            "status": result.status,
            "external_id": result.external_id,
            "external_status": result.external_status,
            "reason": decision.reason,
        })

    active_after = db.count_active_experiments(project_id, provider=provider.name)
    report_output = Path(report_output)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    snapshot_output = Path(snapshot_output)
    snapshot_output.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "project_id": project_id,
        "provider": provider.name,
        "active_jobs": db.list_active_experiments(project_id, provider=provider.name),
        "chosen_submissions": submissions,
        "skipped_candidates": policy.skipped,
        "capacity_summary": {
            "max_active": max_active,
            "max_submit_per_tick": max_submit_per_tick,
            "active_before": active_before,
            "active_after_sync": active_now,
            "active_after_submit": active_after,
            "requested_submissions": requested_submissions,
        },
        "policy_path": policy.policy_path,
        "policy_rationale": policy.rationale,
        "manager_prompt": policy.manager_prompt,
        "raw_response": policy.raw_response,
    }

    manager_run_summary = {
        "jobs_synced": len(synced),
        "jobs_submitted": len(submissions),
        "synced_experiments": [
            {
                "experiment_id": item["brief"].experiment_id,
                "status": item["result"].status,
                "external_status": item["result"].external_status,
            }
            for item in synced
        ],
        "submitted_experiments": submissions,
        "skipped_candidates": policy.skipped,
        "policy_rationale": policy.rationale,
    }
    run_id = db.save_manager_run(
        project_id=project_id,
        provider=provider.name,
        policy_path=policy.policy_path,
        jobs_synced=len(synced),
        jobs_submitted=len(submissions),
        active_before=active_before,
        active_after=active_after,
        report_path=str(report_output),
        snapshot_path=str(snapshot_output),
        summary=manager_run_summary,
    )
    snapshot["manager_run_id"] = run_id
    snapshot_output.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    from research_orchestrator.reporter import write_report
    write_report(db, project_id, report_output)

    return {
        "run_id": run_id,
        "policy_path": policy.policy_path,
        "jobs_synced": len(synced),
        "jobs_submitted": len(submissions),
        "active_before": active_before,
        "active_after": active_after,
        "report_output": str(report_output),
        "snapshot_output": str(snapshot_output),
        "submitted": submissions,
        "synced": [
            {
                "experiment_id": item["brief"].experiment_id,
                "status": item["result"].status,
                "external_status": item["result"].external_status,
            }
            for item in synced
        ],
    }
