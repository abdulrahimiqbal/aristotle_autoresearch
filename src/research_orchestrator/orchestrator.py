from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from research_orchestrator.db import Database
from research_orchestrator.evaluator import score_result
from research_orchestrator.manager import choose_next_experiment, generate_frontier
from research_orchestrator.manager import choose_candidates_for_submission
from research_orchestrator.manager import build_research_directive, materialize_from_directive
from research_orchestrator.prompt_linter import lint_manager_prompt, lint_worker_prompt
from research_orchestrator.prompts import build_worker_prompt
from research_orchestrator.provider_registry import get_provider
from research_orchestrator.result_ingestion import (
    build_verification_signals,
    prepare_ingested_result,
    save_proved_lemmas_to_ledger,
    extract_obligations_from_result,
)
from research_orchestrator.live_projections import refresh_live_projections
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
        route_id="",
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
        route_id="",
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


def _manager_paused(db: Database, project_id: str) -> bool:
    row = db.conn.execute(
        """
        SELECT command_type FROM operator_commands
        WHERE project_id = ?
          AND command_type IN ('pause-manager', 'resume-manager')
          AND status IN ('pending', 'applied')
        ORDER BY issued_at DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    if row is None:
        return False
    return row["command_type"] == "pause-manager"


def _apply_operator_commands(db: Database, project_id: str, run_id: str) -> Dict[str, Any]:
    commands = db.list_operator_commands(project_id, status="pending")
    applied: list[dict[str, Any]] = []
    for command in commands:
        details: dict[str, Any] = {"command_id": command["command_id"]}
        status = "applied"
        if command["command_type"] == "pause-manager":
            details["paused"] = True
        elif command["command_type"] == "resume-manager":
            details["paused"] = False
        elif command["command_type"] == "retry-experiment":
            if command.get("target_id"):
                db.reset_experiment_for_retry(command["target_id"])
        elif command["command_type"] == "kill-job":
            if command.get("target_id"):
                db.mark_experiment_killed(command["target_id"])
        else:
            status = "rejected"
            details["reason"] = "unknown command_type"
        db.mark_operator_command_applied(command["command_id"], status=status, details=details)
        db.emit_manager_event(
            project_id=project_id,
            run_id=run_id,
            event_type="operator.command.applied",
            source_component="operator",
            experiment_id=command.get("target_id"),
            payload={
                "command_id": command["command_id"],
                "command_type": command["command_type"],
                "status": status,
                "details": details,
            },
        )
        applied.append(details)
    return {"manager_paused": _manager_paused(db, project_id), "applied": applied}


def _finalize_result(
    db: Database,
    project_id: str,
    provider_name: str,
    brief: ExperimentBrief,
    result,
    manager_lint,
    worker_lint,
    run_id: str | None = None,
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
    # Save proved lemmas to the cumulative proof ledger
    save_proved_lemmas_to_ledger(
        db=db,
        project_id=project_id,
        conjecture_id=brief.conjecture_id,
        experiment_id=brief.experiment_id,
        result=result,
    )
    # Extract proof obligations from incomplete results
    extract_obligations_from_result(
        db=db,
        project_id=project_id,
        conjecture_id=brief.conjecture_id,
        experiment_id=brief.experiment_id,
        result=result,
    )
    db.update_experiment_result(
        experiment_id=brief.experiment_id,
        provider=provider_name,
        result=result,
        evaluation=evaluation.__dict__,
    )
    resolved_run_id = run_id or f"ingestion:{brief.experiment_id}"
    db.emit_manager_event(
        project_id=project_id,
        run_id=resolved_run_id,
        event_type="result.ingested",
        source_component="result_ingestion",
        experiment_id=brief.experiment_id,
        payload={
            "status": result.status,
            "proof_outcome": result.proof_outcome,
            "blocker_type": result.blocker_type,
            "new_signal_count": result.new_signal_count,
            "reused_signal_count": result.reused_signal_count,
        },
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
            run_id=resolved_run_id,
        )
    incident_type = result.metadata.get("incident_type", "")
    if incident_type:
        db.create_incident(
            project_id=project_id,
            experiment_id=brief.experiment_id,
            incident_type=incident_type,
            detail=result.metadata.get("incident_detail", result.notes or result.signal_summary),
            severity=result.metadata.get("incident_severity", "warning"),
            run_id=resolved_run_id,
        )
    for issue in prepared.validation_issues:
        db.create_incident(
            project_id=project_id,
            experiment_id=brief.experiment_id,
            incident_type=f"verification_validation_{issue.issue_type}",
            detail=issue.detail,
            severity=issue.severity,
            run_id=resolved_run_id,
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
    refresh_live_projections(db, project_id)
    return evaluation


def run_one_cycle(db: Database, project_id: str, provider_name: str, workspace_root: str) -> Dict[str, object]:
    prepared = _prepare_cycle(db, project_id, workspace_root)
    brief = prepared["brief"]
    provider = get_provider(provider_name)
    run_id = f"cycle:{brief.experiment_id}"

    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="cycle.started",
        source_component="single_cycle",
        experiment_id=brief.experiment_id,
        payload={"move": brief.move, "phase": brief.phase, "provider": provider.name},
    )

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
        run_id=run_id,
    )

    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="cycle.completed",
        source_component="single_cycle",
        experiment_id=brief.experiment_id,
        payload={
            "status": result.status,
            "proof_outcome": result.proof_outcome,
            "blocker_type": result.blocker_type,
            "new_signal_count": getattr(result, "new_signal_count", 0),
            "reused_signal_count": getattr(result, "reused_signal_count", 0),
        },
    )
    refresh_live_projections(db, project_id)

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

    run_id = f"cycle:{brief.experiment_id}"
    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="cycle.submit.started",
        source_component="single_cycle",
        experiment_id=brief.experiment_id,
        payload={"move": brief.move, "phase": brief.phase, "provider": provider.name},
    )

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
    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="candidate.submitted",
        source_component="single_cycle",
        experiment_id=brief.experiment_id,
        payload={
            "move": brief.move,
            "status": result.status,
            "external_id": result.external_id,
            "external_status": result.external_status,
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
    refresh_live_projections(db, project_id)
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


def sync_provider_results(
    db: Database,
    project_id: str,
    provider_name: str,
    limit: Optional[int] = None,
    run_id: str | None = None,
) -> List[Dict[str, object]]:
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
            db.emit_manager_event(
                project_id=project_id,
                run_id=run_id or f"sync:{project_id}",
                event_type="job.synced",
                source_component="provider_sync",
                experiment_id=brief.experiment_id,
                payload={
                    "status": result.status,
                    "external_status": result.external_status,
                },
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
            run_id=run_id,
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
    """Execute a manager tick using directive-based decision making.

    Simplified flow:
    1. Build directive from current state
    2. Materialize experiments from directive
    3. Submit them
    """
    import uuid

    run_id = str(uuid.uuid4())
    provider = get_provider(provider_name)
    spec = db.get_campaign_spec(project_id)
    runtime_policy = spec.runtime_policy if spec is not None else None
    budget_policy = spec.budget_policy if spec is not None else None

    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="manager.tick.started",
        source_component="manager",
        payload={
            "provider": provider.name,
            "max_active": max_active,
            "max_submit_per_tick": max_submit_per_tick,
        },
    )

    # Housekeeping: expire stale experiments, sync results, escalate incidents
    expired_stale = db.expire_stale_active_experiments(
        project_id,
        max_age_seconds=runtime_policy.stale_run_timeout_seconds if runtime_policy is not None else getattr(provider, "STALE_PROGRESS_TIMEOUT_SECONDS", 6 * 3600),
    )
    active_before = db.count_active_experiments(project_id, provider=provider.name)
    synced = sync_provider_results(db, project_id, provider_name, limit=max_active * 4, run_id=run_id)
    operational_status = db.escalate_operational_incidents(
        project_id,
        repeated_failure_threshold=runtime_policy.repeated_failure_incident_threshold if runtime_policy is not None else 3,
        repeated_no_signal_threshold=runtime_policy.repeated_no_signal_incident_threshold if runtime_policy is not None else 3,
        stale_run_timeout_seconds=runtime_policy.stale_run_timeout_seconds if runtime_policy is not None else 6 * 3600,
        stuck_run_timeout_seconds=runtime_policy.stuck_run_timeout_seconds if runtime_policy is not None else 2 * 3600,
        max_attempts_per_experiment=budget_policy.max_attempts_per_experiment if budget_policy is not None else 6,
    )
    command_state = _apply_operator_commands(db, project_id, run_id)

    active_now = db.count_active_experiments(project_id, provider=provider.name)
    capacity_remaining = max(0, max_active - active_now)
    requested_submissions = min(capacity_remaining, max_submit_per_tick)

    # === DIRECTIVE-BASED DECISION MAKING ===
    # Step 1: Generate frontier and build directive from current state
    frontier = generate_frontier(db, project_id, workspace_root)

    # Build runtime context for directive
    from research_orchestrator.manager import _runtime_context
    runtime = _runtime_context(db, project_id)

    # Build the research directive
    directive = build_research_directive(db, project_id, frontier, runtime)

    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="directive.built",
        source_component="manager",
        payload={
            "directive_id": directive.directive_id,
            "strategy": directive.strategy,
            "focus_conjectures": directive.focus_conjecture_ids,
            "priority_moves": directive.priority_moves,
            "rationale": directive.rationale,
            "frontier_count": len(frontier),
        },
    )

    # Step 2: Materialize experiments from directive
    directive_candidates = materialize_from_directive(db, directive, workspace_root)

    # Merge directive candidates with frontier for maximum coverage
    combined_frontier = directive_candidates + [f for f in frontier if f["experiment_id"] not in {c["experiment_id"] for c in directive_candidates}]

    db.emit_manager_event(
        project_id=project_id,
        run_id=run_id,
        event_type="experiments.materialized",
        source_component="manager",
        payload={
            "directive_candidates": len(directive_candidates),
            "combined_frontier": len(combined_frontier),
        },
    )

    # Step 3: Use policy to select candidates for submission
    policy = choose_candidates_for_submission(
        db=db,
        project_id=project_id,
        frontier=combined_frontier,
        max_count=requested_submissions,
        llm_manager_mode=llm_manager_mode,
        workspace_root=workspace_root,  # Enable directive-based generation as fallback
    )

    # Apply pause policies
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
    if command_state["manager_paused"]:
        policy.chosen = []
        policy.skipped.append(
            {
                "experiment_id": "",
                "conjecture_id": "",
                "reason": "operator paused manager submissions",
            }
        )

    # Emit policy events
    submissions = []
    for audit in policy.candidate_audits[:20]:
        # Build a proper selection rationale from score breakdown
        score_breakdown = audit.get("score_breakdown", {})
        bonuses = score_breakdown.get("bonuses", {})
        penalties = score_breakdown.get("penalties", {})
        score = score_breakdown.get("score", 0)
        selected = bool(audit.get("selected"))

        # Create strategic rationale
        rationale_parts = []
        if selected:
            rationale_parts.append("Selected by manager policy")
        else:
            rationale_parts.append("Scored but not selected")

        # Add key scoring factors
        key_factors = []
        if bonuses.get("discovery_priority", 0) > 0:
            key_factors.append(f"discovery_priority={bonuses['discovery_priority']:.2f}")
        if bonuses.get("signal_support", 0) > 0:
            key_factors.append(f"signal_support={bonuses['signal_support']:.2f}")
        if bonuses.get("transfer_opportunity", 0) > 0:
            key_factors.append(f"transfer_score={bonuses['transfer_opportunity']:.2f}")
        if bonuses.get("reuse_potential", 0) > 0:
            key_factors.append(f"reuse_score={bonuses['reuse_potential']:.2f}")
        if bonuses.get("semantic_novelty", 0) > 0:
            key_factors.append(f"novelty_score={bonuses['semantic_novelty']:.2f}")

        if key_factors:
            rationale_parts.append("Key factors: " + ", ".join(key_factors))

        # Add rejection reason if not selected
        selection_reason = audit.get("selection_reason", "")
        if not selected and selection_reason:
            rationale_parts.append(f"Reason: {selection_reason}")

        rationale = "; ".join(rationale_parts)

        db.emit_manager_event(
            project_id=project_id,
            run_id=run_id,
            event_type="candidate.scored",
            source_component="policy",
            experiment_id=audit.get("experiment_id"),
            payload={
                "experiment_id": audit.get("experiment_id"),
                "score_breakdown": score_breakdown,
                "selected": selected,
                "policy_score": score,
                "rationale": rationale,
                "selection_reason": selection_reason if not selected else "chosen by policy",
            },
        )
    for skipped in policy.skipped[:20]:
        db.emit_manager_event(
            project_id=project_id,
            run_id=run_id,
            event_type="candidate.rejected",
            source_component="policy",
            experiment_id=skipped.get("experiment_id"),
            payload={
                "experiment_id": skipped.get("experiment_id"),
                "reason": skipped.get("reason", ""),
            },
        )

    # Submit chosen experiments
    for decision in policy.chosen[:requested_submissions]:
        candidate = next(
            item for item in combined_frontier if item["experiment_id"] == decision.experiment_id
        )
        db.emit_manager_event(
            project_id=project_id,
            run_id=run_id,
            event_type="candidate.selected",
            source_component="policy",
            experiment_id=decision.experiment_id,
            payload={
                "experiment_id": decision.experiment_id,
                "reason": decision.reason,
            },
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
                    run_id=run_id,
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
                run_id=run_id,
            )
        if not provider.supports_async or result.status in {"submitted", "in_progress"}:
            db.emit_manager_event(
                project_id=project_id,
                run_id=run_id,
                event_type="job.submitted",
                source_component="provider",
                experiment_id=prepared["brief"].experiment_id,
                payload={
                    "status": result.status,
                    "external_id": result.external_id,
                    "external_status": result.external_status,
                },
            )
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
        "manager_prompt": policy.manager_prompt,
        "raw_response": policy.raw_response,
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
        run_id=run_id,
    )
    db.save_manager_candidate_audits(run_id=run_id, project_id=project_id, rows=policy.candidate_audits)
    db.save_campaign_health_snapshot(run_id=run_id, project_id=project_id, health=health)
    snapshot["manager_run_id"] = run_id
    snapshot_output.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    from research_orchestrator.reporter import write_report
    write_report(db, project_id, report_output)
    refresh_live_projections(db, project_id, run_id=run_id)

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
