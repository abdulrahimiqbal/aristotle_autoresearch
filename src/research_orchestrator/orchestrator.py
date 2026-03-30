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
from research_orchestrator.result_ingestion import build_verification_signals, prepare_ingested_result
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
        move_family=candidate.get("move_family", candidate["move"]),
        theorem_family_id=candidate.get("theorem_family_id", ""),
        move_title=candidate.get("move_title", ""),
        rationale=candidate.get("rationale", ""),
        candidate_metadata=candidate.get("candidate_metadata", {}),
        discovery_question_id=candidate.get("discovery_question_id", ""),
        discovery_question=candidate.get("discovery_question", ""),
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
        move_family=experiment.get("move_family", experiment["move"]),
        theorem_family_id=experiment.get("theorem_family_id", ""),
        move_title=experiment.get("move_title", ""),
        rationale=experiment.get("rationale", ""),
        candidate_metadata=experiment.get("candidate_metadata", {}),
        discovery_question_id=experiment.get("discovery_question_id", "") or "",
        discovery_question="",
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
    result.metadata = dict(result.metadata)
    result.metadata.setdefault("provider_name", provider_name)
    prepared = prepare_ingested_result(result)
    result = prepared.provider_result
    semantic_summary = db.record_result_ingestion(
        project_id=project_id,
        conjecture_id=brief.conjecture_id,
        experiment_id=brief.experiment_id,
        proof_outcome=result.proof_outcome,
        blocker_type=result.blocker_type,
        unresolved_goals=result.unresolved_goals,
        artifact_inventory=result.artifact_inventory,
        signal_summary=result.signal_summary,
        proof_trace_fragments=result.proof_trace_fragments,
        counterexample_witnesses=result.counterexample_witnesses,
        discovery_question_id=brief.discovery_question_id,
        verification_signals=build_verification_signals(
            project_id=project_id,
            conjecture_id=brief.conjecture_id,
            experiment_id=brief.experiment_id,
            result=result,
        ),
        verification_record=prepared.verification_record,
        semantic_summary=prepared.semantic_summary,
        theorem_family=db.get_conjecture(brief.conjecture_id).domain,
    )
    result.semantic_summary = semantic_summary
    result.new_signal_count = semantic_summary.new_exact_count
    result.reused_signal_count = semantic_summary.exact_reuse_count + semantic_summary.canonical_reuse_count
    evaluation = score_result(
        db.get_charter(project_id),
        result,
        verification_record=prepared.verification_record,
        semantic_summary=semantic_summary,
    )
    db.save_lemma_occurrences(
        experiment_id=brief.experiment_id,
        conjecture_id=brief.conjecture_id,
        generated=result.generated_lemmas,
        proved=result.proved_lemmas,
        candidate=result.candidate_lemmas,
    )
    db.update_experiment_result(
        experiment_id=brief.experiment_id,
        provider=provider_name,
        result=result,
        evaluation=evaluation.__dict__,
    )
    db.add_audit_event(
        project_id=project_id,
        experiment_id=brief.experiment_id,
        event_type="experiment_finalized",
        detail={
            "status": result.status,
            "proof_outcome": result.proof_outcome,
            "blocker_type": result.blocker_type,
            "discovery_question_id": brief.discovery_question_id,
        },
    )
    if result.blocker_type in {"dns_failure", "network_unavailable", "malformed"}:
        db.create_incident(
            project_id=project_id,
            experiment_id=brief.experiment_id,
            incident_type=result.blocker_type,
            detail=result.notes or result.signal_summary,
            severity="error" if result.blocker_type != "malformed" else "warning",
        )
    incident_type = result.metadata.get("incident_type", "")
    if incident_type:
        db.create_incident(
            project_id=project_id,
            experiment_id=brief.experiment_id,
            incident_type=incident_type,
            detail=result.metadata.get("incident_detail", result.notes or result.signal_summary),
            severity=result.metadata.get("incident_severity", "warning"),
        )
    for issue in prepared.validation_issues:
        db.create_incident(
            project_id=project_id,
            experiment_id=brief.experiment_id,
            incident_type=f"verification_validation_{issue.issue_type}",
            detail=issue.detail,
            severity=issue.severity,
        )

    if brief.move == "perturb_assumption":
        assumption = brief.modification.get("assumption")
        if assumption:
            if result.proof_outcome not in {"infra_failure", "auth_failure", "malformed"}:
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
        "proof_outcome": result.proof_outcome,
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
    result.metadata = dict(result.metadata)
    result.metadata.setdefault("provider_name", provider.name)
    result = prepare_ingested_result(result).provider_result
    db.update_experiment_result(
        experiment_id=brief.experiment_id,
        provider=provider.name,
        result=result,
        evaluation=None,
    )
    db.add_audit_event(
        project_id=project_id,
        experiment_id=brief.experiment_id,
        event_type="experiment_submitted",
        detail={
            "status": result.status,
            "external_id": result.external_id,
            "discovery_question_id": brief.discovery_question_id,
        },
    )
    memo = {
        "experiment_id": brief.experiment_id,
        "project_id": project_id,
        "move": brief.move,
        "phase": brief.phase,
        "status": result.status,
        "proof_outcome": result.proof_outcome,
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
            submitted_at=experiment.get("submitted_at", "") or "",
        )
        result.metadata = dict(result.metadata)
        result.metadata.setdefault("provider_name", provider.name)
        result = prepare_ingested_result(result).provider_result
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


def backfill_provider_results(db: Database, project_id: str, provider_name: str, limit: Optional[int] = None) -> List[Dict[str, object]]:
    provider = get_provider(provider_name)
    if not provider.supports_async:
        return []

    backfilled = []
    candidates = db.list_backfillable_experiments(project_id, provider=provider.name, limit=limit)
    for experiment in candidates:
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
            submitted_at=experiment.get("submitted_at", "") or "",
        )
        result.metadata = dict(result.metadata)
        result.metadata.setdefault("provider_name", provider.name)
        result = prepare_ingested_result(result).provider_result
        evaluation = _finalize_result(
            db=db,
            project_id=project_id,
            provider_name=provider.name,
            brief=brief,
            result=result,
            manager_lint=lint_manager_prompt(""),
            worker_lint=lint_worker_prompt(""),
        )
        backfilled.append({"brief": brief, "result": result, "evaluation": evaluation})
    return backfilled


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
    spec = db.get_campaign_spec(project_id)
    runtime_policy = spec.runtime_policy if spec is not None else None
    budget_policy = spec.budget_policy if spec is not None else None
    expired_stale = db.expire_stale_active_experiments(
        project_id,
        max_age_seconds=runtime_policy.stale_run_timeout_seconds if runtime_policy is not None else getattr(provider, "STALE_PROGRESS_TIMEOUT_SECONDS", 6 * 3600),
    )
    active_before = db.count_active_experiments(project_id, provider=provider.name)
    synced = sync_provider_results(db, project_id, provider_name, limit=max_active * 4)
    operational_status = db.escalate_operational_incidents(
        project_id,
        repeated_failure_threshold=runtime_policy.repeated_failure_incident_threshold if runtime_policy is not None else 3,
        repeated_no_signal_threshold=runtime_policy.repeated_no_signal_incident_threshold if runtime_policy is not None else 3,
        stale_run_timeout_seconds=runtime_policy.stale_run_timeout_seconds if runtime_policy is not None else 6 * 3600,
        stuck_run_timeout_seconds=runtime_policy.stuck_run_timeout_seconds if runtime_policy is not None else 2 * 3600,
        max_attempts_per_experiment=budget_policy.max_attempts_per_experiment if budget_policy is not None else 6,
    )
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
    if runtime_policy is not None and runtime_policy.pause_on_incident:
        open_errors = [item for item in db.list_incidents(project_id, status="open") if item["severity"] == "error"]
        if open_errors:
            policy.chosen = []
            policy.skipped.append(
                {
                    "experiment_id": "",
                    "conjecture_id": "",
                    "reason": "runtime policy paused submissions because open error incidents exist",
                }
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
        result.metadata = dict(result.metadata)
        result.metadata.setdefault("provider_name", provider.name)
        result = prepare_ingested_result(result).provider_result
        if provider.supports_async:
            if result.status in {"submitted", "in_progress"}:
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
        if not provider.supports_async or result.status in {"submitted", "in_progress"}:
            submissions.append({
                "experiment_id": prepared["brief"].experiment_id,
                "conjecture_id": prepared["brief"].conjecture_id,
                "move": prepared["brief"].move,
                "move_family": prepared["brief"].move_family or prepared["brief"].move,
                "theorem_family_id": prepared["brief"].theorem_family_id,
                "phase": prepared["brief"].phase,
                "status": result.status,
                "external_id": result.external_id,
                "external_status": result.external_status,
                "reason": decision.reason,
            })
        else:
            policy.skipped.append(
                {
                    "experiment_id": prepared["brief"].experiment_id,
                    "conjecture_id": prepared["brief"].conjecture_id,
                    "reason": f"provider submit failed before remote submission: status={result.status}",
                }
            )

    active_after = db.count_active_experiments(project_id, provider=provider.name)
    report_output = Path(report_output)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    snapshot_output = Path(snapshot_output)
    snapshot_output.parent.mkdir(parents=True, exist_ok=True)
    health = db.campaign_health(project_id, frontier=frontier)
    snapshot = {
        "project_id": project_id,
        "provider": provider.name,
        "active_jobs": db.list_active_experiments(project_id, provider=provider.name),
        "chosen_submissions": submissions,
        "skipped_candidates": policy.skipped,
        "candidate_audits": policy.candidate_audits,
        "operational_status": operational_status,
        "campaign_health": health,
        "recurring_structures": {
            "lemmas": db.recurring_lemmas()[:10],
            "subgoals": db.recurring_subgoals(project_id)[:10],
            "proof_traces": db.recurring_proof_traces(project_id)[:10],
            "no_signal_branches": db.no_signal_branches(project_id),
        },
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
        "signal_progress": {
            "latest_completed": [
                {
                    "experiment_id": item["brief"].experiment_id,
                    "new_signal_count": item["result"].new_signal_count,
                    "reused_signal_count": item["result"].reused_signal_count,
                    "proof_outcome": item["result"].proof_outcome,
                }
                for item in synced
            ]
        },
        "expired_stale_active_experiments": expired_stale,
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
        "recurring_structures": snapshot["recurring_structures"],
        "signal_progress": snapshot["signal_progress"],
        "expired_stale_active_experiments": expired_stale,
        "candidate_audits": policy.candidate_audits,
        "operational_status": operational_status,
        "campaign_health": health,
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
    db.save_manager_candidate_audits(run_id=run_id, project_id=project_id, rows=policy.candidate_audits)
    db.save_campaign_health_snapshot(run_id=run_id, project_id=project_id, health=health)
    snapshot["manager_run_id"] = run_id
    snapshot_output.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    from research_orchestrator.reporter import write_report
    write_report(db, project_id, report_output)

    return {
        "run_id": run_id,
        "policy_path": policy.policy_path,
        "jobs_synced": len(synced),
        "jobs_submitted": len(submissions),
        "expired_stale_active_experiments": expired_stale,
        "operational_status": operational_status,
        "active_before": active_before,
        "active_after": active_after,
        "report_output": str(report_output),
        "snapshot_output": str(snapshot_output),
        "campaign_health": health,
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
